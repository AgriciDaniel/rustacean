---
type: pattern
title: "Re-exporting with pub use"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, pub-use, re-export, api-design]
domain: "Modules & Project Structure"
difficulty: intermediate
related: ["[[The use Keyword]]", "[[Visibility and Privacy]]", "[[Module Paths]]", "[[Modules]]", "[[Splitting Modules into Files]]", "[[Glob Imports in Public Code]]"]
sources: ["[[the-book]]", "[[the-reference]]"]
source_urls: ["https://doc.rust-lang.org/book/ch07-04-bringing-paths-into-scope-with-the-use-keyword.html#re-exporting-names-with-pub-use", "https://doc.rust-lang.org/reference/items/use-declarations.html#use-visibility", "https://doc.rust-lang.org/reference/visibility-and-privacy.html#re-exporting-and-visibility"]
rust_version: "edition 2024 / 1.85+"
---

# Re-exporting with pub use

`pub use` imports a name into a module and makes that imported name part of the module's public API.

## What it is
Re-exporting lets a crate expose a caller-friendly API that differs from its
internal module layout. The implementation can live in private modules while
callers import the stable names from the crate root or another facade module.

This is especially useful when internal organization follows implementation
concerns but the public API should follow domain concepts.

## How it works
`use` creates a private binding by default. `pub use` makes that binding public
if the target item can be re-exported. The re-export can provide public access
through a short path even when the target's canonical module path includes
private implementation modules.

Privacy still matters: the item being exposed must itself have suitable
visibility. `pub use` is not a way to publish a private function that should
remain private; it is a way to choose the public path for a public item.

Rustdoc also presents re-exports as part of the public API, so this pattern
affects how users discover the crate.

## Example
```rust
mod implementation {
    pub struct Client {
        endpoint: &'static str,
    }

    impl Client {
        pub fn new(endpoint: &'static str) -> Self {
            Self { endpoint }
        }

        pub fn endpoint(&self) -> &'static str {
            self.endpoint
        }
    }
}

pub use implementation::Client;

fn main() {
    let client = Client::new("https://example.invalid");
    assert_eq!(client.endpoint(), "https://example.invalid");
}
```

Callers can use `Client` from the facade even though it is implemented in an
internal module.

## Worked example
A facade can expose a stable domain API while keeping submodules private:

```rust
mod http {
    pub struct Request {
        path: String,
    }

    impl Request {
        pub fn new(path: &str) -> Self {
            Self { path: path.to_owned() }
        }

        pub fn path(&self) -> &str {
            &self.path
        }
    }
}

mod service {
    pub trait Handler {
        fn handle(&self, request: &crate::Request) -> String;
    }
}

pub use http::Request;
pub use service::Handler;

fn main() {
    let request = Request::new("/health");
    assert_eq!(request.path(), "/health");
}
```

The public API is `crate::Request` and `crate::Handler`, not
`crate::http::Request` or `crate::service::Handler`.

## Common errors
Re-exporting an item that is not visible enough usually produces E0364 or
E0365:

```rust
mod implementation {
    struct Client;
}

pub use implementation::Client;
```

Typical diagnostic:

```console
error[E0603]: struct `Client` is private
```

Fix it by making the target item `pub` while keeping the implementation module
private: `pub struct Client;`. The re-export supplies the public path.

## Deeper mechanics
A `pub use` is both an import and a public item. The binding is created in the
current module, and that binding can be named by external code if its
visibility permits. The Reference describes this as redirecting a public name
to another target definition, including a target whose canonical path passes
through private modules.

This distinction matters for semver and rustdoc. Removing a re-export removes
a public path even if the underlying item still exists. Renaming the internal
module can be non-breaking if all stable re-exports remain, but renaming the
re-exported public name is breaking for callers.

## Best practice
- ✅ Re-export the types and traits users should reach for first from the crate root or a focused prelude.
- ✅ Keep implementation modules private when their names are not part of the API contract.
- ✅ Use `pub use path::Type as BetterName;` when the public name should differ from an internal name.
- ✅ Review re-exports as semver-relevant API, not as cosmetic imports.
- ✅ Re-export concrete error types and key traits from the same facade as the functions that return or require them.
- ✅ Use a prelude module only when users genuinely benefit from importing many extension traits together.
- ✅ Document the facade path in examples so users do not learn private implementation paths.

## Pitfalls
- ⚠️ Re-exporting entire modules just because they exist internally; expose concepts, not folders.
- ⚠️ Using `pub use some_module::*` in public API; see [[Glob Imports in Public Code]].
- ⚠️ Forgetting that removing or renaming a re-export is a breaking change for library users.
- ⚠️ Making every internal item public to satisfy one re-export instead of designing a narrower facade.
- ⚠️ Re-exporting unstable implementation details from the crate root and later discovering users depend on them.
- ⚠️ Creating multiple public paths for the same concept without a clear preferred path in docs.
- ⚠️ Assuming `pub use` bypasses item visibility; the target still needs suitable visibility.

## See also
[[The use Keyword]] · [[Visibility and Privacy]] · [[Module Paths]] · [[Modules]] · [[Splitting Modules into Files]] · [[Glob Imports in Public Code]] · [[Semantic Versioning]] · [[Publishing to crates.io]] · [[Library and Binary Package Layout]] · [[Modules & Project Structure]]

## Sources
- The Rust Programming Language, "Re-exporting Names with pub use" — [[the-book]], https://doc.rust-lang.org/book/ch07-04-bringing-paths-into-scope-with-the-use-keyword.html#re-exporting-names-with-pub-use
- The Rust Reference, "use Visibility" — [[the-reference]], https://doc.rust-lang.org/reference/items/use-declarations.html#use-visibility
- The Rust Reference, "Re-exporting and visibility" — [[the-reference]], https://doc.rust-lang.org/reference/visibility-and-privacy.html#re-exporting-and-visibility
