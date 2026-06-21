---
type: concept
title: "OnceLock and LazyLock"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, concurrency, once-lock, lazy-lock, initialization, statics]
domain: "Concurrency"
difficulty: intermediate
related: ["[[Shared State with Mutex]]", "[[Threads]]", "[[Arc]]", "[[Send and Sync]]", "[[Mutex Poisoning and Recovery]]", "[[Static Items]]"]
sources: ["[[std]]", "[[the-book]]", "[[08-concurrency]]"]
source_urls: ["https://doc.rust-lang.org/std/sync/struct.OnceLock.html", "https://doc.rust-lang.org/std/sync/struct.LazyLock.html", "https://doc.rust-lang.org/book/ch16-03-shared-state.html"]
rust_version: "edition 2024 / 1.85+"
---

# OnceLock and LazyLock

`OnceLock<T>` and `LazyLock<T>` are thread-safe one-time initialization primitives for values that should be computed once and then shared by reference.

## What it is
`OnceLock<T>` is a cell that starts empty and can be initialized once.
After initialization, callers get `&T`.
It is safe to use in `static` items and safe to access from multiple threads.

`LazyLock<T, F>` stores an initializer closure and runs it on first access.
It is the simpler choice when initialization needs no runtime argument.
It dereferences like a shared `T`, so readers usually write `&*VALUE` or call methods through deref.

Use `OnceLock` when the value is supplied by configuration, a test setup, a parser, or some other caller-provided input.
Use `LazyLock` when the initializer is fixed at declaration time.
Both avoid the old pattern of a `static mut` plus unsafe initialization code.

## How it works
`OnceLock::new()` creates an empty cell.
`set(value)` tries to initialize it and returns the value back on failure.
`get()` returns `None` if the value is not initialized.
`get_or_init(f)` initializes with `f()` if needed and returns the stored reference.
If the initializer panics, the panic is propagated and the `OnceLock` remains uninitialized.
`OnceLock` is not poisoned by panic.

`LazyLock::new(f)` creates a lazy value.
The first dereference or `LazyLock::force(&value)` runs `f`.
If another thread is already running the initializer, the caller blocks until initialization finishes.
Unlike `OnceLock`, `LazyLock` poisoning is unrecoverable: if its initializer panics, future dereferences panic.

For edition 2024 / stable 1.85+ examples, stick to `new`, `set`, `get`, `get_or_init`, deref, and `force`.
Some methods shown in current online docs were stabilized after 1.85 or are still nightly-only; do not use those in baseline examples unless the note explicitly calls out the higher version.

## Example
```rust
use std::sync::{LazyLock, OnceLock};

static CONFIG: OnceLock<String> = OnceLock::new();
static FALLBACK_NAME: LazyLock<String> = LazyLock::new(|| String::from("guest"));

fn configure(value: String) -> Result<(), String> {
    CONFIG.set(value)
}

fn name() -> &'static str {
    CONFIG
        .get()
        .map(String::as_str)
        .unwrap_or_else(|| FALLBACK_NAME.as_str())
}

fn main() {
    assert_eq!(name(), "guest");
    configure(String::from("admin")).unwrap();
    assert_eq!(name(), "admin");
    assert_eq!(configure(String::from("ignored")), Err(String::from("ignored")));
}
```

## Example: get_or_init
```rust
use std::sync::OnceLock;

static WORDS: OnceLock<Vec<String>> = OnceLock::new();

fn words() -> &'static [String] {
    WORDS.get_or_init(|| {
        vec![
            String::from("ownership"),
            String::from("borrowing"),
            String::from("threads"),
        ]
    })
}

fn main() {
    assert_eq!(words()[0], "ownership");
    assert_eq!(words().len(), 3);
}
```

## Best practice
- ✅ Use `LazyLock` for fixed lazy statics whose initializer needs no argument.
- ✅ Use `OnceLock` when initialization is caller-driven or fallible setup should happen before reads.
- ✅ Keep initializers short and side-effect-light; every reader may block behind the first initializer.
- ✅ Prefer these types over unsafe global initialization.
- ✅ Treat `set` returning `Err(value)` as a normal race or duplicate-initialization signal.
- ✅ Keep mutable state behind [[Shared State with Mutex]], [[RwLock]], or [[Atomics]] instead of trying to mutate a `OnceLock` value in place.

## Pitfalls
- ⚠️ `OnceLock` is not a resettable cache for ordinary shared mutation; after initialization it exposes shared references.
- ⚠️ Reentrant initialization is an error; do not call back into the same cell from its initializer.
- ⚠️ `LazyLock` poisoning is unrecoverable, unlike [[Mutex Poisoning and Recovery]].
- ⚠️ A `static LazyLock` value is not normally dropped at program termination, so do not rely on its `Drop` for external cleanup.
- ⚠️ Do not use nightly-only methods from current docs in stable-1.85-targeted examples.
- ⚠️ Do not hide expensive I/O in a global lazy initializer if startup and error reporting need to be explicit.

## See also
[[Concurrency]] · [[Shared State with Mutex]] · [[Arc]] · [[Send and Sync]] · [[Threads]] · [[Atomics]] · [[RwLock]] · [[Mutex Poisoning and Recovery]] · [[Ownership]] · [[Interior Mutability]]

## Sources
- Standard library, `std::sync::OnceLock` — [[std]],
  https://doc.rust-lang.org/std/sync/struct.OnceLock.html
- Standard library, `std::sync::LazyLock` — [[std]],
  https://doc.rust-lang.org/std/sync/struct.LazyLock.html
- The Rust Programming Language, ch. 16.3 "Shared-State Concurrency" — [[the-book]],
  https://doc.rust-lang.org/book/ch16-03-shared-state.html
