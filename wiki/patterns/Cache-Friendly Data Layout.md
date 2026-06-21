---
type: pattern
title: "Cache-Friendly Data Layout"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, performance, cache, layout, memory]
domain: "Performance & Optimization"
difficulty: advanced
related: ["[[Type Layout and repr]]", "[[Vec]]", "[[The Slice Type]]", "[[Iterator Performance]]", "[[SIMD and target_feature]]", "[[Performance & Optimization]]"]
sources: ["[[07-performance-optimization]]", "[[rust-performance-book]]", "[[the-reference]]", "[[std]]"]
source_urls: ["https://nnethercote.github.io/perf-book/type-sizes.html", "https://nnethercote.github.io/perf-book/heap-allocations.html", "https://doc.rust-lang.org/reference/type-layout.html#representations", "https://doc.rust-lang.org/std/vec/struct.Vec.html", "https://doc.rust-lang.org/std/mem/fn.size_of.html", "https://doc.rust-lang.org/std/mem/macro.offset_of.html"]
rust_version: "edition 2024 / 1.85+"
---

# Cache-Friendly Data Layout

Cache-friendly data layout keeps hot data contiguous, compact, and traversed predictably so the CPU spends less time waiting for memory.

## What it is
Rust makes memory ownership explicit, but it does not automatically make every data structure cache-friendly.
A `Vec<T>` is contiguous.
A linked structure of `Box<T>` values is not.
A large struct may mix fields used in a hot loop with fields needed only for logging or error reporting.
That can waste cache bandwidth even when the algorithm is correct and allocation count is low.

Cache-friendly layout is a pattern for performance-sensitive data.
Keep hot fields close together.
Prefer contiguous storage.
Separate cold metadata from hot numeric state.
Traverse in storage order when possible.
Measure with profiling and benchmarks before adding layout complexity.

This is related to, but not the same as, `#[repr(...)]`.
[[Type Layout and repr]] describes language layout guarantees.
Cache-friendly layout is usually an API and data-structure decision.
Most of the time, the right tool is `Vec`, slices, field grouping, or a structure-of-arrays design, not a representation attribute.

## How it works
Modern CPUs fetch memory in cache lines.
If a loop touches adjacent values in a slice, one memory fetch can feed several iterations.
If a loop follows pointers to scattered heap objects, each step can miss cache and stall.
If each element carries cold fields, the hot loop drags unused bytes through the cache.

Two common layouts are array of structs and structure of arrays.
Array of structs is ergonomic when each operation needs most fields of one object.
Structure of arrays is often faster when a hot loop needs the same few fields for many objects.
Rust can express either layout safely.
The ownership question is which type owns the storage and which APIs expose slices or indexed access.

Field order can affect size because padding is inserted to satisfy alignment.
The default Rust representation does not promise a stable field order for layout-sensitive contracts, but the compiler may still choose an efficient internal layout.
Use `std::mem::size_of`, `std::mem::align_of`, and `std::mem::offset_of` to inspect specific compiled layouts when optimizing private code.
Use `repr(C)` only when layout is a contract, such as FFI, not as a generic speed knob.

## Example
```rust
#[derive(Default)]
struct Particles {
    x: Vec<f32>,
    y: Vec<f32>,
    vx: Vec<f32>,
    vy: Vec<f32>,
}

impl Particles {
    fn push(&mut self, x: f32, y: f32, vx: f32, vy: f32) {
        self.x.push(x);
        self.y.push(y);
        self.vx.push(vx);
        self.vy.push(vy);
    }

    fn step(&mut self, dt: f32) {
        for ((x, y), (vx, vy)) in self
            .x
            .iter_mut()
            .zip(&mut self.y)
            .zip(self.vx.iter().zip(&self.vy))
        {
            *x += *vx * dt;
            *y += *vy * dt;
        }
    }
}

fn main() {
    let mut particles = Particles::default();
    particles.push(0.0, 1.0, 2.0, 3.0);
    particles.step(0.5);
    assert_eq!(particles.x[0], 1.0);
    assert_eq!(particles.y[0], 2.5);
}
```

This structure-of-arrays layout keeps each field in a contiguous vector.
The update loop touches only positions and velocities, so it avoids loading unrelated per-particle fields.
The iterator shape also keeps bounds and aliasing clear for the optimizer.

## Choosing a layout
Use array of structs when code naturally works object-by-object.
Use structure of arrays when hot loops scan one or two fields across many elements.
Use indexes or typed handles when relationships must be stored without pointer chasing.
Use small numeric IDs rather than repeated strings in hot state.
Split cold fields into a side table when they are rarely read during the hot path.

Do not make public types hard to use just to chase a theoretical cache win.
Hide layout behind methods when possible.
If a public API exposes slices, document ordering and mutation rules clearly.
If the layout uses parallel vectors, maintain equal lengths through one owner type so callers cannot desynchronize them.

## Best practice
- ✅ Start with [[Flamegraph and perf Workflow]] or counters that show memory stalls, cache misses, or traversal cost.
- ✅ Prefer `Vec<T>` and slices for hot sequential data.
- ✅ Keep hot loops traversing memory in storage order.
- ✅ Split hot and cold fields when a loop repeatedly touches only part of a large record.
- ✅ Use a structure-of-arrays owner type to keep parallel vectors consistent.
- ✅ Inspect size and alignment with `size_of`, `align_of`, and `offset_of` for private optimization work.
- ✅ Pair layout changes with [[Benchmarking with Criterion]] on realistic input sizes.
- ✅ Consider [[SIMD and target_feature]] only after the memory layout can feed vector code efficiently.

## Pitfalls
- ⚠️ Pointer-heavy structures can dominate runtime with cache misses even when allocation count is acceptable.
- ⚠️ Parallel vectors exposed directly can drift out of sync; wrap them in one owner type.
- ⚠️ Adding `repr(C)` does not automatically make a type faster and can freeze a layout contract unnecessarily.
- ⚠️ Overusing `repr(packed)` can create unaligned access hazards; see [[Type Layout and repr]].
- ⚠️ Reordering fields in public or FFI types can be a breaking layout change.
- ⚠️ Making code much less readable for an unmeasured cache theory is [[Speculative Micro-Optimization]].
- ⚠️ Optimizing layout while still allocating or cloning in the hot loop may miss the larger cost.

## See also
[[Type Layout and repr]] · [[Vec]] · [[The Slice Type]] · [[Iterator Performance]] · [[Bounds-Check Elimination]] · [[SIMD and target_feature]] · [[Reducing Heap Allocations]] · [[Arena Allocation]] · [[SmallVec for Inline Storage]] · [[Flamegraph and perf Workflow]] · [[Benchmarking with Criterion]] · [[Performance & Optimization]]

## Sources
- Rust Performance Book, "Type sizes" — [[rust-performance-book]],
  https://nnethercote.github.io/perf-book/type-sizes.html
- Rust Performance Book, "Heap allocations" — [[rust-performance-book]],
  https://nnethercote.github.io/perf-book/heap-allocations.html
- The Rust Reference, "Type layout: representations" — [[the-reference]],
  https://doc.rust-lang.org/reference/type-layout.html#representations
- Rust standard library, `Vec` — [[std]],
  https://doc.rust-lang.org/std/vec/struct.Vec.html
- Rust standard library, `size_of` and `offset_of` — [[std]],
  https://doc.rust-lang.org/std/mem/fn.size_of.html and https://doc.rust-lang.org/std/mem/macro.offset_of.html
- Verified research pack, "Performance & Optimization" — [[07-performance-optimization]]
