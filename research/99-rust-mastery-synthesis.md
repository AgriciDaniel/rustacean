# Rust Mastery — Synthesis

A cross-cutting distillation of the ten topic reports in this corpus, targeting **stable Rust ~1.85+ on edition 2024** (June 2026). Two halves: the practices that recur across topics as *good*, and the mistakes that recur as *footguns*. Every bullet links back to the report(s) it draws from. See the [index](00-INDEX.md) for the full report list and [consolidated sources](sources.md) for all citations.

The single throughline of the whole corpus: **push invariants into the type system, measure before you optimize, and reach for runtime escape hatches (`clone`, `Rc<RefCell>`, `unsafe`, `Arc<Mutex>`) only when the compiler genuinely can't help.**

---

## Do this (good practices)

### Type-driven design
- Make invalid states unrepresentable — use enums (sum types), private fields, and exhaustive `match` so the compiler rejects nonsense; "parse, don't validate" at boundaries ([idiomatic API design](01-idiomatic-api-design.md), [anti-patterns](05-anti-patterns-footguns.md)).
- Use the newtype pattern to encode units, IDs, and validated scalars; validate at construction and return `Result`, so once you hold the value it is *always* valid ([idiomatic API design](01-idiomatic-api-design.md), [anti-patterns](05-anti-patterns-footguns.md)).
- Encode invariants in types rather than re-checking at runtime — a richer type today removes a class of runtime checks and tests tomorrow ([error handling](03-error-handling.md), [idiomatic API design](01-idiomatic-api-design.md)).
- Reach for typestate (and crates like `bon`) when a builder has required fields, so calling `build()` early is a *compile* error, not a runtime one ([idiomatic API design](01-idiomatic-api-design.md)).

### API design
- Follow the official API Guidelines as a PR review tool: `C-CASE`/`C-CONV` naming (cost/ownership-encoding `as_`/`to_`/`into_` prefixes), the `iter`/`iter_mut`/`into_iter` trio, getters named after the property (no `get_`) ([idiomatic API design](01-idiomatic-api-design.md)).
- Implement `From`/`TryFrom` (never `Into` directly); never panic in a `From` impl — use `TryFrom` if it can fail ([idiomatic API design](01-idiomatic-api-design.md)).
- Future-proof: keep struct fields private, mark types `#[non_exhaustive]`, give new trait methods default impls, and don't bound structs on derivable traits ([idiomatic API design](01-idiomatic-api-design.md), [tooling & hygiene](09-tooling-project-hygiene.md)).
- Decide `dyn`-vs-generic dispatch up front: generics/static dispatch for hot homogeneous paths, trait objects for heterogeneous collections and plugin-style registries ([idiomatic API design](01-idiomatic-api-design.md)).
- Seal traits meant to be *used* but not *implemented* downstream, so you can extend them without a breaking change ([idiomatic API design](01-idiomatic-api-design.md)).

### Ownership & borrowing
- Borrow first; reorder code so borrows end before the next mutation (NLL ends a borrow at its last use). Borrow disjoint struct fields directly; use `split_at_mut` for slices ([ownership & lifetimes](02-ownership-borrowing-lifetimes.md)).
- Prefer indices/ranges or an arena over self-referential structs; reserve `Pin` and crates like `ouroboros` for when an internal pointer is genuinely unavoidable ([ownership & lifetimes](02-ownership-borrowing-lifetimes.md)).
- Add lifetimes only when elision can't decide; prefer `'_` to keep them visible but light ([ownership & lifetimes](02-ownership-borrowing-lifetimes.md)).
- Clone deliberately, in order: borrow → restructure ownership → cheap `Arc`-clone → deep clone on a cold path ([ownership & lifetimes](02-ownership-borrowing-lifetimes.md), [anti-patterns](05-anti-patterns-footguns.md)).

### Error handling
- Default to `Result` + `?`; design your error type so the needed `From` conversions exist (that's what makes `?` "just work") ([error handling](03-error-handling.md)).
- Implement `std::error::Error` (`Debug + Display`, plus `Send + Sync + 'static`); expose causes via `source()`; lowercase, no-trailing-punctuation `Display` ([error handling](03-error-handling.md)).
- Choose error style by **intent**: typed enum (`thiserror`) when callers must branch on the failure; opaque `anyhow::Error` (or `Box<dyn Error>`) when they just report and give up ([error handling](03-error-handling.md)).
- Add context at boundaries, preserve `source`, and log only where an error is *handled* — not on every `?` hop ([error handling](03-error-handling.md)).

