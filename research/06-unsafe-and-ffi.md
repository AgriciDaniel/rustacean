# Unsafe Rust & FFI — Soundness

*Current as of June 2026. Targets stable Rust 1.85+ and edition 2024.*

`unsafe` is not an escape hatch from Rust's rules — it is a way to assert to the
compiler that *you* are upholding invariants the type system cannot check. Getting
this wrong does not produce a runtime error; it produces **undefined behavior (UB)**,
which can mean miscompilation, silent corruption, or a vulnerability that only appears
after the next compiler upgrade. This report covers the unsafe contract, the precise UB
categories, provenance and aliasing, `MaybeUninit`, C FFI, and the tooling (Miri) that
makes any of this tractable — with a *good practice / mistake to avoid* pairing on each
major point.

## What `unsafe` Actually Means

`unsafe` does exactly two things: it lets you perform five "unsafe superpowers"
(dereference a raw pointer, call an `unsafe fn`/FFI function, access/modify a `static mut`,
implement an `unsafe trait`, access `union` fields), and it lets you *promise* the compiler
that you have met the obligations those operations require [1][2]. It does **not** turn off
the borrow checker, type checking, or any other static check [2]. The mental model from the
Rustonomicon is that *safe* code can never cause UB no matter what it does; *unsafe* code can,
and so the burden of proof shifts to the human [3].

The central design promise is that **all safe code is sound**: a function is *safe* if it lacks
`unsafe`, and *sound* if no combination of safe callers can trigger UB through it [4][1]. A
subtle but load-bearing point (Matsakis, via the wider literature): soundness is *self-referential* —
whether your `unsafe` block is sound depends on what other code is allowed to assume [4]. This is
why a safe wrapper around `setjmp`/`longjmp` that looks sound in isolation becomes unsound the
moment threads exist [4].

- **Good practice:** Treat every `unsafe` block as a *contract with the rest of the program*.
  Encapsulate it behind a safe API whose public signature cannot be misused to cause UB.
- **Mistake to avoid:** Marking a function `pub unsafe fn` and assuming that absolves you.
  If a *safe* function you expose can be driven to UB with safe inputs, the function is
  unsound regardless of how much `unsafe` is inside [1][4].

## Soundness vs. Safety — the distinction that matters

"Safe" is a syntactic property (no `unsafe` keyword). "Sound" is a semantic property (cannot
cause UB) [5][1]. The whole point of the language is to keep these aligned: safe ⇒ sound. A
*soundness bug* is a safe API that can trigger UB — these are treated as serious defects in the
ecosystem and routinely earn RUSTSEC advisories even when no one has exploited them yet.

- **Good practice:** When auditing, ask "can a malicious *safe* caller break this?" not "is
  there `unsafe` here?" Memory-safety vulnerabilities written entirely in safe Rust are possible
  precisely when some `unsafe` elsewhere exposed an unsound safe API [5].
- **Mistake to avoid:** Conflating "compiles without `unsafe`" with "correct." Safe code calling
  an unsound dependency inherits the UB.

## The Categories of Undefined Behavior

The Rust Reference enumerates UB explicitly [6]. Memorize these — they are the entire attack
surface:

1. **Data races** — always UB [6].
2. **Dangling or misaligned access** — loading/storing through a pointer whose bytes aren't all in
   one live allocation, or that isn't aligned for its type (`*const S` where `S` aligns to 8 must
   be 8-aligned) [6].
3. **Out-of-bounds place projection** — field/index projection violating in-bounds pointer
   arithmetic [6].
4. **Breaking aliasing rules** — `&T` must not be mutated while live (except inside `UnsafeCell`),
   and `&mut T` must be the *only* path that reads or writes its memory while live [6].
5. **Mutating immutable data** — writing through a shared reference or to const-promoted/`static`
   bytes (outside `UnsafeCell`) [6].
6. **Producing an invalid value** — on *any* read, write, argument pass, or return [6]:
   - `bool` not exactly `0`/`1`; `char` a surrogate or `> char::MAX`; `!` ever existing; a `fn`
     pointer that is null [6].
   - An integer, float, or raw pointer read from **uninitialized** memory [6].
   - An `enum` with an invalid discriminant [6].
   - A reference or `Box<T>` that is null, unaligned, dangling, or points to an invalid value [6].
   - A `NonNull`/`NonZero` outside its custom valid range [6].
