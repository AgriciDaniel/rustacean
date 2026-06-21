---
type: concept
title: "The inline Attribute"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, performance, attributes, codegen]
domain: "Performance & Optimization"
difficulty: advanced
related: ["[[Attribute Macros]]", "[[Codegen and Optimization Flags]]", "[[LTO and codegen-units]]", "[[Static Dispatch with Generics]]", "[[Zero-Cost Abstractions]]", "[[Benchmarking with Criterion]]", "[[Performance & Optimization]]"]
sources: ["[[the-reference]]", "[[rustc-book]]", "[[cargo-book]]"]
source_urls: ["https://doc.rust-lang.org/reference/attributes/codegen.html#the-inline-attribute", "https://doc.rust-lang.org/rustc/codegen-options/index.html#inline-threshold", "https://doc.rust-lang.org/cargo/reference/profiles.html#lto"]
rust_version: "edition 2024 / 1.85+"
---

# The inline Attribute

`#[inline]` is a code generation hint, most useful for small public functions that need cross-crate optimization; it is not a command and it is not a general speed switch.

## What it is
The `inline` attribute can be written as `#[inline]`, `#[inline(always)]`, or `#[inline(never)]`.
The Rust Reference defines it as a hint to the compiler's inliner.
That distinction matters: the optimizer may ignore an inline request or inline a function without the attribute.

The attribute is most relevant at crate boundaries.
Inside one crate, the compiler and LLVM can usually see private function bodies during optimization.
Across crates, a downstream crate may need the function body available in metadata to inline a small public wrapper.
That is why `#[inline]` appears frequently on tiny standard library and crate APIs.

## How it works
Inlining trades call overhead and optimization visibility against compile time and code size.
If a helper is inlined, the optimizer may propagate constants, remove branches, and simplify bounds checks in the caller.
If too much code is inlined, the binary grows, instruction cache behavior can get worse, and compile time increases.
For cross-crate calls, `#[inline]` also changes what gets made available to downstream crates for optimization.
A small public function in a library may otherwise be visible only as a symbol to call.
With `#[inline]`, downstream compilation can see the body and decide whether to substitute it into each call site.
That can improve runtime code but can also increase downstream compile time because more code is optimized in more crates.

`#[inline(always)]` is stronger than `#[inline]`, but it is still a hint, and it should be rare.
Use it only for a tiny hot function after measurement shows that normal optimization did not inline it.
`#[inline(never)]` is useful for keeping cold error paths out of hot code or for making profiles easier to read.
The attribute is not transitive in the way many people expect.
If an inlined public wrapper immediately calls a private helper that is not visible or not inlined, the call may remain.
For library APIs, a tiny public wrapper should either contain the tiny operation directly or keep the private helper small and measurable.
For application binaries, [[LTO and codegen-units]] often gives the optimizer a broader view without turning source code into a field of annotations.

## Example
```rust
#[derive(Clone, Copy)]
pub struct Millis(pub u64);

impl Millis {
    #[inline]
    pub fn as_secs_f64(self) -> f64 {
        self.0 as f64 / 1_000.0
    }
}

#[inline(never)]
fn format_error(ms: Millis) -> String {
    format!("timeout after {:.3} seconds", ms.as_secs_f64())
}

fn main() {
    let elapsed = Millis(1_250);
    assert_eq!(elapsed.as_secs_f64(), 1.25);
    assert!(format_error(elapsed).contains("timeout"));
}
```

The public getter-like method is a reasonable candidate for `#[inline]` in a library.
The formatting helper is intentionally not inlined because formatting is large and cold relative to the numeric conversion.

## Worked example: hot wrapper, cold error path
```rust
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct Percent(u8);

impl Percent {
    #[inline]
    pub fn get(self) -> u8 {
        self.0
    }

    pub fn new(value: u8) -> Result<Self, String> {
        if value <= 100 {
            Ok(Self(value))
        } else {
            Err(percent_error(value))
        }
    }
}

#[inline(never)]
fn percent_error(value: u8) -> String {
    format!("percent must be <= 100, got {value}")
}

fn main() {
    let pct = Percent::new(42).unwrap();
    assert_eq!(pct.get(), 42);
    assert!(Percent::new(200).is_err());
}
```

The tiny getter is plausible in a public library API because callers may use it in hot loops.
The error formatting is kept out of the hot constructor path.
This shape is still a hypothesis: only a profile and benchmark can prove that the split matters.

## Common errors
`#[inline]` is an attribute on items, not a statement inside a function body.

```text
error: expected statement after outer attribute
```

Put it directly before a function, method, closure-like item supported by the Reference, or compatible item form.
Another common mistake is trying to combine contradictory forms:

```text
error: multiple `inline` attributes
```

Choose one of `#[inline]`, `#[inline(always)]`, or `#[inline(never)]`.
If the goal is profiling readability, use `#[inline(never)]`; if the goal is cross-crate visibility for a tiny public function, use plain `#[inline]`.

## Best practice
- ✅ Put `#[inline]` on tiny public library functions when cross-crate callers benefit from seeing the body.
- ✅ Prefer plain `#[inline]` over `#[inline(always)]` unless a benchmark and profile justify the stronger hint.
- ✅ Consider `#[inline(never)]` for cold, large, diagnostic, or formatting-heavy paths.
- ✅ Re-measure after adding inline attributes; inlining can help one call site and hurt another.
- ✅ Try [[LTO and codegen-units]] for whole-program optimization before scattering attributes through application code.
- ✅ Keep inline annotations close to API boundaries or measured hot spots so future readers can infer the reason.
- ✅ Prefer splitting hot and cold code paths over forcing a large function to inline as one unit.
- ✅ Re-check annotations after compiler upgrades; inliner heuristics and generated code can change.

## Pitfalls
- ⚠️ Sprinkling `#[inline(always)]` everywhere can increase compile time and binary size without improving runtime.
- ⚠️ Adding `#[inline]` to private functions is often noise because intra-crate optimization can already see them.
- ⚠️ Assuming generic functions always need `#[inline]` ignores monomorphization; generic bodies are already available where instantiated.
- ⚠️ Treating inline as a correctness feature is wrong; program behavior must not depend on whether a call is inlined.
- ⚠️ Using inline attributes before profiling is a form of [[Speculative Micro-Optimization]].
- ⚠️ Exposing too many inline bodies from a widely used crate can move compile-time cost to every downstream user.
- ⚠️ Using `#[inline(never)]` on a tiny hot helper can block constant propagation and bounds-check elimination.

## See also
[[Codegen and Optimization Flags]] · [[Profiles and Optimization Settings]] · [[LTO and codegen-units]] · [[Static Dispatch with Generics]] · [[Zero-Cost Abstractions]] · [[Benchmarking with Criterion]] · [[Profiling Rust Programs]] · [[Speculative Micro-Optimization]] · [[Avoiding Premature Optimization]] · [[Performance & Optimization]]

## Sources
- The Rust Reference, "Code generation attributes: inline" — [[the-reference]],
  https://doc.rust-lang.org/reference/attributes/codegen.html#the-inline-attribute
- The rustc Book, "Codegen options" — [[rustc-book]],
  https://doc.rust-lang.org/rustc/codegen-options/index.html
- The Cargo Book, "Profiles: lto" — [[cargo-book]],
  https://doc.rust-lang.org/cargo/reference/profiles.html#lto
