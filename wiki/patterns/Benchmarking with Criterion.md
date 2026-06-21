---
type: pattern
title: "Benchmarking with Criterion"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, performance, benchmarking, criterion]
domain: "Performance & Optimization"
difficulty: intermediate
related: ["[[Profiling Rust Programs]]", "[[Avoiding Premature Optimization]]", "[[Iterator Performance]]", "[[Reducing Heap Allocations]]", "[[Bounds-Check Elimination]]", "[[Profiles and Optimization Settings]]", "[[Performance & Optimization]]"]
sources: ["[[the-book]]", "[[cargo-book]]"]
source_urls: ["https://doc.rust-lang.org/cargo/commands/cargo-bench.html", "https://doc.rust-lang.org/std/hint/fn.black_box.html", "https://doc.rust-lang.org/book/ch11-01-writing-tests.html"]
rust_version: "edition 2024 / 1.85+"
---

# Benchmarking with Criterion

Benchmarking with Criterion means measuring a focused operation repeatedly with statistical analysis, then using the result to validate or reject a performance change.

## What it is
Criterion is the common stable Rust benchmarking crate used when the built-in nightly benchmark harness is not appropriate.
It runs benchmark functions repeatedly, estimates variance, detects outliers, and reports whether a change is likely meaningful.
Use it for microbenchmarks and small integration benchmarks where you can isolate the operation under test.

Benchmarking is not profiling.
A benchmark tells you whether `parse_fast` is faster than `parse_simple` on selected inputs.
A profiler tells you whether parsing is actually where the program spends time.
Good optimization work usually uses both: profile to pick the target, benchmark to confirm the change.

## How it works
Criterion benchmarks live under `benches/`.
A Cargo project normally adds Criterion as a dev-dependency and disables the default libtest harness for the benchmark target.
Inside the benchmark, `std::hint::black_box` prevents the optimizer from deleting the work because the result is unused.
Current Rust provides `std::hint::black_box`, so prefer it over Criterion's older compatibility helper.
`black_box` is an optimization barrier, not a magic realism switch: it can stop constant folding or dead-code elimination around a value, but it cannot make an unrealistic benchmark representative.

Choose benchmark inputs deliberately.
Use tiny, medium, and large cases if the algorithm has different scaling behavior.
Keep setup outside the timed closure unless setup is part of what you want to measure.
Benchmark one change at a time, or the numbers cannot explain which change mattered.
Criterion first warms up the benchmark, then collects repeated samples and estimates variance.
That makes it better than timing a single call with `Instant`, but it also means the benchmark body must be deterministic enough that the measured distribution answers your question.
If each iteration reads from disk, grabs a contended lock, or depends on network timing, the benchmark may be measuring the environment more than the Rust code.

## Example
```rust
use criterion::{criterion_group, criterion_main, Criterion};
use std::hint::black_box;

fn count_ascii_digits(bytes: &[u8]) -> usize {
    bytes.iter().filter(|b| b.is_ascii_digit()).count()
}

fn bench_count_digits(c: &mut Criterion) {
    let input = b"order-2026-06-21: 144 items";
    c.bench_function("count_ascii_digits", |b| {
        b.iter(|| count_ascii_digits(black_box(input)))
    });
}

criterion_group!(benches, bench_count_digits);
criterion_main!(benches);
```

For this file to compile as `benches/count_digits.rs`, the crate needs a Criterion dev-dependency and a benchmark target configuration in `Cargo.toml`.
The important Rust-side details are that the operation is small, the input is stable, and the benchmark consumes the result through `black_box`.

## Worked example: separating setup from the timed body
```rust
use criterion::{criterion_group, criterion_main, BenchmarkId, Criterion};
use std::hint::black_box;

fn sum_sorted(mut values: Vec<u64>) -> u64 {
    values.sort_unstable();
    values.iter().sum()
}

fn bench_sum_sorted(c: &mut Criterion) {
    let mut group = c.benchmark_group("sum_sorted");

    for len in [64_usize, 4096] {
        let input: Vec<u64> = (0..len as u64).rev().collect();
        group.bench_with_input(BenchmarkId::from_parameter(len), &input, |b, input| {
            b.iter(|| sum_sorted(black_box(input.clone())))
        });
    }

    group.finish();
}

criterion_group!(benches, bench_sum_sorted);
criterion_main!(benches);
```

Here the benchmark intentionally includes the clone because `sum_sorted` takes ownership and mutates its input.
If you wanted to measure only sorting an already allocated buffer, use Criterion's batched iteration APIs so setup is controlled separately.
The benchmark name includes the input size, which makes scaling changes visible in reports.

## Common errors
Criterion benchmarks need their own harness when using `criterion_main!`.

```text
error[E0601]: `main` function not found in crate
```

This often means the benchmark target was compiled with the default test harness disabled incorrectly, or `criterion_main!(...)` is missing from the file.
The usual `Cargo.toml` shape is:

```toml
[[bench]]
name = "count_digits"
harness = false
```

Another common failure is measuring a value the optimizer can compute at compile time.
If a benchmark reports implausibly tiny times, pass realistic inputs through `std::hint::black_box` and inspect whether the result is used.

## Best practice
- ✅ Benchmark optimized code through `cargo bench`, not debug builds.
- ✅ Keep setup outside the measured closure unless setup cost is the subject of the benchmark.
- ✅ Use `black_box` for inputs or results that the optimizer might otherwise remove.
- ✅ Run representative inputs, not only the smallest happy path.
- ✅ Pair benchmark results with [[Profiling Rust Programs]] before making broad code changes.
- ✅ Use benchmark groups and `BenchmarkId` when comparing sizes, algorithms, or configuration choices.
- ✅ Pin relevant environment details in notes or commit messages: CPU, Rust version, target, feature flags, and profile.
- ✅ Benchmark error paths separately when they allocate, format, or branch differently from the success path.

## Pitfalls
- ⚠️ A microbenchmark can improve while the real application is unchanged because the measured function is not hot.
- ⚠️ Benchmarking code that allocates during setup inside the timed loop can hide the cost you meant to measure.
- ⚠️ Comparing one run before and after a change ignores noise; use Criterion's repeated measurements.
- ⚠️ Changing build flags and code together confuses the result; see [[LTO and codegen-units]] for build changes.
- ⚠️ Tuning code until one benchmark improves can become [[Speculative Micro-Optimization]].
- ⚠️ Putting random input generation inside `b.iter` can measure the generator more than the function.
- ⚠️ Treating microbenchmark wins as product wins skips the profiling step that proves the code is hot.

## See also
[[Profiling Rust Programs]] · [[Avoiding Premature Optimization]] · [[Iterator Performance]] · [[Reducing Heap Allocations]] · [[Bounds-Check Elimination]] · [[Profiles and Optimization Settings]] · [[Codegen and Optimization Flags]] · [[The inline Attribute]] · [[LTO and codegen-units]] · [[Performance & Optimization]]

## Sources
- The Cargo Book, "`cargo bench`" — [[cargo-book]],
  https://doc.rust-lang.org/cargo/commands/cargo-bench.html
- Rust standard library, `std::hint::black_box` — [[the-book]],
  https://doc.rust-lang.org/std/hint/fn.black_box.html
- The Rust Programming Language, ch. 11.1 "Writing Tests" — [[the-book]],
  https://doc.rust-lang.org/book/ch11-01-writing-tests.html
- Criterion.rs crate documentation,
  https://docs.rs/criterion/latest/criterion/
