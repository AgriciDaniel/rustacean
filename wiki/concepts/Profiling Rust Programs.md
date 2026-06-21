---
type: concept
title: "Profiling Rust Programs"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, performance, profiling, optimization]
domain: "Performance & Optimization"
difficulty: intermediate
related: ["[[Benchmarking with Criterion]]", "[[Reducing Heap Allocations]]", "[[Bounds-Check Elimination]]", "[[LTO and codegen-units]]", "[[Avoiding Premature Optimization]]", "[[Performance & Optimization]]"]
sources: ["[[the-book]]", "[[cargo-book]]", "[[rustc-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch14-01-release-profiles.html", "https://doc.rust-lang.org/cargo/reference/profiles.html", "https://doc.rust-lang.org/rustc/codegen-options/index.html"]
rust_version: "edition 2024 / 1.85+"
---

# Profiling Rust Programs

Profiling is the measurement step that tells you where a Rust program spends time, allocates memory, or waits on the system; it should precede almost every optimization.

## What it is
Profiling answers a different question from benchmarking. A benchmark says "this operation takes about this long"; a profiler says "the time is mostly in these call paths."
For Rust, the normal workflow is to profile an optimized binary, keep enough debug information for readable symbols, and then make the smallest change that attacks the measured hot path.
This matters because Rust code often looks higher-level than the machine code it becomes.
Iterator chains, generics, and small wrappers may compile away, while allocation, formatting, hash table behavior, cache misses, or syscalls dominate.

The usual profiler families are sampling CPU profilers, allocation profilers, and hardware-counter tools.
Sampling profilers are the first stop for CPU time because they interrupt the program and record stacks without instrumenting every function.
Allocation profilers are the first stop when a program is allocating unexpectedly or spending time in allocator routines.
Hardware counters become useful when the question is about cache misses, branch behavior, or instruction counts.

## How it works
Build configuration changes the quality of profiling data.
Debug builds are easy to read but are not representative of shipped performance.
Release builds are representative but can be hard to read if debug symbols are omitted or stripped.
A dedicated profiling profile often gives the best tradeoff: inherit release optimizations, keep debug symbols, and avoid stripping names.
Cargo profiles control both optimizer behavior and the metadata a profiler can use.
`debug = true` or a line-table debug setting gives stack frames and source locations; `strip = false` keeps names available to external tools.
Those settings do not make the code "debug mode" if the profile inherits from `release`; the optimizer still runs according to the inherited `opt-level`, `lto`, and `codegen-units`.

Use profiling results as a map, not a verdict.
Inlining can move cost from a helper into its caller.
Generic monomorphization can create several copies of similar code.
Allocator cost can appear under generic collection operations.
Read the call tree and the source together, then confirm any candidate fix with a benchmark.
If a hot function disappears from the profile, it may have been inlined into callers rather than optimized away.
If a single standard-library function dominates, inspect the call path before replacing it; `String` formatting, hashing, sorting, and allocation are often symptoms of a higher-level data-flow choice.
For wall-clock stalls, pair CPU profiling with I/O, lock, or allocation profiling so a blocked program is not misread as an efficient one.

## Example
```rust
use std::hint::black_box;

fn checksum(bytes: &[u8]) -> u64 {
    bytes.iter().map(|&b| u64::from(b)).sum()
}

fn main() {
    let data = vec![42_u8; 8 * 1024 * 1024];
    let mut total = 0_u64;

    for _ in 0..200 {
        total = total.wrapping_add(checksum(black_box(&data)));
    }

    println!("{total}");
}
```

Profile this kind of workload as an optimized binary, not with `cargo run` defaults.
For a Cargo project, a profiling profile can be configured in `Cargo.toml`:

```toml
[profile.profiling]
inherits = "release"
debug = true
strip = false
```

Then run the profiler against the resulting optimized target.
The exact profiler is platform-specific, but the Rust-side rule is stable: measure optimized code with readable symbols.