7. **Wrong ABI / illegal unwind** — calling with the wrong call ABI, or unwinding past a frame that
   forbids it (e.g. a `"C-unwind"` fn transmuted to `"C"`) [6].
8. **UB via intrinsics, unsupported `target_feature`, or bad inline asm** [6].
9. **Violating runtime assumptions** — e.g. `longjmp` skipping destructors of a live frame [6].

A defining feature of Rust UB is that it is **not** "it does something weird" — UB is a *contract
violation that the optimizer is allowed to assume never happens*, so the consequences are unbounded
and can be non-local.

- **Good practice:** When writing `unsafe`, walk this list and write a `// SAFETY:` comment naming
  which obligations you uphold and how.
- **Mistake to avoid:** Assuming a value is "probably fine." A `bool` that is `2` is UB the instant
  it is *produced* — you don't even have to branch on it [6].

## Pointer Aliasing, Provenance, and Strict Provenance

Rust's optimizer relies on aliasing guarantees: if two pointers have different *provenance*, they
cannot alias, which licenses aggressive reordering and caching [7][8]. **Provenance** is the
invisible "where did this pointer come from / what allocation may it touch" metadata attached to
every pointer; a pointer with the right address but wrong provenance is UB to dereference [9][8].

Since **Rust 1.84 (Jan 2025)** the *strict provenance* APIs are stable: `ptr::without_provenance`,
`addr()`, `with_addr()`, `map_addr()`, and `expose_provenance`/`with_exposed_provenance` for the
deliberately-lossy integer-cast path [7][10]. These let you store tag bits in the low bits of an
aligned pointer *without* casting through `usize`, keeping provenance intact [10][7]. RFC 3559
formally adopted provenance into Rust's model [11].

```rust
// Good: keep provenance, only change the address bits.
let tagged = ptr.map_addr(|a| a | 1);          // set a tag bit
let clean  = tagged.map_addr(|a| a & !1);      // strip it, provenance preserved

// Mistake: round-trip through usize loses/launders provenance.
let bad = (ptr as usize | 1) as *mut T;        // address right, provenance wrong → UB-prone
```

- **Good practice:** Use `map_addr`/`with_addr` for pointer tagging and alignment math; reach for
  `expose_provenance`/`with_exposed_provenance` *only* when you genuinely need int↔ptr round-trips,
  and document why [7][10].
- **Mistake to avoid:** `ptr as usize ... as *mut T` casts that "work" today. They are exactly what
  defeats alias analysis and what Miri flags under strict-provenance checking [9][8].
- **Mistake to avoid:** Creating two `&mut` to the same location, even transiently. That violates
  rule 4 above and is caught by Miri's borrow models [12][6].

## MaybeUninit — the only sound way to touch uninitialized memory

`MaybeUninit<T>` is the type with **no validity invariant**: *any* byte pattern, initialized or
not, is a valid `MaybeUninit<T>` [13]. This is what makes it the correct tool for delayed/partial
initialization, FFI out-parameters, and uninitialized buffers. The rule of thumb: *never name
uninitialized memory with anything except a raw pointer or a `MaybeUninit` wrapper* [14].

The legacy `mem::uninitialized()` / `mem::zeroed::<T>()` for non-zeroable `T` are **instant UB** —
they produce an invalid value of `T` the moment they return, before you touch anything [15][14].
They are deprecated; `MaybeUninit` replaces them.

```rust
use std::mem::MaybeUninit;

let mut buf: MaybeUninit<[u8; 1024]> = MaybeUninit::uninit();
let ptr = buf.as_mut_ptr() as *mut u8;
// ... fill `len` bytes via raw pointer / FFI ...
// SAFETY: first `len` bytes were just initialized by the call above.
let init: &[u8] = unsafe { std::slice::from_raw_parts(ptr, len) };
```

