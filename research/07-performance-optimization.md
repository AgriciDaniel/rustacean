# Performance & Optimization

Rust gives you C-class performance *by default*, which is precisely why so much "optimization"
in Rust is misguided: people pay complexity costs to chase wins the compiler already delivered.
This report is opinionated. For every technique it pairs the **good practice** with the
**mistake to avoid**, grounded in canonical sources (the Rust Performance Book, the official
Book, the Cargo reference, and recognized practitioners like Aleksey Kladov/matklad and
Sergey "Shnatsel" Davidoff). Target audience: stable Rust ~1.85+ on edition 2024.

The single most important rule, stated up front and repeated throughout: **measure first**.
"Never optimize without data. Your intuition about bottlenecks is often wrong, and premature
optimization wastes time on code that doesn't matter." [1][9]

---

## 1. Profile First, Always (the meta-rule)

**Good practice.** Treat optimization as a measurement loop: profile to find *where* time goes,
benchmark to confirm a change *actually helped*, then commit. "Use a profiler to identify the
parts of your code where you're spending most of your time, and use benchmarking to ensure that
your changes actually make your program faster." [9] A flamegraph "costs 10 minutes and gives
the answer directly." [10]

**Mistake to avoid.** Reading code, guessing the hot spot, and rewriting it into something
clever and unmaintainable. "Guessing where your code is slow almost always leads you down the
wrong path." [9] Bottlenecks frequently live in unexpected places (allocator behavior, a `clone`
in a trait impl, a `format!` in a log line), not where your gut says.

**Rationale.** Rust's zero-cost abstractions mean the "obvious slow code" is often already fast,
while the real cost hides in allocation, syscalls, or cache misses that no amount of staring at
source will reveal.

---

## 2. The Profiling Toolchain (perf, flamegraph, samply, criterion)

The professional workflow has two distinct halves that answer different questions: **profilers**
tell you *where* time goes; **benchmarks** tell you *how much* a function takes and whether a
change moved the needle. [9]

**Profilers (where):**

- **`samply`** is the current low-friction default. It's a sampling profiler that works on
  macOS, Linux, and Windows and opens results in the Firefox Profiler's interactive UI with
  essentially no setup beyond `cargo install samply`. [4][10] "Start with sampling unless you
  have a strong reason not to." [10]
- **`cargo flamegraph`** wraps `perf` (Linux) or DTrace (macOS/BSD) and emits an interactive
  SVG; wide plateaus are your hot functions. [3][4] Run it as `cargo flamegraph --bin my_app`.
- **`perf`** directly is the Linux power-tool for CPU/cache counters. [4]
- **DHAT** (via `dhat-rs`) is the allocation profiler — use it to find *where allocations
  happen*, not just where CPU goes. [6]

**Benchmarks (how much):**

- **Criterion** is the standard. It runs benchmarks repeatedly, computes confidence intervals,
  and tells you whether a delta is statistically significant or just noise, and auto-generates
  HTML reports at `target/criterion/report/index.html`. [1] Plain `cargo bench` works (it uses
  the `bench` profile with optimizations on) but lacks Criterion's statistical rigor. [1][9]
- **iai/iai-callgrind** count *instructions* via Cachegrind for deterministic, CI-friendly
  results immune to machine noise. [1]

