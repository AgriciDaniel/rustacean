# Ownership, Borrowing & Lifetimes — Pitfalls

> Scope: practical, opinionated guidance for fighting (and winning against) the borrow checker on stable Rust ~1.85+ with the 2024 edition. Each section pairs the GOOD practice with the MISTAKE TO AVOID, plus rationale and a tiny sketch where it helps.

Rust's ownership model is not a tax you pay; it is a static proof of memory and data-race safety that the compiler checks for you [1]. Most "fights" with the borrow checker are the checker telling you something genuinely true about your data's aliasing. The skill is learning to *restructure* so the truth becomes expressible, and reaching for escape hatches (`clone`, `Rc<RefCell<_>>`, `unsafe`) only when restructuring is genuinely worse. The borrow checker is best treated as a negotiating partner, not a foe [2].

## Mental model first: what lifetimes actually are

A lifetime is a *compile-time region* describing how long a borrow is valid — it constrains references, it is not the runtime "lifetime" of a value [3]. Getting this wrong is the root of most lifetime confusion.

The most damaging misconceptions, with their corrections [3]:

- **Lifetimes change at runtime.** No — they are statically resolved; a container cannot "swap" a reference to lengthen its region at runtime [3].
- **`T: 'static` means "lives for the whole program."** Read it as "*can* live as long as `'static`," i.e. contains no non-`'static` references. An owned `String` is `'static` and still gets dropped early [3].
- **`&'a T` and `T: 'a` are the same.** `T: 'a` is strictly more general: it accepts owned types and types containing references, whereas `&'a T` is specifically a reference [3].
- **Generic `T` excludes references.** `T` is a *superset* that includes `&U` and `&mut U`; that is why `T: 'static` bounds matter on generic APIs [3].
- **"If it compiles, my lifetime annotations are right."** The compiler only proves memory safety; over-restrictive-but-valid annotations compile yet needlessly reject callers [3].

MISTAKE TO AVOID: blindly applying the compiler's suggested fix. Its suggestions guarantee *compilation*, not that the resulting signature matches your intended API contract [3].

## Lifetime elision: lean on it, but know the three rules

Elision lets you omit lifetimes where the compiler can infer "the obvious" choice. The three function rules, applied in order [4]:

1. Each elided input lifetime becomes its **own distinct** parameter.
2. If there is **exactly one** input lifetime, it is assigned to **all** elided output lifetimes.
3. In methods, if the receiver is `&self`/`&mut self`, **`self`'s lifetime** is assigned to all elided outputs.

```rust
fn first(s: &str) -> &str { /* rule 2: in-lifetime -> out */ &s[..1] }
fn longest(a: &str, b: &str) -> &str { /* ILLEGAL: rule 1 gives two distinct
   inputs, no rule picks the output -> you must annotate <'a> */ a }
```

GOOD: use `'_` to make an *elided* lifetime visible in paths and `impl` headers (`impl Trait for Foo<'_>`), which keeps signatures honest without manual naming [4]. Also know: `const`/`static` items are implicitly `'static`, and `Box<dyn Trait>` defaults to `Box<dyn Trait + 'static>` — trait objects always carry a lifetime bound even when invisible [4][3].

MISTAKE TO AVOID: adding explicit `<'a>` everywhere "to be safe." Nearly all non-generic code already has elided lifetimes inferred correctly [3]; redundant annotations add noise and frequently *over-constrain* (e.g. tying two independent inputs to one region). Annotate only when elision genuinely can't decide.

## The classic borrow-checker fights and idiomatic fixes

### 1. "Cannot borrow as mutable more than once" / overlapping borrows

Usually means you are holding a shared borrow alive across a mutation. Thanks to **NLL** (non-lexical lifetimes, default since Rust 1.63), a borrow ends at its *last use*, not at the end of its lexical scope — so simply reordering so the read finishes before the write often just works now [5].

