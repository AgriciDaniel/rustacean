# Rust Deep-Research Index

A deep-research corpus on writing correct, idiomatic, high-quality Rust, targeting **stable Rust ~1.85+ on edition 2024** (current as of June 2026). Each report pairs the **good practice** with the **mistake to avoid** on every major point, is adversarially fact-checked, and carries its own cited `## Sources` section.

Start with the [**Rust Mastery synthesis**](99-rust-mastery-synthesis.md) for the cross-cutting do/avoid view, then drill into any topic below.

## Reports

| # | Title | Report | One-line description |
|---|-------|--------|----------------------|
| 01 | Idiomatic Rust & API Design | [01-idiomatic-api-design.md](01-idiomatic-api-design.md) | Naming, newtypes, builders, conversions, sealed traits, dispatch, and making invalid states unrepresentable. |
| 02 | Ownership, Borrowing & Lifetimes — Pitfalls | [02-ownership-borrowing-lifetimes.md](02-ownership-borrowing-lifetimes.md) | Lifetime mental model, elision, classic borrow-checker fights, NLL/Polonius, self-referential structs, clone-vs-restructure. |
| 03 | Error Handling — Current Consensus | [03-error-handling.md](03-error-handling.md) | `Result`/`?`, panic-vs-`Result`, the `Error` trait, `thiserror`/`anyhow`, `Box<dyn Error>`, and error context. |
| 04 | Async Rust — Best Practices & Pitfalls | [04-async-rust.md](04-async-rust.md) | Never blocking the executor, `spawn_blocking`, cancellation safety, `select!`, `Send` bounds, async traits, structured concurrency. |
| 05 | Anti-Patterns & Footguns | [05-anti-patterns-footguns.md](05-anti-patterns-footguns.md) | `unwrap` overuse, needless `clone`, `Rc<RefCell>`, stringly-typed code, premature `Arc<Mutex>`, deref polymorphism, integer overflow. |
| 06 | Unsafe Rust & FFI — Soundness | [06-unsafe-and-ffi.md](06-unsafe-and-ffi.md) | The unsafe contract, UB categories, provenance, `MaybeUninit`, C FFI as a trust boundary, and Miri. |
| 07 | Performance & Optimization | [07-performance-optimization.md](07-performance-optimization.md) | Profile-first, the toolchain, cutting allocations, `SmallVec`/arenas, iterators, `#[inline]` myths, build config (LTO et al.). |
| 08 | Concurrency — Send/Sync & Shared State | [08-concurrency.md](08-concurrency.md) | `Send`/`Sync`, `Arc<Mutex>`, `RwLock`, channels, std-vs-crossbeam-vs-parking_lot, scoped threads, atomics, deadlock avoidance. |
| 09 | Tooling & Project Hygiene | [09-tooling-project-hygiene.md](09-tooling-project-hygiene.md) | Workspaces, feature flags, Clippy, rustfmt, MSRV, edition-2024 migration, CI, nextest, doctests, SemVer discipline. |
| 10 | Dependency & Supply-Chain Security | [10-dependency-supply-chain-security.md](10-dependency-supply-chain-security.md) | Threat model, `cargo-audit`/`-deny`/`-vet`, minimizing surface, typosquatting, `build.rs` trust, trusted publishing, reproducible builds. |

## Cross-cutting

- [99-rust-mastery-synthesis.md](99-rust-mastery-synthesis.md) — **Rust Mastery synthesis**: every report distilled into a "Do this" / "Avoid this" pairing plus a Top-10 cheat-sheet.
- [sources.md](sources.md) — **Consolidated sources**: 177 unique URLs from all ten reports, deduplicated and grouped by domain.