- **Good practice:** Initialize through the raw `*mut T` (raw pointers don't assert validity), and
  call `assume_init()` **only** after *every* byte is initialized on *every* path [13][14].
- **Mistake to avoid:** Calling `assume_init()` where an early return or error path can skip the
  initialization — that reads garbage and is UB [15]. Also: never build a `&T` or `&mut T` to
  still-uninitialized memory; the reference's validity invariant is violated immediately [14][6].
- **Mistake to avoid:** `transmute`-ing a C `int` into a Rust `enum` whose discriminants don't
  cover the full integer range — any out-of-range value is UB [15][6].

## FFI with C — the boundary is a trust boundary

C is the canonical reason `unsafe` exists, and the FFI boundary is where most real-world UB hides.
The Rustonomicon's FFI chapter and the ecosystem converge on a few hard rules [16][17]:

- **Unwinding across FFI is UB.** A Rust panic propagating into a plain `extern "C"` frame, or a C++
  exception entering Rust, is undefined [16][17]. Use `extern "C-unwind"` only when you *intend*
  unwinding to cross; otherwise wrap Rust callbacks in `std::panic::catch_unwind` and convert panics
  to error codes [17].
- **Everything from C is suspect.** Validate pointers, lengths, and lifetimes before trusting them;
  everything sent to C must be in C-ABI form [17].
- **Model thread-safety honestly.** If the C library isn't thread-safe, mark your wrapper `!Send`/`!Sync`
  so safe Rust can't smuggle it across threads [17].

```rust
extern "C" fn rust_callback(x: i32) -> i32 {
    // SAFETY net: never let a panic unwind into C.
    std::panic::catch_unwind(|| do_work(x)).unwrap_or(-1)
}
```

- **Good practice:** Generate declarations with `bindgen` rather than hand-writing them (eliminates
  type/ABI mismatches), then hand-write a thin safe wrapper with `Drop` for cleanup and proper
  `CStr`/UTF-8 handling [16][17]. Keep the `unsafe` surface tiny and test it under Miri,
  Valgrind/ASan [17][18].
- **Mistake to avoid:** Returning C++ `std::string`/`std::vector` *by value* across FFI — not
  FFI-safe; bindgen itself warns about this [16]. Pass opaque pointers and C-ABI types only.
- **Mistake to avoid:** Assuming a C function won't hold onto a pointer you passed it (use-after-free),
  won't cast away `const` to mutate your data, or won't bypass your `Mutex` — the compiler can't see
  any of it [17].

## Miri — your single most effective UB detector

Miri is an interpreter for Rust's MIR that **executes** your tests and watches for UB as it runs;
it is, per the POPL 2026 paper, the only freely available tool that finds *all de-facto UB in
deterministic Rust programs* [19][20]. It detects misaligned accesses, invalid values, aliasing
violations (via **Stacked Borrows** and the newer **Tree Borrows** models), data races, and
provenance/int-to-pointer-cast violations — pinpointing both accesses in a race and showing
allocation/deallocation sites [12][20][21]. It ships with the nightly toolchain and needs no
annotations [19].

```sh
rustup +nightly component add miri
cargo +nightly miri test
```

In a 100,000+ library evaluation Miri ran over 70% of combined test suites and has caught dozens of
real bugs, including in the standard library, where `cargo miri test` is part of CI [19][20].

- **Good practice:** Add `cargo miri test` to CI for any crate with `unsafe`; run with
  `MIRIFLAGS=-Zmiri-tree-borrows` to catch the cases the default model misses, and
  `-Zmiri-many-seeds` for concurrency [12][18][21].
- **Mistake to avoid:** Treating "Miri is green" as "sound." Miri only checks the paths your tests
  *exercise*, runs deterministically (so non-deterministic bugs need extra flags), and tracks
  current compiler behavior rather than a frozen spec [20]. Pair it with ASan/Valgrind for FFI and
  with broad test coverage [18].

## When Unsafe Is Justified — and How to Write It

Legitimate reasons for `unsafe` are narrow and well-known: FFI, performance-critical code with
*benchmark-proven* gains, building safe abstractions over raw pointers (e.g. data structures), and
talking to hardware/OS primitives [22][2]. Everything else should be safe Rust.

- **Good practice:** Minimize and isolate. Keep `unsafe` blocks as small as possible, confine them
  to a dedicated module, wrap them in a safe API, and attach a `// SAFETY:` comment to *every* block
  and every `unsafe fn` that names the invariants relied upon and proves they hold [22][23][24]. The
  std-dev guide *requires* such comments [24].
- **Good practice:** Write SAFETY comments with *evidence*, referencing the specific type invariants
  and prior checks that make the operation sound [23]. Phrases like "this should be safe" are a red
  flag, not a justification [23].
- **Mistake to avoid:** Reaching for `unsafe` to silence the borrow checker. If safe Rust rejects it,
  the usual fix is restructuring ownership or using `Cell`/`RefCell`/`UnsafeCell` correctly — not
  `transmute` or raw-pointer aliasing [25][3].
- **Mistake to avoid:** Large `unsafe` blocks. When a memory bug appears, every line inside is a
  suspect; small blocks shrink the search space [22].

## Quick Reference: Highest-Frequency UB Bugs

- `mem::uninitialized()` / `zeroed()` for non-zeroable types → use `MaybeUninit` [15][14].
- `assume_init()` on a partially/never-initialized value (error paths!) [15].
- Two `&mut` (or `&` + `&mut`) to the same memory via raw pointers [12][6].
- `transmute` extending a lifetime → use-after-free the borrow checker would have caught [25].
- `transmute` an out-of-range integer into an `enum`/`bool`/`char` [15][6].
- int→ptr→int round-trips that launder provenance → use strict-provenance APIs [9][10].
- Panic unwinding across a plain `extern "C"` boundary → `catch_unwind` or `"C-unwind"` [16][17].

The throughline: `unsafe` is a *proof obligation*, not a permission slip. Make the obligation
explicit (SAFETY comments), make it small (tight blocks, safe wrappers), and make it *checkable*
(Miri in CI, sanitizers on FFI). Do that and unsafe Rust stays sound; skip it and the optimizer
will eventually find the gap for you.

## Sources

1. [`unsafe` keyword — std docs](https://doc.rust-lang.org/std/keyword.unsafe.html)
2. [Unsafe Rust — The Rust Programming Language (Book), ch. 20](https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html)
3. [What Unsafe Can Do — The Rustonomicon](https://doc.rust-lang.org/nomicon/what-unsafe-does.html)
4. [Safe Systems Programming in Rust — Communications of the ACM](https://cacm.acm.org/research/safe-systems-programming-in-rust/)
5. [Safety and Soundness in Rust — Jack O'Connor](https://jacko.io/safety_and_soundness.html)
6. [Behavior considered undefined — The Rust Reference](https://doc.rust-lang.org/reference/behavior-considered-undefined.html)
7. [Rust 1.84 introduces strict provenance APIs — InfoWorld](https://www.infoworld.com/article/3732079/rust-1-84-introduces-strict-provenance-apis.html)
8. [Pointers Are Complicated III: Pointer-integer casts exposed — Ralf Jung](https://www.ralfj.de/blog/2022/04/11/provenance-exposed.html)
9. [Tracking issue for strict_provenance (#95228) — rust-lang/rust](https://github.com/rust-lang/rust/issues/95228)
10. [`std::ptr` module — std docs (strict provenance APIs)](https://doc.rust-lang.org/std/ptr/index.html)
11. [RFC 3559: Rust Has Provenance — The Rust RFC Book](https://rust-lang.github.io/rfcs/3559-rust-has-provenance.html)
12. [Detecting Undefined Behavior in Rust with Miri in GitHub Actions — Kevin Flansburg](https://kflansburg.com/posts/improving-rust-codebase-quality-with-miri-in-ci/)
13. [`MaybeUninit` — std docs](https://doc.rust-lang.org/std/mem/union.MaybeUninit.html)
14. [Uninitialized Memory — The Rustonomicon](https://doc.rust-lang.org/nomicon/uninitialized.html)
15. [Uninitialized memory — Learn Unsafe Rust (Google)](https://google.github.io/learn_unsafe_rust/advanced_unsafety/uninitialized.html)
16. [FFI — The Rustonomicon](https://doc.rust-lang.org/nomicon/ffi.html)
17. [How to Create Safe FFI Bindings in Rust — OneUptime (2026)](https://oneuptime.com/blog/post/2026-01-30-rust-safe-ffi-bindings/view)
18. [Miri, Valgrind, and Sanitizers — Verifying Unsafe Code (Microsoft Rust Training)](https://microsoft.github.io/RustTraining/engineering-book/ch05-miri-valgrind-and-sanitizers-verifying-u.html)
19. [What's "new" in Miri (and there's a Miri paper!) — Ralf Jung, Dec 2025](https://www.ralfj.de/blog/2025/12/22/miri.html)
20. [Miri: Practical Undefined Behavior Detection for Rust — POPL 2026 paper (PDF)](https://research.ralfj.de/papers/2026-popl-miri.pdf)
21. [Glossary — Unsafe Code Guidelines Reference](https://rust-lang.github.io/unsafe-code-guidelines/glossary.html)
22. [Safety — Pragmatic Rust Guidelines (Microsoft)](https://microsoft.github.io/rust-guidelines/guidelines/safety/index.html)
23. [Safety Comments Matter — TheBestTvarynka](https://tbt.qkation.com/posts/safety-comments-matter/)
24. [Safety comments policy — Standard Library Developers Guide](https://std-dev-guide.rust-lang.org/policy/safety-comments.html)
25. [Unsafe Rust: How and when (not) to use it — LogRocket](https://blog.logrocket.com/unsafe-rust-how-and-when-not-to-use-it/)

## Verification notes

Adversarially fact-checked on 2026-06-21 against current stable Rust (1.85+) and
edition 2024. The report is substantively accurate and well-cited; the technical core
(UB categories, provenance, `MaybeUninit`, FFI, Miri) holds up. Cited sources were
sampled and verified live. The issues below are corrections/refinements, not body
rewrites.

1. **`mem::zeroed()` is not deprecated (line 125).** The report states "`mem::uninitialized()`
   / `mem::zeroed::<T>()` ... are ... deprecated." Only `mem::uninitialized` was deprecated
   (since Rust 1.39, RFC 1892). `mem::zeroed` was deliberately **not** deprecated — it is
   safe and useful for genuinely all-zero-valid types; it is only *instant UB* when the
   all-zeros bit pattern violates `T`'s validity invariant. The "instant UB for non-zeroable
   `T`" framing is correct; the blanket "deprecated" label applied to `zeroed` is wrong.
   Source: https://doc.rust-lang.org/std/mem/fn.zeroed.html (no `#[deprecated]`) and
   https://github.com/rust-lang/rust/issues/53491 (decision not to deprecate `zeroed`).

2. **Edition-2024 `static mut` nuance is missing (lines 16–18).** The "five unsafe
   superpowers" list (which correctly includes "access/modify a `static mut`," matching the
   current Rust Book) omits that under edition 2024 the `static_mut_refs` lint is
   **deny-by-default**: creating a *reference* to a `static mut` is now an error by default.
   The modern idiom is raw-borrow operators (`&raw const`/`&raw mut STATE`, or
   `&mut *&raw mut STATE` only when a reference is truly needed). Given the report explicitly
   targets edition 2024, this is worth a sentence. The superpower count itself is still
   correct. Source: https://doc.rust-lang.org/edition-guide/rust-2024/static-mut-references.html

3. **Edition-2024 FFI changes not mentioned (FFI section).** Edition 2024 makes two
   FFI-relevant changes the report could note: `extern` blocks must be written
   `unsafe extern { ... }`, and the `no_mangle`/`export_name`/`link_section` attributes must
   now be wrapped as `#[unsafe(no_mangle)]` etc. These tighten the very "trust boundary" the
   section discusses. Not an error in the report, but a relevant edition-2024 omission.
   Sources: https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-extern.html and
   https://doc.rust-lang.org/edition-guide/rust-2024/unsafe-attributes.html

Verified as correct (spot-checked):
- Strict-provenance APIs stabilized in **Rust 1.84** (`without_provenance`, `addr`,
  `with_addr`, `map_addr`, `expose_provenance`/`with_exposed_provenance`); RFC 3559 accepted.
  Source: https://github.com/rust-lang/rust/pull/130350.
- Miri: the POPL 2026 paper [20] does state Miri ran on **>100,000 Rust libraries** and
  executed **>70% of combined test suites**, found dozens of real bugs, and is integrated into
  std CI — and that Miri "finds all de-facto UB in deterministic Rust programs." (Note: that
  evaluation data lives in the paper [20], not the blog post [19]; both are cited.)
  Source: https://research.ralfj.de/papers/2026-popl-miri.pdf and
  https://www.ralfj.de/blog/2025/12/22/miri.html.
- Miri's **default** model is still **Stacked Borrows**; **Tree Borrows** remains opt-in via
  `-Zmiri-tree-borrows` (Tree Borrows won a PLDI 2025 Distinguished Paper but is not the
  default). The report's wording and CI advice are correct.
  Source: https://github.com/rust-lang/miri/.
- The UB-categories list matches the current Rust Reference; the five-superpowers list matches
  the current Rust Book ch. 20.
