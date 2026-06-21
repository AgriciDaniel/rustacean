---
type: pattern
title: "SAFETY Comments"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, unsafe, documentation, pattern]
domain: "Unsafe Rust & FFI"
difficulty: intermediate
related: ["[[Unsafe Rust]]", "[[unsafe fn]]", "[[Soundness vs Safety]]", "[[Safe Abstractions over Unsafe Code]]", "[[Undefined Behavior]]", "[[Miri]]"]
sources: ["[[the-book]]", "[[the-reference]]", "[[rustonomicon]]"]
source_urls: ["https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#accessing-or-modifying-a-mutable-static-variable", "https://doc.rust-lang.org/reference/unsafe-keyword.html", "https://doc.rust-lang.org/nomicon/working-with-unsafe.html"]
rust_version: "edition 2024 / 1.85+"
---

# SAFETY Comments

SAFETY comments state the concrete invariant that makes an unsafe operation sound at the exact place where the compiler cannot verify it.

## What it is
A `// SAFETY:` comment is a local proof note attached to an unsafe block or unsafe
implementation. A public [[unsafe fn]] should also have a `# Safety` documentation
section describing caller obligations.

The Book calls this idiomatic for unsafe functions and unsafe operations. The goal
is not ceremony; it is to keep the human proof close enough that reviewers can check
whether the code actually establishes the stated facts.

## How it works
A useful SAFETY comment names the operation's preconditions and points to the code,
type invariant, or API contract that establishes each one.

Weak comment: `// SAFETY: this is safe`.

Useful comment: `// SAFETY: index < slice.len(), ptr came from slice.as_ptr(), and
u8 is initialized in every element of a slice.`

The comment should be updated when the validation changes. If the proof becomes too
large for one comment, the unsafe block is probably doing too much.

For public APIs, separate two comment styles. `# Safety` documentation belongs on
the unsafe item and tells callers what they must guarantee. `// SAFETY:` comments
belong at unsafe operations and explain why the current code has met that operation's
preconditions. A safe function with an unsafe block usually needs only the local
comment, because callers should not inherit any unsafe obligation.

## Example
```rust
fn byte_at(bytes: &[u8], index: usize) -> Option<u8> {
    if index >= bytes.len() {
        return None;
    }

    let ptr = bytes.as_ptr();
    // SAFETY: index is in bounds for bytes, ptr came from bytes, and u8 is Copy.
    Some(unsafe { *ptr.add(index) })
}

fn main() {
    assert_eq!(byte_at(b"abc", 2), Some(b'c'));
    assert_eq!(byte_at(b"abc", 9), None);
}
```

## Worked example
```rust
/// Returns a shared view of `len` bytes at `ptr`.
///
/// # Safety
///
/// `ptr` must be non-null, valid for reads of `len` bytes, and point to one
/// allocation that remains alive for `'a`.
unsafe fn view_bytes<'a>(ptr: *const u8, len: usize) -> &'a [u8] {
    // SAFETY: the caller guarantees the full from_raw_parts contract.
    unsafe { std::slice::from_raw_parts(ptr, len) }
}

fn main() {
    let data = [1, 2, 3];
    // SAFETY: data is live and initialized for data.len() bytes.
    let view = unsafe { view_bytes(data.as_ptr(), data.len()) };
    assert_eq!(view, &[1, 2, 3]);
}
```

This example has both levels: the item docs define the caller contract, and the
body comment connects the unsafe operation to that contract. If the function later
checked the pointer internally and became safe, the caller-facing `# Safety` section
would no longer be appropriate.

## Common errors
SAFETY comments do not change compiler behavior. If the unsafe block is missing,
rustc still reports E0133:

```text
error[E0133]: call to unsafe function is unsafe and requires unsafe block
```

The fix is to add a real unsafe boundary and a real proof. A comment that says
"checked above" is insufficient unless the nearby code actually checks every
precondition the unsafe operation requires.

## Best practice
- ✅ Put `// SAFETY:` immediately before or inside the unsafe block it justifies.
- ✅ For public unsafe APIs, add `# Safety` docs that tell callers exactly what they must guarantee.
- ✅ Mention lifetimes, alignment, initialization, aliasing, bounds, ABI, and thread-safety when relevant.
- ✅ Use comments as review handles: each claim should be checkable from nearby code or documented invariants.
- ✅ Keep one unsafe operation or one tightly related group per comment whenever practical.
- ✅ Update comments in the same commit as invariant-changing edits, especially around constructors and trait impls.

## Pitfalls
- ⚠️ Writing comments that restate the operation instead of proving it.
- ⚠️ Letting comments drift after refactors.
- ⚠️ Omitting caller obligations from `unsafe fn` docs because the name seems obvious.
- ⚠️ Using a SAFETY comment to rationalize an API that should instead be redesigned as safe or more constrained.
- ⚠️ Copy-pasting a comment from a similar unsafe block without checking differences in alignment, length, or aliasing requirements.

## See also
[[Unsafe Rust]] · [[unsafe fn]] · [[Soundness vs Safety]] · [[Safe Abstractions over Unsafe Code]] · [[Undefined Behavior]] · [[Miri]] · [[FFI with C]] · [[Dereferencing Raw Pointers]] · [[Unsafe Rust & FFI]]

## Sources
- The Rust Programming Language, ch. 20.1 "Accessing or Modifying a Mutable Static Variable" — [[the-book]], https://doc.rust-lang.org/book/ch20-01-unsafe-rust.html#accessing-or-modifying-a-mutable-static-variable
- The Rust Reference, "The unsafe keyword" — [[the-reference]], https://doc.rust-lang.org/reference/unsafe-keyword.html
- The Rustonomicon, "Working with Unsafe" — [[rustonomicon]], https://doc.rust-lang.org/nomicon/working-with-unsafe.html
