---
type: concept
title: "Practice: Quizzes"
status: seed
created: 2026-06-21
updated: 2026-06-21
tags: [rust, practice, rustlings, quizzes]
domain: "Practice (Rustlings)"
difficulty: intermediate
related: ["[[Practice (Rustlings)]]", "[[Ownership]]", "[[Named Field Structs]]", "[[Enums]]", "[[Result]]", "[[Iterators]]"]
sources: ["[[rustlings]]"]
source_urls: ["https://github.com/rust-lang/rustlings"]
rust_version: "edition 2024 / 1.85+"
---

# Practice: Quizzes

The quizzes group combines earlier Rustlings topics into small programs that must compile and pass tests. The key idea is integration: syntax, ownership, data modeling, and error handling all have to fit at once.

## What it is
These exercises are checkpoints rather than new topic introductions. They ask for complete fixes across variables, functions, structs, enums, options, results, and iterators.

## How it works
Each quiz uses the same compiler feedback loop as the topic folders, but the missing piece may involve several concepts at once. Start by reading the types and tests, then solve the first compiler error without losing the intended behavior.

## Example
```rust
#[derive(Debug, PartialEq)]
enum Grade {
    Pass,
    Fail,
}

fn grade(score: u8) -> Grade {
    if score >= 60 {
        Grade::Pass
    } else {
        Grade::Fail
    }
}

fn main() {
    println!("{:?}", grade(88));
}
```

## Best practice
- ✅ Read the whole file before editing; quiz failures often depend on later tests.
- ✅ Let types guide the solution before adding extra state or allocations.
- ✅ Reuse the simplest construct from the earlier topic that fits the problem.

## Pitfalls
- ⚠️ Do not overfit to one visible assertion if hidden behavior is implied by the type.
- ⚠️ Do not replace compile errors with panics just to satisfy a signature.
- ⚠️ Do not add clones or owned strings until ownership analysis says they are needed.

## See also
[[Practice (Rustlings)]] · [[Ownership]] · [[Named Field Structs]] · [[Enums]] · [[Result]] · [[Iterators]] · [[Trait Bounds]]

## Sources
- Rustlings `quizzes` exercises — [[rustlings]],
  https://github.com/rust-lang/rustlings