### Async
- Treat the async thread as a cooperative scheduler: keep work between `.await` points tiny, and move blocking/sync calls to `spawn_blocking` (and heavy CPU work to rayon + a channel) ([async Rust](04-async-rust.md)).
- Know the cancel-safe set and move accumulator state *out of the future into a struct field* so a cancelled-and-restarted future resumes; pin a future once and reuse `&mut` across a `select!` loop ([async Rust](04-async-rust.md)).
- Confine `!Send` values (`Rc`, guards) to a scope that ends before the next `.await` so the future stays `Send` and spawnable ([async Rust](04-async-rust.md), [anti-patterns](05-anti-patterns-footguns.md)).
- Prefer structured concurrency: `JoinSet` (aborts on drop) over detached `tokio::spawn`, and an explicit `CancellationToken` for graceful shutdown ([async Rust](04-async-rust.md)).

### Concurrency
- Trust auto-derivation of `Send`/`Sync`; share mutable state with `Arc<Mutex<T>>`, keep critical sections tiny, and use `.lock().unwrap()` to propagate poison ([concurrency](08-concurrency.md)).
- Prefer message passing (channels / the actor pattern) over shared mutable state; std `mpsc` for one consumer, `crossbeam` for MPMC + `select!` ([concurrency](08-concurrency.md), [anti-patterns](05-anti-patterns-footguns.md)).
- Use `thread::scope` (1.63+) to borrow stack data across threads without `Arc`/`'static`/clone; use atomics with `Relaxed` for plain counters and `Acquire`/`Release` to publish data behind a flag ([concurrency](08-concurrency.md)).
- Default to std locks (futex-backed since 1.62); adopt `parking_lot` deliberately for measured contention, fairness, downgrade, or the deadlock detector. Acquire multiple locks in one global order, or merge coupled data under one lock ([concurrency](08-concurrency.md)).

### Unsafe & FFI
- Treat every `unsafe` block as a contract: keep it tiny, isolate it in a dedicated module, wrap it in a safe API that can't be driven to UB, and attach an evidence-based `// SAFETY:` comment ([unsafe & FFI](06-unsafe-and-ffi.md)).
- Use `MaybeUninit` (never `mem::uninitialized`) for partial init; initialize through raw pointers and call `assume_init()` only after every byte is set on every path ([unsafe & FFI](06-unsafe-and-ffi.md)).
- Use strict-provenance APIs (`map_addr`/`with_addr`) for pointer tagging; generate FFI declarations with `bindgen`, wrap Rust callbacks in `catch_unwind`, and model thread-safety honestly (`!Send`/`!Sync` for non-thread-safe handles) ([unsafe & FFI](06-unsafe-and-ffi.md)).
- Run `cargo +nightly miri test` in CI for any crate with `unsafe`, plus ASan/Valgrind on the FFI boundary ([unsafe & FFI](06-unsafe-and-ffi.md)).

### Performance
- Measure first, always: profile (`samply`/flamegraph/DHAT) to find *where*, benchmark (Criterion) to confirm a change *helped*, and build with debug symbols for readable frames ([performance](07-performance-optimization.md)).
- Cut allocations — `Vec::with_capacity`, reuse buffers via `clear()`, `Cow` for usually-borrowed data — and default to iterators (zero-cost, no bounds checks) over hand-rolled index loops ([performance](07-performance-optimization.md)).
- Take the cheapest wins first: build flags (`lto`, `codegen-units = 1`, `panic = "abort"`, a faster linker, alternative allocator) before any code change — benchmarking each one at a time ([performance](07-performance-optimization.md)).
- Use `#[inline]` for its real job — cross-crate inlining of small public functions — reactively in apps; prefer LTO over scattering it everywhere ([performance](07-performance-optimization.md)).

