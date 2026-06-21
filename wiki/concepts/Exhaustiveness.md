---
type: concept
title: "Exhaustiveness"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, match, exhaustiveness, enums]
domain: "Enums & Pattern Matching"
difficulty: basic
related: ["[[The match Expression]]", "[[Enums]]", "[[Option]]", "[[Catch-All and Wildcard Patterns]]", "[[Overbroad Catch-All Match Arms]]", "[[Enums & Pattern Matching]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch06-02-match.html#matches-are-exhaustive", "https://doc.rust-lang.org/book/ch19-01-all-the-places-for-patterns.html#match-arms"]
rust_version: "edition 2024 / 1.85+"
---

# Exhaustiveness

Exhaustiveness is Rust's requirement that a `match` cover every possible value of the matched expression.

## What it is
In a `match`, every possible input must be handled by some arm.
For an enum, that usually means every variant.
For `Option<T>`, it means both `Some(_)` and `None`.
For larger value spaces, a wildcard, catch-all binding, or complete range coverage may be needed.

This is a major safety feature.
When a new enum variant is introduced and you matched explicitly, the compiler points to all places that need a decision.

## How it works
The compiler analyzes the set of patterns in the match arms.
If any possible value is uncovered, the code fails to compile.
If an earlier arm already covers later arms, the compiler can warn that later patterns are unreachable.

Catch-all arms satisfy exhaustiveness but remove information.
Use them intentionally for values you truly want to ignore.
When matching your own domain enum, prefer naming every variant while the domain is still evolving.

Exhaustiveness is checked over patterns, not over arbitrary boolean logic. A guarded arm such as
`Some(n) if n > 0` does not cover all `Some(_)` values because the guard may be false at runtime.
Similarly, a range like `1..=10` covers only that range; the compiler still requires the rest of the
integer or character domain to be covered.

For library APIs, `#[non_exhaustive]` intentionally prevents downstream crates from assuming they know
all variants or fields. Inside your own crate, explicit matches make refactors loud. Outside your crate,
an explicit wildcard may be required as a forward-compatibility arm.

## Example
```rust
enum TrafficLight {
    Red,
    Yellow,
    Green,
}

fn instruction(light: TrafficLight) -> &'static str {
    match light {
        TrafficLight::Red => "stop",
        TrafficLight::Yellow => "slow down",
        TrafficLight::Green => "go",
    }
}

fn main() {
    assert_eq!(instruction(TrafficLight::Green), "go");
}
```

## Worked example
```rust
enum Access {
    Anonymous,
    User { suspended: bool },
    Admin,
}

fn can_delete(access: Access) -> bool {
    match access {
        Access::Anonymous => false,
        Access::User { suspended: true } => false,
        Access::User { suspended: false } => true,
        Access::Admin => true,
    }
}

fn main() {
    assert!(!can_delete(Access::Anonymous));
    assert!(can_delete(Access::User { suspended: false }));
}
```

## Common errors
The compiler reports the first uncovered shape it can name:

```text
error[E0004]: non-exhaustive patterns: `Access::Admin` not covered
```

Fix it by adding the missing variant or a deliberate catch-all. If a guarded arm appears to cover a
case, add an unguarded arm for the same pattern shape because guards are not proof of exhaustiveness.

## Best practice
- ✅ Match every variant explicitly for small domain enums you own.
- ✅ Use `_` only when all remaining values genuinely share the same behavior.
- ✅ Let exhaustiveness errors guide refactors after adding enum variants.
- ✅ Prefer explicit field patterns for security, billing, persistence, and protocol decisions.
- ✅ Use `#[non_exhaustive]` on public enums only when downstream crates must keep a fallback arm.

## Pitfalls
- ⚠️ A final `_ => ...` can hide newly added variants; see [[Overbroad Catch-All Match Arms]].
- ⚠️ [[if let]] does not enforce exhaustiveness; choose it only when ignoring other cases is intended.
- ⚠️ Match guards can make exhaustiveness less obvious; include an unguarded fallback for the same shape when needed.
- ⚠️ Do not assume exhaustive matching on primitive values is practical without ranges or wildcards.
- ⚠️ Do not silence E0004 with `todo!()` unless the note or code clearly marks unfinished behavior.

## See also
[[The match Expression]] · [[Enums]] · [[Option]] · [[Patterns]] · [[Catch-All and Wildcard Patterns]] · [[Overbroad Catch-All Match Arms]] · [[Match Guards]] · [[Refutable and Irrefutable Patterns]] · [[Enum Variants with Data]] · [[Enums & Pattern Matching]]

## Sources
- The Rust Programming Language, ch. 6.2 "Matches Are Exhaustive" - [[the-book]], https://doc.rust-lang.org/book/ch06-02-match.html#matches-are-exhaustive
- The Rust Programming Language, ch. 19.1 "match Arms" - [[the-book]], https://doc.rust-lang.org/book/ch19-01-all-the-places-for-patterns.html#match-arms
