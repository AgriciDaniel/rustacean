---
type: pattern
title: "Flamegraph and perf Workflow"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, performance, profiling, perf, flamegraph]
domain: "Performance & Optimization"
difficulty: intermediate
related: ["[[Profiling Rust Programs]]", "[[Benchmarking with Criterion]]", "[[Codegen and Optimization Flags]]", "[[Profiles and Optimization Settings]]", "[[Avoiding Premature Optimization]]", "[[Performance & Optimization]]"]
sources: ["[[07-performance-optimization]]", "[[rust-performance-book]]", "[[cargo-book]]"]
source_urls: ["https://nnethercote.github.io/perf-book/profiling.html", "https://doc.rust-lang.org/cargo/reference/profiles.html", "https://docs.rs/flamegraph/latest/flamegraph/", "https://perfwiki.github.io/main/"]
rust_version: "edition 2024 / 1.85+"
---

# Flamegraph and perf Workflow

A flamegraph workflow profiles an optimized Rust binary, keeps symbols readable, finds wide hot call paths, changes one thing, then re-benchmarks to confirm the improvement.

## What it is
`perf` is the Linux profiler used to sample CPU activity, collect call stacks, and inspect hardware counters.
`cargo flamegraph` and the `flamegraph` crate wrap platform profilers and turn sampled stacks into an interactive SVG.
The useful mental model is visual: a wider frame represents more samples in that call path.
Wide does not always mean "bad"; it means "worth understanding first."

This is a pattern because the tool matters less than the loop.
Build release-like code.
Profile representative input.
Read the hot path.
Make the smallest plausible change.
Validate with [[Benchmarking with Criterion]] or an application-level benchmark.
Repeat only if the next profile still points at the same problem.

The workflow complements [[Profiling Rust Programs]].
Profiling answers where time is going.
Benchmarks answer whether a specific change improved the case you care about.
Skipping either side turns optimization into guesswork.

## How it works
For Rust, the first build mistake is profiling debug code.
Debug builds preserve source structure but do not represent shipped performance.
The second build mistake is stripping all useful symbols.
A dedicated Cargo profile can inherit release optimizations while keeping debug information:

```toml
[profile.profiling]
inherits = "release"
debug = true
strip = false
```

With that profile in place, build or run the target through the profiler.
For `cargo flamegraph`, a common shape is:

```text
cargo flamegraph --profile profiling --bin my-app -- workload-arg
```

On Linux, `perf` can be used directly when you need lower-level control:

```text
cargo build --profile profiling --bin my-app
perf record --call-graph dwarf target/profiling/my-app workload-arg
perf report
```

Exact permissions and command flags vary by Linux distribution and kernel settings.
Treat that as environment setup, not as a reason to profile an unoptimized build.
When using third-party crates such as `flamegraph`, cite docs.rs and verify the latest crate version before pinning or copying command options.

## Example
```rust
use std::hint::black_box;

fn checksum(bytes: &[u8]) -> u64 {
    bytes.iter().map(|&byte| u64::from(byte)).sum()
}

fn main() {
    let data = vec![7_u8; 4 * 1024 * 1024];
    let mut total = 0_u64;

    for _ in 0..250 {
        total = total.wrapping_add(checksum(black_box(&data)));
    }

    println!("{total}");
}
```

This program is intentionally boring: it creates a stable CPU workload that can be profiled as a release-like binary.
In real code, keep the input representative rather than making a toy workload just because it is convenient.
The `black_box` call prevents the optimizer from deleting work that exists only for the measurement example.

## Reading the graph
Start with the widest frames near the top of the stack.
If a hot frame is your function, inspect its caller and inputs before editing the function body.
If a hot frame is allocation, formatting, hashing, sorting, locking, or I/O, inspect the call path that led there.
The fix might be in data flow rather than in the library routine.

Inlining changes how samples are attributed.
A helper may disappear because its cost was charged to the caller.
Generic code may appear in several monomorphized copies.
That is normal in Rust.
Use names, source paths, and benchmark results together instead of reading a flamegraph as exact source-level accounting.

## Best practice
- ✅ Profile release-like code with debug symbols, not default debug builds.
- ✅ Use a representative command line, input data set, feature set, and target CPU baseline.
- ✅ Keep the profiling command in notes or a commit message so later measurements are comparable.
- ✅ Follow a flamegraph with [[Benchmarking with Criterion]] or a real workload benchmark before declaring victory.
- ✅ Investigate allocation-heavy stacks with [[Reducing Heap Allocations]] and, when needed, allocation-specific tools.
- ✅ Change one variable at a time: source code, `lto`, allocator, target features, and input shape should not all move together.
- ✅ Treat profiler setup errors as setup errors; fix permissions or choose another profiler before changing the workload.
- ✅ Use direct `perf` when you need counters or advanced Linux views beyond an SVG.

## Pitfalls
- ⚠️ Profiling a debug build often highlights work the optimizer would remove or reshape.
- ⚠️ Stripping symbols before profiling can turn a useful trace into anonymous addresses.
- ⚠️ Assuming the widest frame is the fix location ignores callers, input shape, and inlining.
- ⚠️ Comparing flamegraphs from different inputs, CPUs, or feature flags can explain noise rather than regressions.
- ⚠️ Rewriting code before profiling is [[Avoiding Premature Optimization]].
- ⚠️ Taking a single profile as proof ignores sampling variation and scheduler noise.
- ⚠️ Optimizing only a microbenchmark after the application flamegraph points elsewhere is [[Speculative Micro-Optimization]].

## See also
[[Profiling Rust Programs]] · [[Benchmarking with Criterion]] · [[Reducing Heap Allocations]] · [[Iterator Performance]] · [[Bounds-Check Elimination]] · [[LTO and codegen-units]] · [[Codegen and Optimization Flags]] · [[Profiles and Optimization Settings]] · [[Avoiding Premature Optimization]] · [[Speculative Micro-Optimization]] · [[Performance & Optimization]]

## Sources
- Rust Performance Book, "Profiling" — [[rust-performance-book]],
  https://nnethercote.github.io/perf-book/profiling.html
- The Cargo Book, "Profiles" — [[cargo-book]],
  https://doc.rust-lang.org/cargo/reference/profiles.html
- `flamegraph` crate documentation, verify latest version before pinning,
  https://docs.rs/flamegraph/latest/flamegraph/
- Linux perf wiki,
  https://perfwiki.github.io/main/
- Verified research pack, "Performance & Optimization" — [[07-performance-optimization]]