### Tooling & supply chain
- Centralize versions/deps with workspace inheritance; keep features strictly additive; enable Clippy `pedantic` + `cargo` at the workspace level and prefer `#[expect]` over `#[allow]` ([tooling & hygiene](09-tooling-project-hygiene.md)).
- Declare and CI-verify an MSRV (resolver 3), commit and enforce `rustfmt.toml`, migrate to edition 2024 crate-by-crate with `cargo fix --edition`, and run `cargo-semver-checks` before every publish ([tooling & hygiene](09-tooling-project-hygiene.md)).
- Run a layered CI that denies warnings (`-D warnings`), uses nextest plus a `--doc` step, and tests multiple feature combinations — not just `--all-features` ([tooling & hygiene](09-tooling-project-hygiene.md)).
- Layer supply-chain defenses: `cargo audit --deny warnings` (PR + nightly), `cargo-deny` policy (ban wildcards/unknown sources), `cargo-vet` for positive human review, minimize surface with `cargo-machete`, sandbox untrusted builds, and enforce trusted publishing ([dependency & supply-chain security](10-dependency-supply-chain-security.md)).

---

## Avoid this (mistakes & footguns)

### Stringly-typed & sloppy modeling
- Passing `String`/`&str` (or bare `bool`/`i32`) where the domain has structure, then guarding with `if !valid { panic!() }` — that's representable-but-invalid state waiting to leak ([anti-patterns](05-anti-patterns-footguns.md), [idiomatic API design](01-idiomatic-api-design.md)).
- Relying on type *aliases* for safety — they give none of the newtype's type-checking benefits ([anti-patterns](05-anti-patterns-footguns.md)).
- Leaving newtype fields public, or blindly forwarding all inner-type behavior, defeating the encapsulation ([idiomatic API design](01-idiomatic-api-design.md)).
- Sentinel/half-initialized states (`-1` means missing, fill-fields-later) instead of `Option`/`Result` and full construction ([anti-patterns](05-anti-patterns-footguns.md)).

### Borrow-checker avoidance
- Scattering `.clone()` to silence the borrow checker — it hides an ownership-design question and can turn an O(1) borrow into an O(n) deep copy on a hot path ([ownership & lifetimes](02-ownership-borrowing-lifetimes.md), [anti-patterns](05-anti-patterns-footguns.md), [performance](07-performance-optimization.md)).
- Defaulting to `Rc<RefCell<T>>` for any tree/graph — it trades compile-time guarantees for runtime borrow panics, re-entrancy bugs, and cycle leaks; try arena + indices first ([ownership & lifetimes](02-ownership-borrowing-lifetimes.md), [anti-patterns](05-anti-patterns-footguns.md)).
- Adding explicit `<'a>` everywhere "to be safe," over-constraining signatures; or blindly applying the compiler's suggested lifetime fix, which guarantees compilation, not your intended contract ([ownership & lifetimes](02-ownership-borrowing-lifetimes.md)).
- Writing `unsafe` to escape an NLL precision gap (use a safe `bool`/index dance) or to silence the borrow checker generally — it is not a magical "stop complaining" switch ([ownership & lifetimes](02-ownership-borrowing-lifetimes.md), [anti-patterns](05-anti-patterns-footguns.md), [unsafe & FFI](06-unsafe-and-ffi.md)).

