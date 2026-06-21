---
type: pattern
title: "Tokio Runtime Playbook"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, tokio, async, runtime, ecosystem]
domain: "Ecosystem & Crate Playbooks"
difficulty: intermediate
related: ["[[The Tokio Runtime]]", "[[Async Rust]]", "[[Blocking in Async]]", "[[Tasks and spawn]]", "[[Ecosystem & Crate Playbooks]]"]
sources: ["[[tokio]]", "[[async-rust]]", "[[tooling-project-hygiene]]", "docs.rs/tokio"]
source_urls: ["https://docs.rs/tokio/latest/tokio/", "https://tokio.rs/", "https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html", "https://docs.rs/tokio/latest/tokio/runtime/"]
rust_version: "edition 2024 / 1.85+"
---

# Tokio Runtime Playbook

Use Tokio as the async runtime for networked Rust applications, but keep CPU work, blocking calls, and feature flags explicit.

## What it is
Tokio is the dominant runtime for async Rust applications.
It provides an executor, timers, async I/O, task spawning, synchronization primitives, and optional macros such as `#[tokio::main]`.
The runtime is not "async itself"; it is the scheduler that repeatedly polls futures until they make progress.
Tokio is a good default for servers, clients, background workers, and anything built around crates like [[Reqwest HTTP Client Playbook]] or [[Axum Web Service Playbook]].
It is not a substitute for a CPU work scheduler; for parallel CPU loops, prefer [[Rayon Data Parallelism Playbook]].

## How it works
Most binaries use `#[tokio::main]`, which creates a runtime and runs one async entry point.
Library crates should usually not create their own runtime; expose async functions and let the caller decide where they run.
Tokio tasks are lightweight futures scheduled on runtime worker threads.
They are cooperatively scheduled, so a task must reach `.await` points to let other tasks run.
Long blocking calls, synchronous filesystem calls in hot paths, or CPU-heavy loops can starve other tasks.
Use `tokio::task::spawn_blocking` for unavoidable blocking work.
For sustained CPU parallelism, hand the work to Rayon or a dedicated thread pool.

Tokio is heavily feature-gated.
For application prototypes, `features = ["full"]` is convenient.
For libraries and serious binaries, enable only the needed features such as `rt-multi-thread`, `macros`, `time`, `net`, `sync`, or `signal`.
Docs.rs should be checked for the latest feature list and crate version before changing `Cargo.toml`.

## Example
```rust
use std::time::Duration;

#[tokio::main]
async fn main() {
    let handle = tokio::spawn(async {
        tokio::time::sleep(Duration::from_millis(10)).await;
        21
    });

    let value = handle.await.expect("task should not panic");
    assert_eq!(value * 2, 42);
}
```

Cargo features for this example:
```toml
[dependencies]
tokio = { version = "1", features = ["rt-multi-thread", "macros", "time"] }
```

## Best practice
- ✅ Put the runtime at the binary boundary, not deep inside library code.
- ✅ Use `JoinHandle` results; task panics and cancellations are observable.
- ✅ Use `spawn_blocking` for blocking adapters and isolate sustained CPU work elsewhere.
- ✅ Prefer cancellation-aware loops with `select!`, timeouts, and graceful shutdown channels.
- ✅ Keep Tokio feature flags narrow in libraries.
- ✅ Use `#[tokio::test]` for async tests that need the runtime.
- ✅ Instrument task boundaries with [[Tracing and Structured Logging Playbook]].
- ✅ Read docs.rs and verify the latest Tokio version before relying on a feature.

## Pitfalls
- ⚠️ Calling blocking code inside async tasks; see [[Blocking the Async Executor]].
- ⚠️ Holding a `std::sync::MutexGuard` across `.await`; see [[Holding Locks Across Await]].
- ⚠️ Spawning fire-and-forget tasks without shutdown or error handling; see [[Fire-and-Forget Tokio Tasks]].
- ⚠️ Creating nested runtimes from inside async code.
- ⚠️ Using `features = ["full"]` in a reusable library without considering dependency surface.
- ⚠️ Treating `.await` as parallelism; it is suspension, not automatic CPU distribution.
- ⚠️ Assuming cancellation runs destructors at a business-logic boundary unless your future is cancellation-safe.

## See also
[[Ecosystem & Crate Playbooks]] · [[The Tokio Runtime]] · [[Async Rust]] · [[Futures]] · [[Tasks and spawn]] · [[Blocking in Async]] · [[Blocking the Async Executor]] · [[Cancellation Safety]] · [[Shared State in Async]] · [[Structured Task Sets with JoinSet]] · [[Reqwest HTTP Client Playbook]] · [[Axum Web Service Playbook]]

## Sources
- Tokio crate docs — https://docs.rs/tokio/latest/tokio/; verify the latest version before editing `Cargo.toml`.
- Tokio runtime module docs — https://docs.rs/tokio/latest/tokio/runtime/
- Tokio `spawn_blocking` docs — https://docs.rs/tokio/latest/tokio/task/fn.spawn_blocking.html
- Existing source notes — [[tokio]], [[async-rust]], [[tooling-project-hygiene]].