```rust
let mut v = vec![1, 2, 3];
let first = &v[0];      // shared borrow
println!("{first}");    // last use of `first` -> borrow ends here (NLL)
v.push(4);              // OK: no longer borrowed
```

### 2. Borrowing two struct fields at once ("split borrows")

`self.a` and `self.b` are *disjoint*, and the compiler permits borrowing them simultaneously through field access [6]. The fight appears when you route through a `&mut self` *method* that opaquely borrows all of `self`.

GOOD: borrow fields directly, or factor the work into a free function taking the two fields as separate parameters; for slices use `split_at_mut` to get two non-overlapping `&mut` halves [6].

MISTAKE TO AVOID: introducing `Rc<RefCell<_>>` to dodge a two-field borrow. That trades a *compile-time* problem you could solve structurally for a *runtime* panic risk (see interior mutability below).

### 3. Closures capturing too much

Pre-2021, a closure captured an entire variable even if it touched one field; in **edition 2021+** closures use **disjoint capture** (RFC 2229), capturing only the fields actually used — so a closure can borrow `self.a` while you still use `self.b` [7].

MISTAKE TO AVOID: assuming closure signatures follow the function elision rules. They do not — closure inputs and outputs get *independent* lifetimes, which is why returning a borrow from a closure is often more restrictive than from an equivalent `fn` [3].

### 4. Returning a reference / borrow-then-modify loops

The canonical NLL pain point is "problem case 3": code like `last_or_push` that conditionally returns an existing borrow *or* mutates and returns a new one. Current stable NLL still rejects some of these; the upcoming **Polonius** borrow checker accepts them [5][8].

GOOD interim fix: compute a `bool`/index first, drop the borrow, then branch:

```rust
fn last_or_push(v: &mut Vec<String>) -> &String {
    if v.is_empty() { v.push("x".into()); }  // borrow released before reborrow
    v.last().unwrap()
}
```

## Polonius and NLL: where the frontier is in 2026

NLL was the second-generation borrow checker (control-flow-graph based instead of lexical), default since 1.63 [5]. **Polonius** is the next generation: a *location-sensitive* analysis that is a strict superset of NLL — it accepts everything NLL accepts plus extra patterns such as NLL problem case 3 and lending-iterator filtering [8]. As of the 2025–2026 project goals, a "Polonius alpha" prototype has landed on nightly, passes crater and performance runs, and the team is targeting stabilization, accepting a ~10–20% borrow-check overhead for the added expressiveness [8].

GOOD: if a clearly-correct function is rejected, check whether it's a known NLL limitation before restructuring heavily — and you can experiment with `-Z polonius` on nightly [8].

MISTAKE TO AVOID: writing `unsafe` to escape a pattern that is merely an NLL precision gap. A `bool`/index dance (above) is safe and forward-compatible.

## Self-referential structs: usually a smell

A struct that holds a reference into its own data is the canonical thing Rust forbids, because *moving* the struct invalidates the internal pointer, producing a dangling reference [9]. You cannot express `struct S<'a> { data: String, slice: &'a str }` pointing `slice` into its own `data`.

Idiomatic options, in rough order of preference [9][10]:

1. **Don't.** Store *indices/ranges* instead of references (`struct S { data: String, span: Range<usize> }`). This is the overwhelmingly common, zero-`unsafe` answer.
2. **Arena / `id-arena` / `Vec` + indices** when you need a graph: every node lives in one owner, edges are indices, so nothing moves out from under a borrow [9].
3. **`Pin`** when an internal pointer is unavoidable (notably self-referential `Future`s from `async`). `Pin<P>` guarantees the pointee never moves before `Drop`, which is exactly the invariant a self-reference needs [9][11]. `Box::pin` is the easy constructor. This is what `async`/`await` uses under the hood [11].
4. **Crates like `ouroboros`/`self_cell`** to generate the `unsafe` glue safely if you truly need owned-data-plus-borrow in one type [9].