### Panic & error mishandling
- Using `unwrap`/`expect` as the default for I/O, parsing, env vars, or locks — each is a latent `panic!`; reserve them for true invariants and prefer `expect("reason")` ([error handling](03-error-handling.md), [anti-patterns](05-anti-patterns-footguns.md)).
- Using `panic!` for *expected* runtime conditions (bad input, network failure) — it removes the caller's agency ([error handling](03-error-handling.md)).
- Using `()` as an error type, or exposing `anyhow::Error`/`Box<dyn Error>` in a library API where callers need to branch ([error handling](03-error-handling.md)).
- "Ball of mud" error enums (one variant per call site), swallowing `source` when adding context, or logging on every `?` hop ([error handling](03-error-handling.md)).

### Async footguns
- Calling blocking/sync APIs (`std::fs`, `thread::sleep`, big CPU loops) inline in an `async fn`, starving every other task on the worker ([async Rust](04-async-rust.md)).
- Holding partial state in a future's locals across `.await` in a `select!` loop (silent data loss), putting non-cancel-safe ops in `select!` branches, or recreating a future each loop iteration ([async Rust](04-async-rust.md)).
- Holding a `MutexGuard` across `.await` — `!Send` won't compile, and a `Send` one deadlocks the scheduler ([async Rust](04-async-rust.md), [anti-patterns](05-anti-patterns-footguns.md), [concurrency](08-concurrency.md)).
- Fire-and-forget detached `tokio::spawn` (leaked, orphaned tasks); exposing a native `async fn` in a public trait when users need a `Send` bound or `dyn` dispatch ([async Rust](04-async-rust.md)).

### Concurrency footguns
- `unsafe impl Send`/`Sync` to silence a real cross-thread hazard you don't understand — it's a promise to the compiler, and getting it wrong is UB ([concurrency](08-concurrency.md)).
- Defaulting every shared value to `Arc<Mutex<T>>`; reaching for an async mutex to "fix" contention instead of sharding or message-passing ([anti-patterns](05-anti-patterns-footguns.md), [async Rust](04-async-rust.md)).
- `Relaxed` to publish data behind a flag (no happens-before edge); or `SeqCst` everywhere "to be safe," costing performance on weak hardware ([concurrency](08-concurrency.md)).
- Ignoring channel `send`/`recv` `Result`s, reentrant read-locking an `RwLock`, returning a `MutexGuard` from a function, or holding a lock across a callback — all deadlock vectors ([concurrency](08-concurrency.md)).
- Cargo-culting `parking_lot` "because it's faster" without benchmarking, then being surprised poisoning silently disappeared ([concurrency](08-concurrency.md)).

### Unsafe & FFI hazards
- Assuming `pub unsafe fn` absolves you — if a *safe* API you expose can be driven to UB with safe inputs, it's unsound regardless of the `unsafe` inside ([unsafe & FFI](06-unsafe-and-ffi.md)).
- `mem::uninitialized()`/`zeroed::<T>()` on non-zeroable types, `assume_init()` on a partially-initialized value (error paths!), or building a `&T`/`&mut T` to uninitialized memory ([unsafe & FFI](06-unsafe-and-ffi.md)).
- `ptr as usize ... as *mut T` round-trips that launder provenance; two `&mut` (or `&` + `&mut`) to the same memory; `transmute` to extend a lifetime or to coerce an out-of-range integer into an `enum`/`bool`/`char` ([unsafe & FFI](06-unsafe-and-ffi.md)).
- Letting a panic unwind across a plain `extern "C"` boundary; returning C++ `std::string`/`std::vector` by value across FFI; trusting "Miri is green" as proof of soundness ([unsafe & FFI](06-unsafe-and-ffi.md)).

### Performance anti-patterns
- Optimizing without data — guessing the hot spot and rewriting it into clever, unmaintainable code; profiling a debug build or stripped symbols ([performance](07-performance-optimization.md)).
- Hand-rolling index loops "for speed" (adds bounds checks and inhibits vectorization); reaching for `SmallVec`/arenas/`get_unchecked` speculatively ([performance](07-performance-optimization.md)).
- `#[inline]` everywhere (worse compile times, code bloat) or on generics (already implicitly inlinable); flipping all build knobs at once instead of one at a time; shipping `target-cpu=native` binaries to users ([performance](07-performance-optimization.md)).
- Integer-overflow assumptions: `a + b` panics in debug but silently wraps in release — be explicit with `checked_`/`saturating_`/`wrapping_` ([anti-patterns](05-anti-patterns-footguns.md)).

