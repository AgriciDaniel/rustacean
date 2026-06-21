---
type: pattern
title: "Rayon Data Parallelism Playbook"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, rayon, parallelism, performance, ecosystem]
domain: "Ecosystem & Crate Playbooks"
difficulty: intermediate
related: ["[[Concurrency]]", "[[Iterator Performance]]", "[[Threads]]", "[[Tokio Runtime Playbook]]", "[[Ecosystem & Crate Playbooks]]"]
sources: ["[[performance-optimization]]", "[[concurrency]]", "[[tooling-project-hygiene]]", "docs.rs/rayon"]
source_urls: ["https://docs.rs/rayon/latest/rayon/", "https://docs.rs/rayon/latest/rayon/iter/trait.ParallelIterator.html", "https://docs.rs/rayon/latest/rayon/iter/trait.IntoParallelIterator.html", "https://docs.rs/rayon/latest/rayon/struct.ThreadPoolBuilder.html"]
rust_version: "edition 2024 / 1.85+"
---

# Rayon Data Parallelism Playbook

Use Rayon for CPU-bound data parallelism when independent work can be split across threads and joined without shared mutable bottlenecks.

## What it is
Rayon is the standard Rust ecosystem crate for ergonomic data parallelism.
It turns ordinary iterator-shaped work into parallel work with `par_iter`, `into_par_iter`, `map`, `filter`, `sum`, `collect`, and other familiar adapters.
It is best for CPU-bound workloads over collections, ranges, trees, and divide-and-conquer algorithms.
It complements [[Tokio Runtime Playbook]]: Tokio schedules async I/O tasks, while Rayon burns CPU cores efficiently.
Rayon is not magic acceleration; it pays off when work per item is large enough to amortize scheduling and synchronization.

## How it works
Rayon uses a work-stealing thread pool.
Parallel iterators split work into chunks, execute chunks across worker threads, and combine results.
Closures used by Rayon must satisfy thread-safety bounds such as `Send` and `Sync` where required.
This keeps data races out while still allowing shared immutable reads and safe reductions.
Prefer reductions such as `sum`, `reduce`, `fold`, or `collect` over locking a shared accumulator.
For custom environments, `ThreadPoolBuilder` can configure the pool.
In async services, do not run large Rayon jobs casually on request paths without considering CPU saturation and latency.
Verify the latest Rayon version on docs.rs before editing `Cargo.toml`.

## Example
```rust
use rayon::prelude::*;

fn expensive_score(n: u64) -> u64 {
    (1..=n).map(|x| x * x).sum()
}

fn main() {
    let inputs = vec![10, 20, 30, 40];
    let scores: Vec<u64> = inputs
        .par_iter()
        .map(|&n| expensive_score(n))
        .collect();

    assert_eq!(scores.len(), 4);
    assert!(scores[3] > scores[0]);
}
```

Cargo dependency for this example:
```toml
[dependencies]
rayon = "1"
```

## Best practice
- ✅ Use Rayon for CPU-heavy, independent work over collections or ranges.
- ✅ Start with sequential iterators, measure, then change to parallel iterators where the work is coarse enough.
- ✅ Prefer pure functions and reductions over shared mutable state.
- ✅ Keep captured data `Send + Sync` by design instead of fighting compiler errors late.
- ✅ Use custom pools when embedding Rayon into larger schedulers with strict resource budgets.
- ✅ Benchmark with [[Benchmarking with Criterion]] because small workloads may slow down.
- ✅ Keep Rayon out of public APIs unless parallelism is part of the contract.
- ✅ Verify the latest Rayon version on docs.rs before updating examples or dependency versions.

## Pitfalls
- ⚠️ Parallelizing tiny operations where overhead dominates.
- ⚠️ Using a `Mutex` around every update and serializing the hot path; see [[Premature Arc Mutex]].
- ⚠️ Mixing Rayon and async request handling without a CPU budget.
- ⚠️ Assuming output order for adapters that do not promise the order you need.
- ⚠️ Capturing `Rc`, `RefCell`, or other non-thread-safe state and then fighting `Send`/`Sync`.
- ⚠️ Optimizing by instinct instead of measuring; see [[Speculative Micro-Optimization]].
- ⚠️ Using Rayon for I/O-bound concurrency that belongs in async or threads.

## See also
[[Ecosystem & Crate Playbooks]] · [[Concurrency]] · [[Threads]] · [[Iterator Performance]] · [[Iterator Adapters]] · [[Benchmarking with Criterion]] · [[Speculative Micro-Optimization]] · [[Premature Arc Mutex]] · [[Tokio Runtime Playbook]] · [[Send and Sync]] · [[Choosing the Right Rust Crate]]

## Sources
- Rayon crate docs — https://docs.rs/rayon/latest/rayon/; verify the latest version before editing `Cargo.toml`.
- Rayon `ParallelIterator` docs — https://docs.rs/rayon/latest/rayon/iter/trait.ParallelIterator.html
- Rayon `ThreadPoolBuilder` docs — https://docs.rs/rayon/latest/rayon/struct.ThreadPoolBuilder.html
- Existing source notes — [[performance-optimization]], [[concurrency]], [[tooling-project-hygiene]].