MISTAKE TO AVOID: hand-rolling self-references with raw pointers and `unsafe` "just this once." `Pin`'s rules are subtle and easy to violate; reach for indices or a vetted crate first [9][11].

## When to `clone` vs. restructure

`clone()` is the most over-used escape hatch: it makes the error disappear but can silently turn an O(1) borrow into an O(n) deep copy, and frequently signals a *design* problem — do you actually want two independent copies of this data? [12]

A practical decision order:

1. **Borrow instead.** Change the signature to take `&T`/`&mut T` and "lend" the value rather than give it away; this is the idiomatic, fastest default [2][12].
2. **Restructure ownership.** If borrows tangle, move the data (and the functions using it) into a struct so ownership is clear, or split a long function so borrows don't overlap [13][2].
3. **Cheap clone on purpose.** If you genuinely need shared ownership (e.g. functional-style pipelines, multi-owner), make clones cheap with `Rc`/`Arc` so `clone` is a refcount bump, not a deep copy [12].
4. **Deep `clone` as a last resort**, ideally on a cold path. In a hot loop, prefer mutation/borrowing — it is both faster and more idiomatic [12].

MISTAKE TO AVOID: scattering `.clone()` to silence the checker in hot paths. The functional "clone everything" style can be markedly slower than mutate-in-place; reserve deep clones for cold paths or make them `Arc`-cheap [12].

## Interior mutability: power with a runtime bill

`Cell<T>` and `RefCell<T>` provide *interior mutability* — mutation through a shared `&` reference — in contrast to Rust's default *inherited* mutability. Inherited mutability is preferred; interior mutability is "something of a last resort" [14][15].

Tradeoffs that should drive the choice [14]:

- **`Cell<T>`**: get/set/replace by value, **no runtime checks**, but `Copy`/move-only (no borrowing the interior). Cheap and panic-free; limited.
- **`RefCell<T>`**: `borrow()`/`borrow_mut()` enforce the aliasing rules **at runtime** and **panic** (or `try_borrow` errors) on violation. You move the *check* from compile time to run time — so bugs surface later, possibly in production, with a small runtime cost [14].

The notorious combo is `Rc<RefCell<T>>` for shared-mutable graphs/trees: it compiles, but it is verbose, leaks easily into cycles (`Rc` cycles leak memory — use `Weak` for back-edges), and converts compile-time guarantees into runtime panics [15][14]. *Learning Rust With Entirely Too Many Linked Lists* is blunt that `Rc<RefCell<_>>` "can get unwieldy" and that you should prefer plain `Vec`/`VecDeque` unless you truly need the linked structure [15].

GOOD: use interior mutability surgically — e.g. a `Cell<usize>` cache counter, an `Arc<Mutex<_>>` for genuinely shared concurrent state — and keep the `RefCell`/`Mutex` region small so borrows don't escape and cause re-entrant panics/deadlocks [14].

MISTAKE TO AVOID: defaulting to `Rc<RefCell<_>>` for any tree/graph. First try arena + indices (compile-time-checked, cache-friendlier, no cycle leaks); reach for `Rc<RefCell>` only when shared mutation with unpredictable ownership is the actual requirement [15][9].

## A pragmatic checklist