### Architecture & hygiene
- Deref polymorphism — `impl Deref` to fake inheritance — a surprising idiom with no real subtyping ([anti-patterns](05-anti-patterns-footguns.md)).
- Per-crate version drift instead of workspace inheritance; mutually-exclusive feature flags (features unify, so they break); feature-gating public items carelessly (a SemVer break) ([tooling & hygiene](09-tooling-project-hygiene.md)).
- Enabling Clippy `nursery`/`restriction` groups wholesale (false positives, contradictory lints); relying on nightly-only rustfmt options in a stable workflow; claiming an MSRV you don't CI-test ([tooling & hygiene](09-tooling-project-hygiene.md)).
- Silent SemVer breaks: adding a variant to a plain `enum`, a field to an all-public struct, an undefaulted trait method, or tightening a generic bound ([tooling & hygiene](09-tooling-project-hygiene.md)).

### Supply chain
- Assuming "it's Rust, it's safe" — the safety model covers UB, not malice; `build.rs` and proc-macros run arbitrary code at build time with your privileges ([dependency & supply-chain security](10-dependency-supply-chain-security.md)).
- Running `cargo build`/`test` on an untrusted repo on your main workstation with real secrets loaded; picking crates by download count alone (typosquats had thousands); copy-pasting dependency lines from a blog or LLM without verifying the exact crate ([dependency & supply-chain security](10-dependency-supply-chain-security.md)).
- Treating `cargo audit` as advisory (no `--deny warnings`) or local-only; allow-listing every license; keeping a long-lived `CARGO_REGISTRY_TOKEN` when trusted publishing is available ([dependency & supply-chain security](10-dependency-supply-chain-security.md)).

---

## Top 10 rules

1. **Make invalid states unrepresentable.** Newtypes + enums + private fields + "parse, don't validate" beat runtime checks. ([01](01-idiomatic-api-design.md), [05](05-anti-patterns-footguns.md))
2. **`Result` + `?` by default; `panic!`/`unwrap` only for true bugs.** Choose `thiserror` vs `anyhow` by whether the caller must branch. ([03](03-error-handling.md))
3. **Don't clone to silence the borrow checker.** Borrow → restructure → cheap `Arc`-clone → deep clone (cold path). ([02](02-ownership-borrowing-lifetimes.md), [05](05-anti-patterns-footguns.md))
4. **Never block the async executor, and never hold a guard across `.await`.** `spawn_blocking` for blocking work, rayon for CPU. ([04](04-async-rust.md), [05](05-anti-patterns-footguns.md))
5. **Prefer message passing over shared mutable state**; when you must share, `Arc<Mutex<T>>` with tiny critical sections. ([08](08-concurrency.md), [05](05-anti-patterns-footguns.md))
6. **Avoid `Rc<RefCell>` reflexes** — model ownership as a tree, use arena + indices for graphs. ([02](02-ownership-borrowing-lifetimes.md), [05](05-anti-patterns-footguns.md))
7. **`unsafe` is a proof obligation, not a permission slip.** Tiny blocks, safe wrappers, `// SAFETY:` comments, Miri in CI. ([06](06-unsafe-and-ffi.md))
8. **Measure before optimizing.** Profile, benchmark, change one thing; take free build-flag wins before touching code. ([07](07-performance-optimization.md))
9. **Default to iterators and trust zero-cost abstractions**; be explicit about integer-overflow intent. ([07](07-performance-optimization.md), [05](05-anti-patterns-footguns.md))
10. **Automate hygiene and supply-chain defense.** Workspace lints, MSRV, `cargo-semver-checks`, and layered `audit`/`deny`/`vet` in CI. ([09](09-tooling-project-hygiene.md), [10](10-dependency-supply-chain-security.md))