## Worked example: profiling allocation churn
```rust
fn render_labels(ids: &[u32]) -> Vec<String> {
    ids.iter().map(|id| format!("item-{id:08}")).collect()
}

fn main() {
    let ids: Vec<u32> = (0..50_000).collect();
    let labels = render_labels(&ids);
    assert_eq!(labels[0], "item-00000000");
    assert_eq!(labels.len(), ids.len());
}
```

A CPU profile may show time under formatting and allocator functions, but that does not automatically mean `format!` is the bug.
The useful question is whether the program really needs to allocate one `String` per label.
If labels are immediately written to a socket or file, reuse a scratch `String` and stream them.
If labels are stored long-term, the allocation may be the correct cost and the benchmark should compare alternative representations, not just a hand-written formatter.

## Common errors
Profiling often fails for workflow reasons rather than Rust language errors.

```text
error: profile `profiling` is not defined
```

This happens when running `cargo build --profile profiling` before adding `[profile.profiling]` to the workspace root `Cargo.toml`.
Cargo only reads profile settings from the root manifest of a workspace; dependency manifests do not get to override the final build profile.

```text
perf: failed to mmap with 1 (Operation not permitted)
```

On Linux this is an operating-system permission issue, not a Rust problem.
Use a profiler that works under the current permissions, adjust system profiling settings, or run inside an environment where sampling is allowed.
Do not compensate by profiling an unoptimized debug build just because it is easier to launch.

## Best practice
- ✅ Start with a release-like build so the optimizer, monomorphization, inlining, and bounds-check elimination resemble production.
- ✅ Keep debug symbols for profiling sessions; readable function names are worth the larger binary.
- ✅ Use profiling to choose the next experiment, then use [[Benchmarking with Criterion]] or another benchmark to confirm the change.
- ✅ Look for allocation-heavy call paths before rewriting algorithms; see [[Reducing Heap Allocations]].
- ✅ Record the command, input data, build profile, and machine details so future profiles are comparable.
- ✅ Profile with representative inputs; a tiny synthetic input can make setup, parsing, or cold branches look hotter than the real workload.
- ✅ Separate CPU, allocation, and blocking questions; one tool rarely answers all three cleanly.
- ✅ Keep one known-good baseline profile before changing code so regressions can be compared visually and numerically.

## Pitfalls
- ⚠️ Profiling an unoptimized debug build can send you after costs the release optimizer removes.
- ⚠️ Stripping symbols before profiling turns useful stack traces into addresses and mangled names.
- ⚠️ Treating a profiler sample as exact accounting ignores sampling noise and optimizer movement across call boundaries.
- ⚠️ Rewriting code from intuition before profiling is [[Avoiding Premature Optimization]] in reverse: the tool should identify the hot path first.
- ⚠️ Changing `#[inline]`, LTO, allocation strategy, and algorithms all at once makes it impossible to know which change helped.
- ⚠️ Reading inlined stacks as source-level call counts can be misleading; inlining changes where samples are charged.
- ⚠️ Profiling a workload that spends most time waiting on I/O with only a CPU sampler can make the program appear idle rather than blocked.

## See also
[[Benchmarking with Criterion]] · [[Reducing Heap Allocations]] · [[Iterator Performance]] · [[Bounds-Check Elimination]] · [[The inline Attribute]] · [[LTO and codegen-units]] · [[Avoiding Premature Optimization]] · [[Speculative Micro-Optimization]] · [[Profiles and Optimization Settings]] · [[Codegen and Optimization Flags]] · [[Performance & Optimization]]

## Sources
- The Rust Programming Language, ch. 14.1 "Customizing Builds with Release Profiles" — [[the-book]],
  https://doc.rust-lang.org/book/ch14-01-release-profiles.html
- The Cargo Book, "Profiles" — [[cargo-book]],
  https://doc.rust-lang.org/cargo/reference/profiles.html
- The rustc Book, "Codegen options" — [[rustc-book]],
  https://doc.rust-lang.org/rustc/codegen-options/index.html