- Reorder so borrows end before the next mutation (NLL does the rest) [5].
- Borrow disjoint fields directly; use `split_at_mut` for slices [6].
- Replace internal references with indices/ranges or an arena before considering `Pin` or `unsafe` [9].
- Add lifetimes only when elision can't decide; prefer `'_` to keep them visible-but-light [4].
- `clone` deliberately: borrow → restructure → `Arc`-cheap-clone → deep clone (cold paths) [12].
- Treat `RefCell`/`Rc<RefCell>` as a runtime-checked last resort, not a default [14][15].

## Sources

1. The Rust Programming Language — Validating References with Lifetimes: https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html
2. fasterthanlime — Declarative memory management: https://fasterthanli.me/articles/declarative-memory-management
3. pretzelhammer — Common Rust Lifetime Misconceptions: https://github.com/pretzelhammer/rust-blog/blob/master/posts/common-rust-lifetime-misconceptions.md
4. The Rust Reference — Lifetime elision: https://doc.rust-lang.org/reference/lifetime-elision.html
5. The Rust Blog — Non-lexical lifetimes (NLL) fully stable: https://blog.rust-lang.org/2022/08/05/nll-by-default/
6. The Rustonomicon — Splitting Borrows: https://doc.rust-lang.org/nomicon/borrow-splitting.html
7. The Rust Edition Guide — Disjoint capture in closures (RFC 2229): https://doc.rust-lang.org/edition-guide/rust-2021/disjoint-capture-in-closures.html
8. Rust Project Goals — Stabilize and model Polonius / Scalable Polonius support on nightly: https://rust-lang.github.io/rust-project-goals/2026/polonius.html
9. Rust RFC Book — RFC 2349 (Pin) and self-referential structures: https://rust-lang.github.io/rfcs/2349-pin.html
10. The Rust Programming Language Forum — Proper way to create self-referential structs (with or without Pin): https://users.rust-lang.org/t/proper-way-to-create-self-referential-structs-with-or-without-pin/65026
11. The Rust standard library — std::pin module documentation: https://doc.rust-lang.org/std/pin/index.html
12. HAMY — The Problem with Clones in Rust: https://hamy.xyz/blog/2026-02_the-problem-with-clones-in-rust
13. qouteall — How to Avoid Fighting Rust Borrow Checker: https://qouteall.fun/qouteall-blog/2025/How%20to%20Avoid%20Fighting%20Rust%20Borrow%20Checker
14. The Rust Programming Language — RefCell<T> and the Interior Mutability Pattern: https://doc.rust-lang.org/book/ch15-05-interior-mutability.html
15. Learning Rust With Entirely Too Many Linked Lists — A Bad Safe Doubly-Linked Deque: https://rust-unofficial.github.io/too-many-lists/fourth.html

## Verification notes

Adversarially fact-checked 2026-06-21 against current authoritative sources (edition 2024 / stable Rust ~1.85+). All key technical claims verified accurate and current; no corrections required. Spot-checks performed:

- **NLL default since 1.63** — confirmed by the cited Rust blog ([NLL by default](https://blog.rust-lang.org/2022/08/05/nll-by-default/)). Minor nuance (not an error): NLL was already default for the 2018 edition from its introduction; Rust 1.63 made it the sole borrow checker for *all* editions (including 2015). The report's phrasing matches its cited source.
- **Three lifetime elision rules; `const`/`static` implicitly `'static`; `Box<dyn Trait>` defaults to `+ 'static`** — all confirmed by the [Rust Reference, Lifetime elision](https://doc.rust-lang.org/reference/lifetime-elision.html). (Elision rule 2 is precisely "exactly one lifetime used in the parameters, elided or not" — the report's "exactly one input lifetime" is a fair paraphrase.)
- **Polonius status** — confirmed verbatim against the cited [Rust Project Goals (2026) Polonius page](https://rust-lang.github.io/rust-project-goals/2026/polonius.html): a functional Polonius-alpha prototype has landed on nightly, passes crater and perf runs, the team explicitly accepts a "10–20%" borrow-check overhead, and stabilization is "the natural next step." One known soundness issue (opaque types) remains.
- **Disjoint closure capture (RFC 2229) in edition 2021** — confirmed stabilized as part of Rust 2021 ([Edition Guide](https://doc.rust-lang.org/edition-guide/rust-2021/disjoint-capture-in-closures.html)).
- **Pin = RFC 2349, self-referential structs, `split_at_mut`, disjoint struct-field borrows** — confirmed against [RFC 2349 (Pin)](https://rust-lang.github.io/rfcs/2349-pin.html) and the [Rustonomicon, Splitting Borrows](https://doc.rust-lang.org/nomicon/borrow-splitting.html).

Verdict: solid — checked and current as of June 2026.