**Good practice.** Build a release binary *with debug symbols* for profiling
(`[profile.release] debug = true`, and don't strip), so frames are readable. [3][4]

**Mistake to avoid.** Profiling a debug build (numbers are meaningless), or stripping symbols and
then staring at `0x7f...` addresses. Also: trusting a single criterion run — let it gather
enough samples to report a confidence interval. [1]

```toml
# A dedicated profiling profile keeps release lean but stays debuggable
[profile.profiling]
inherits = "release"
debug = true
strip = false
```

---

## 3. Reducing Heap Allocations

Allocation is "moderately expensive" — it can take locks, manipulate data structures, and
sometimes hit a syscall. [6] Reducing allocations is often the highest-ROI optimization in real
Rust code, and DHAT shows where to look. [6]

**Good practices:**

- **Pre-size collections.** `Vec::with_capacity(n)` turns "~log₂(n) reallocations" into one.
  Pushing 20 items into a default `Vec` can cause 4 allocations; one `with_capacity(20)` does it
  in one. [6]
- **Reuse buffers across iterations.** Hoist the `Vec`/`String` out of the loop and `clear()` it
  each pass instead of reallocating. [6]
- **`Cow<'_, T>`** for "usually borrowed, occasionally owned" data — allocate only on the
  mutation path. [6]
- **Kill unnecessary `clone`s.** DHAT flags hot clone sites; many are vestigial and "can simply
  be removed" once borrows are tightened. [6]

**Mistake to avoid.** `.clone()`-driven development to silence the borrow checker, and
`String`/`Vec` churn inside hot loops. Note even small wins compound: cutting "10 allocations per
million instructions" can be a measurable ~1% gain. [6]

```rust
// BAD: reallocates every iteration
for line in input { let mut buf = Vec::new(); process(&mut buf, line); }
// GOOD: one allocation, reused
let mut buf = Vec::with_capacity(64);
for line in input { buf.clear(); process(&mut buf, line); }
```

---

## 4. SmallVec, Arenas, and Bump Allocation

When allocation *is* the bottleneck (confirmed by DHAT), specialized strategies pay off "with
minimal code changes." [7][8]

- **`SmallVec<[T; N]>` / `smallstr`** store up to `N` elements inline on the stack, spilling to
  the heap only when they grow past `N` — eliminating allocation for the common small case. [6]
  Tradeoff: it's "slightly slower than `Vec` for normal operations because it must always check
  if the elements are heap-allocated." [6]
- **Arena / bump allocators** (`bumpalo`, `typed-arena`) shine when you have "many allocations
  with a shared lifetime" — request handling, compiler passes, per-frame game logic. [7][8]
  Allocation is a pointer bump; the whole arena is freed at once. `bumpalo` is the most-downloaded
  arena; `typed-arena` is simpler but single-type. [7][8]

**Mistake to avoid.** Reaching for `SmallVec` or an arena *speculatively*. The inline-vs-heap
branch makes `SmallVec` a net loss when collections are usually large [6], and arenas add
lifetime complexity that fights the borrow checker for no benefit if allocation wasn't your
hot spot. Profile, then introduce.

---

## 5. Iterators vs. Loops (and bounds-check elimination)

**Good practice: default to iterators.** Rust iterators are a zero-cost abstraction; chains like
`.iter().filter().map().sum()` compile to the same machine code as the hand-written loop, and the
official Book's benchmarks show for-loops and iterators performing equivalently. [11] Iterators
also "avoid bounds checks entirely because the iteration is built into the abstraction" — the
index is never out of range by construction. [12][13]

**Mistake to avoid.** Hand-rolling index loops "for speed." Indexing inside a loop
(`v[i]`) introduces a runtime bounds check that, in complex patterns (multiple arrays, computed
indices), LLVM can't always prove away — costing ~1–2ns each. [12] Manual indexing also
introduces aliasing concerns that *inhibit* vectorization the iterator form would have enabled. [12]

**When you must index — eliminate bounds checks *safely*** (the Performance Book's ladder): [13]

1. Replace direct indexing with iteration.
2. Slice the `Vec` *before* the loop and index the slice (narrows the compiler's analysis).
3. Add an `assert!` constraining the index range; LLVM uses it to delete later checks.
4. Only as a last resort, `get_unchecked` (`unsafe`) — and prove the invariant. [13]

```rust
// Hint the optimizer; the assert lets LLVM drop per-iteration checks
assert!(idx.len() <= data.len());
for &i in idx { sum += data[i]; }   // data[i] check provably safe
```

Davidoff's deeper guidance: you can usually reach unsafe-level speed with `assert!`s and
iterator/`zip` patterns *without* `unsafe`. [12] Avoid `get_unchecked` unless a profiler proves
the check matters and you've exhausted safe options.

---

## 6. `#[inline]`: What It Actually Does, and the Myths

This is the most misunderstood attribute in Rust. The mechanism: **within a crate, the compiler
already inlines well** ("a joke that LLVM's heuristic for when a function should be inlined is
'yes'"). [2] `#[inline]`'s real job is **cross-crate inlining**: a downstream crate sees only your
function's *signature*, not its body, so it can't inline the call unless you mark it `#[inline]`,
which makes the compiler emit a copy of the body into every using crate. [2][5]

**The three forms** (all *suggestions*, not guarantees): [14]
- `#[inline]` — suggests inlining (enables cross-crate).
- `#[inline(always)]` — strongly suggests; inlines "in all but the most exceptional cases."
- `#[inline(never)]` — strongly suggests *not* inlining.

**Good practice.**
- *In libraries:* proactively `#[inline]` small public functions, especially trivial trait
  impls like `Deref`/`AsRef`/`Index`. [2][5]
- *In applications:* apply *reactively* — only after profiling fingers a small hot function the
  compiler declined to inline. [2][14]
- For large functions with one hot call site, split into an `#[inline(always)]` hot core wrapped
  by an `#[inline(never)]` cold shell. [14]

**Myths / mistakes to avoid:**
- **Myth: slap `#[inline]` everywhere.** It "makes compile time worse" because every using crate
  recompiles a copy. [2] LLVM already inlines local trivial calls. [2]
- **Myth: `#[inline]` on private functions helps.** It "usually isn't necessary" intra-crate. [2]
- **Myth: it's transitive.** It isn't — if a trivial public fn calls a trivial private fn, both
  need it. [5]
- **Myth: generics need `#[inline]`.** Generic functions are *implicitly* inlinable (the body
  must be available to monomorphize), which instead causes silent code bloat; wrap a generic
  public fn around a non-generic private impl to contain it. [2][5]
- **Effects are unpredictable:** adding an inline can *evict* a nearby function that was being
  inlined, and can hurt performance. Always re-measure. [14] Verify with Cachegrind: an inlined
  function's first/last lines carry *no* event counts. [14]

**The pragmatic alternative for whole-program speed: don't hand-annotate — turn on LTO** (next
section), which gives superior cross-crate optimization without per-crate `#[inline]` bloat. [2]

---

## 7. Build Configuration: LTO, codegen-units, opt-level, panic, target-cpu

The cheapest performance wins in Rust require *zero code changes* — they live in `Cargo.toml`. [4]
Defaults: `release` uses `opt-level = 3`, `codegen-units = 16`, thin-local LTO. [15]

**For maximum runtime speed** (the Performance Book's recommended stack): [4]

```toml
[profile.release]
codegen-units = 1     # whole-crate optimization; slower compile
lto = "fat"           # cross-crate inlining/optimization; may not always help
panic = "abort"       # removes unwinding tables & landing pads
# plus: an alternative allocator (jemalloc/mimalloc), and optionally:
# RUSTFLAGS="-C target-cpu=native"
```

- **`codegen-units = 1`** maximizes optimization by removing the parallelism boundary the
  optimizer can't see across — at the cost of longer, single-threaded compiles. [4][15]
- **LTO:** `"thin"` is more aggressive than the default and usually a clear win;
  `"fat"` is most aggressive and "may improve performance and reduce binary size further (but not
  always)" — both raise build time. [4][15]
- **Alternative allocators** (jemalloc, mimalloc) can yield "large improvements in runtime speed
  and large reductions in memory usage" depending on workload. [4]
- **`-C target-cpu=native`** unlocks modern SIMD but **breaks portability** to older CPUs. [4]
- **PGO** (profile-guided optimization) is the next tier when the above is exhausted. [4]

**For minimum binary size:** `opt-level = "z"`, `codegen-units = 1`, `lto = "fat"`,
`panic = "abort"`, `strip = "symbols"`. [4] Note `strip` "may make your program more difficult to
debug and profile." [4]

**Free wins (no tradeoffs):** swap in a faster linker — `lld`, `mold`, or `wild` — and you cut
link time with "no trade-offs"; disabling debug info speeds dev builds "by as much as 20–40%." [4]

**Mistake to avoid.** Shipping `target-cpu=native` binaries to users (illegal-instruction crashes
on older hardware). And the cardinal sin: flipping all these knobs at once. **"Benchmark all
changes, one at a time, to ensure they have the expected effects."** [4] `fat` LTO sometimes
*regresses* speed or only helps size — you cannot know without measuring. [4][15]

---

## 8. Avoiding Premature Optimization (putting it together)

**Good practice — the optimization loop:**
1. Write clear, idiomatic code (iterators, owned types where simplest). Idiomatic Rust is usually
   already fast. [11]
2. Establish a baseline with Criterion. [1][9]
3. Profile with samply/flamegraph/DHAT to find the *actual* hot spot. [4][10]
4. Apply the *narrowest* fix (pre-size a `Vec`, drop a clone, add an `assert!`), and re-benchmark
   to confirm a statistically significant win. [1][6]
5. Reach for `unsafe`, `SmallVec`, arenas, or hand-tuned `#[inline]` only when data demands it. [7][13]

**Mistake to avoid.** "Premature optimization... may unnecessarily complicate the code and waste
development time." [9] Every speculative `unsafe`, hand-rolled loop, or scattered `#[inline]` is a
maintenance liability you took on without evidence it helped. In Rust specifically, the temptation
is acute because the tools *exist* — but `get_unchecked` and `#[inline(always)]` are debts, not
defaults.

**Rule of thumb hierarchy (cheapest → most invasive):**
build flags (LTO/codegen-units) → algorithmic fix → allocation reduction → data-structure choice
(`SmallVec`/arena) → safe bounds-check hints → targeted `#[inline]` → `unsafe`. Stop as soon as
you've hit your target; the later rungs cost readability and safety. [4][13][14]

---

## Sources

1. Criterion.rs — statistical benchmarking: https://lib.rs/crates/criterion · benchmarking with Criterion & iai: https://blog.lambdaclass.com/benchmarking-and-analyzing-rust-performance-with-criterion-and-iai/
2. Aleksey Kladov (matklad), "Inline In Rust": https://matklad.github.io/2021/07/09/inline-in-rust.html
3. flamegraph-rs/flamegraph: https://github.com/flamegraph-rs/flamegraph
4. The Rust Performance Book — Build Configuration: https://nnethercote.github.io/perf-book/build-configuration.html
5. The Rust Reference — Codegen attributes (`inline`): https://doc.rust-lang.org/nightly/reference/attributes/codegen.html
6. The Rust Performance Book — Heap Allocations: https://nnethercote.github.io/perf-book/heap-allocations.html
7. fitzgen/bumpalo — bump allocation arena: https://github.com/fitzgen/bumpalo
8. thomcc/rust-typed-arena: https://github.com/thomcc/rust-typed-arena
9. The Rust Performance Book — Profiling (overview/principles): https://nnethercote.github.io/perf-book/profiling.html
10. nicole@web, "Profiling Rust programs the easy way" (samply): https://ntietz.com/blog/profiling-rust-programs-the-easy-way/
11. The Rust Programming Language Book — Ch.13.4, Comparing Performance: Loops vs. Iterators: https://doc.rust-lang.org/book/ch13-04-performance.html
12. Sergey "Shnatsel" Davidoff, "How to avoid bounds checks in Rust (without unsafe!)": https://shnatsel.medium.com/how-to-avoid-bounds-checks-in-rust-without-unsafe-f65e618b4c1e
13. The Rust Performance Book — Bounds Checks: https://nnethercote.github.io/perf-book/bounds-checks.html
14. The Rust Performance Book — Inlining: https://nnethercote.github.io/perf-book/inlining.html
15. The Cargo Book — Profiles (opt-level, codegen-units, lto, panic): https://doc.rust-lang.org/cargo/reference/profiles.html

---

## Verification notes

Adversarially fact-checked 2026-06-21 against current authoritative sources. The report is
**solid and current** for stable Rust (1.95/1.96 as of mid-2026) and edition 2024 (which shipped
with Rust 1.85 in Feb 2025, so the report's "stable Rust ~1.85+ on edition 2024" framing is
accurate). Sampled and confirmed the load-bearing cited sources directly; no corrections required.

- **Build configuration (§7, source [4]).** Verified against the Rust Performance Book. All claims
  hold verbatim: thin LTO is "a little more aggressive" than the default and "likely to improve
  runtime speed and reduce binary size while also increasing compile times"; fat LTO "may improve
  performance and reduce binary size further (but not always)"; alternative allocators (jemalloc/
  mimalloc) can give "large improvements in runtime speed and large reductions in memory usage";
  alternative linkers (lld/mold/wild) have "no trade-offs"; and the summary rule "Benchmark all
  changes, one at a time, to ensure they have the expected effects" is quoted correctly.
  https://nnethercote.github.io/perf-book/build-configuration.html
- **#[inline] (§6, source [2]).** Verified against matklad's "Inline In Rust." The cross-crate
  rationale, the "LLVM's heuristic for when a function should be inlined is 'yes'" joke, generics
  being implicitly inlinable, non-transitivity ("if a trivial public function calls a trivial
  private function, you need to #[inline] both"), the library-proactive / application-reactive
  split, and LTO as the whole-program alternative are all accurately represented.
  https://matklad.github.io/2021/07/09/inline-in-rust.html
- **Bounds checks (§5, source [13]).** Verified against the Performance Book. The four-rung ladder
  (iterate → slice before the loop → assert! to hint the compiler → get_unchecked as last resort)
  matches the source exactly. https://nnethercote.github.io/perf-book/bounds-checks.html
- **Iterators vs. loops (§5/§8, source [11]).** Verified the Book page exists and concludes "The
  two implementations have similar performance!" and describes iterators as a zero-cost
  abstraction — exactly as cited. https://doc.rust-lang.org/book/ch13-04-performance.html
- **Minor, non-blocking.** Source [11] is cited as "Ch.13.4"; the live page is titled "Comparing
  Performance: Loops vs. Iterators" at the same URL — content and benchmark are unchanged, so the
  citation is still valid.
