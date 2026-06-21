---
type: concept
title: "The Drop Trait"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, ownership, drop, destructors]
domain: "Ownership & Memory"
difficulty: intermediate
related: ["[[Ownership]]", "[[Move Semantics]]", "[[Copy and Clone]]", "[[The Stack and the Heap]]", "[[RAII and Drop Guards]]", "[[Panic Unwinding and Abort]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html", "https://doc.rust-lang.org/reference/destructors.html", "https://doc.rust-lang.org/std/ops/trait.Drop.html"]
rust_version: "edition 2024 / 1.85+"
aliases: ["RAII and Drop Guards"]
---

# The Drop Trait

`Drop` is Rust's destructor hook: when an initialized value goes out of scope or is overwritten, Rust runs cleanup for that value and then recursively drops its fields. Ownership decides which value is responsible for that cleanup.

## What it is
The `Drop` trait lets a type define cleanup code in `fn drop(&mut self)`.
Types use it to release heap memory, close files, unlock guards, decrement reference counts, flush buffers, or return other resources.

Most Rust code does not call `drop` methods directly.
The compiler inserts destructor calls automatically at the end of scopes, on assignment to an initialized place, and along control-flow paths such as early return and panic unwinding when unwinding is enabled.

The destructor of a type consists of calling its `Drop::drop` implementation if it has one, then dropping its fields.
The Reference defines the detailed order for fields, arrays, locals, temporaries, and function parameters.

## How it works
Local variables are dropped in reverse order of declaration when their scope is left.
Struct fields are dropped in declaration order after the struct's own `Drop::drop` runs.
Assignment to an initialized variable drops the old value before storing the new value.

`std::mem::drop(value)` is just a function that takes ownership of `value`, causing it to be dropped at the end of that function call.
Use it when early release matters, such as dropping a lock guard before slow work.

Static items do not call `drop` at program termination.
Also, `Copy` and `Drop` are incompatible: a type that needs destructor logic cannot be implicitly duplicated.

Destructor order matters when cleanup has side effects.
Local bindings in one scope drop in reverse declaration order, while struct fields drop in the order
they are declared after the type's own `Drop::drop` method runs.
If one field's destructor depends on another field, declare fields and write `Drop::drop` with that
order in mind, or wrap dependent resources in a dedicated owner that encodes the invariant.

`Drop::drop` receives `&mut self`, not ownership of `self`.
That prevents moving fields out directly during destruction, because the compiler still needs to
drop the remaining initialized fields afterward.
Use `Option<T>` plus `take()` inside a type only when the type is explicitly designed around early
extraction.

## Example
```rust
struct TempBuffer {
    name: String,
}

impl Drop for TempBuffer {
    fn drop(&mut self) {
        println!("releasing {}", self.name);
    }
}

fn main() {
    let first = TempBuffer { name: String::from("first") };
    let second = TempBuffer { name: String::from("second") };

    drop(first);
    println!("after early drop");

    let _still_drops = second;
}
```

## Worked example
```rust
use std::sync::{Arc, Mutex};
use std::thread;

fn main() {
    let shared = Arc::new(Mutex::new(Vec::new()));

    {
        let mut guard = shared.lock().expect("mutex poisoned");
        guard.push("prepared");
    } // guard drops here, unlocking before the thread starts.

    let worker_state = Arc::clone(&shared);
    let handle = thread::spawn(move || {
        worker_state.lock().expect("mutex poisoned").push("done");
    });

    handle.join().expect("worker panicked");
    println!("{:?}", shared.lock().expect("mutex poisoned"));
}
```

## Common errors
Calling a destructor method directly is rejected:

```text
error[E0040]: explicit use of destructor method
```

Use `std::mem::drop(value)` to move the value into an immediate drop point:

```rust
fn main() {
    let text = String::from("release now");
    drop(text);
}
```

## Best practice
- ✅ Let scope drive cleanup; use explicit `drop(value)` only when releasing early makes behavior clearer or avoids holding a resource too long.
- ✅ Keep `Drop::drop` small, infallible in practice, and focused on cleanup.
- ✅ Use RAII guard types so resources are released on every normal exit path.
- ✅ Understand drop order when one field's cleanup depends on another field still being valid.
- ✅ Prefer explicit `close`, `flush`, or `finish` methods returning `Result` when cleanup can fail and
  callers must observe the error.
- ✅ Keep panics out of destructors; panicking while another panic is already unwinding can abort the
  process.

## Pitfalls
- ⚠️ Do not manually call `value.drop()`; Rust does not allow direct destructor calls. Use `drop(value)` if early cleanup is needed.
- ⚠️ Do not put essential process-shutdown cleanup only in `Drop` for `static` items; statics are not dropped at program end.
- ⚠️ Do not combine hidden clones with cleanup-owning types; shared cleanup needs explicit ownership such as [[Arc]].
- ⚠️ Do not hold a guard until the end of a long scope accidentally. See [[Holding Locks Too Long]] and [[RAII and Drop Guards]].
- ⚠️ Do not rely on `Drop` for `mem::forget`, leaked boxes, reference cycles, or aborting process
  termination paths; destructors are not a universal finally block.

## See also
[[Ownership]] · [[Move Semantics]] · [[Copy and Clone]] · [[The Stack and the Heap]] · [[RAII and Drop Guards]] · [[Panic Unwinding and Abort]] · [[Holding Locks Too Long]] · [[Shared State with Mutex]] · [[Ownership & Memory]]

## Sources
- The Rust Programming Language, ch. 4.1 "Memory and Allocation" — [[the-book]],
  https://doc.rust-lang.org/book/ch04-01-what-is-ownership.html
- The Rust Reference, "Destructors" — [[the-reference]],
  https://doc.rust-lang.org/reference/destructors.html
- Standard library docs for `Drop`,
  https://doc.rust-lang.org/std/ops/trait.Drop.html
