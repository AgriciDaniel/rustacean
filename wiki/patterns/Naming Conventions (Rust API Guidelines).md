---
type: pattern
title: "Naming Conventions (Rust API Guidelines)"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, naming, api-guidelines, api-design]
domain: "Idioms & API Design"
difficulty: intermediate
related: ["[[Conversion Method Prefixes]]", "[[Constructor Naming]]", "[[Iterator Method Trio]]", "[[Documentation Comments]]", "[[Conversion Traits]]"]
sources: ["[[the-reference]]", "[[rustdoc-book]]"]
source_urls: ["https://doc.rust-lang.org/reference/identifiers.html", "https://doc.rust-lang.org/style-guide/", "https://doc.rust-lang.org/rustdoc/how-to-write-documentation.html"]
rust_version: "edition 2024 / 1.85+"
---

# Naming Conventions (Rust API Guidelines)

Rust names should make APIs predictable: casing, word order, getter names, and conversion prefixes communicate semantics before a caller reads the implementation.

## What it is
Rust code conventionally uses `UpperCamelCase` for types and traits, `snake_case` for functions, methods, modules, and variables, and `SCREAMING_SNAKE_CASE` for constants and statics.
The Rust API Guidelines add higher-level naming rules for library APIs, including conversion prefixes, getter names, iterator method families, and consistent word order.

Names are part of the public contract.
Changing them is a breaking API change, and misleading names can be worse than verbose names.

## How it works
Use property names directly for getters: `name()`, not `get_name()`.
Use `_mut` for mutable accessors and `into_` for consuming accessors.
Use [[Conversion Method Prefixes]] to signal cost and ownership: `as_`, `to_`, and `into_` mean different things.

Acronyms are treated like words in Rust style: prefer `HttpClient` and `Uuid`, not `HTTPClient` or `UUID`.
Within a crate, keep word order consistent: if you choose `ParseConfigError`, do not also introduce `ConfigParseError`.

Names also interact with method lookup.
Inherent methods take priority over trait methods with the same name, and adding trait methods can create ambiguity for downstream crates that use glob imports.
For public APIs, avoid cute names and avoid generic verbs like `handle`, `process`, or `do_it` when a domain word would make call sites self-explanatory.

Rust warnings and Clippy lints catch some casing mistakes, but they cannot know whether a name's semantics are honest.
The API designer must keep ownership, cost, and failure visible in the vocabulary.

## Example
```rust
struct HttpClient {
    user_agent: String,
}

impl HttpClient {
    fn new(user_agent: impl Into<String>) -> Self {
        Self { user_agent: user_agent.into() }
    }

    fn user_agent(&self) -> &str {
        &self.user_agent
    }

    fn user_agent_mut(&mut self) -> &mut String {
        &mut self.user_agent
    }

    fn into_user_agent(self) -> String {
        self.user_agent
    }
}

fn main() {
    let mut client = HttpClient::new("RustBrain/1.0");
    client.user_agent_mut().push_str(" docs");

    assert_eq!(client.user_agent(), "RustBrain/1.0 docs");
    assert_eq!(client.into_user_agent(), "RustBrain/1.0 docs");
}
```

## Iterator and error names
Related items should share a predictable stem.

```rust
#[derive(Debug, PartialEq, Eq)]
struct ParseWidgetError {
    message: String,
}

struct WidgetIds {
    next: u32,
    end: u32,
}

impl Iterator for WidgetIds {
    type Item = u32;

    fn next(&mut self) -> Option<Self::Item> {
        if self.next == self.end {
            None
        } else {
            let id = self.next;
            self.next += 1;
            Some(id)
        }
    }
}

fn widget_ids(end: u32) -> WidgetIds {
    WidgetIds { next: 0, end }
}

fn main() {
    assert_eq!(widget_ids(3).collect::<Vec<_>>(), vec![0, 1, 2]);
    let err = ParseWidgetError { message: String::from("missing id") };
    assert_eq!(err.message, "missing id");
}
```

## Common errors
Rust warns about non-idiomatic casing:

```text
warning: type `http_client` should have an upper camel case name
```

Fix the public item name before release.
Renaming a public item later is a breaking change for downstream callers, even if the old name was merely awkward.

## Best practice
- ✅ Follow Rust casing consistently across public items.
- ✅ Name getters after the property and reserve `get` for APIs where lookup is the central operation.
- ✅ Use `as_`, `to_`, and `into_` according to [[Conversion Method Prefixes]].
- ✅ Keep error and iterator type names aligned with their constructors and methods.
- ✅ Treat acronyms as words: `HttpRequest`, `JsonValue`, `Uuid`.
- ✅ Use consistent word order across modules, especially for error types and builder names.

## Pitfalls
- ⚠️ Avoid Java-style `get_` prefixes for ordinary property access.
- ⚠️ Do not use `as_` for an allocating conversion or `to_` for a consuming conversion.
- ⚠️ Avoid clever abbreviations that force callers to learn local slang.
- ⚠️ Do not reuse a familiar standard-library method name for different semantics.
- ⚠️ Avoid names that hide fallibility, such as `parse` returning a default value on invalid input.

## See also
[[Conversion Method Prefixes]] · [[Constructor Naming]] · [[Iterator Method Trio]] · [[Documentation Comments]] · [[From and Into]] · [[AsRef for Flexible Arguments]] · [[Builder Pattern]] · [[Error Handling]] · [[Idioms & API Design]]

## Sources
- The Rust Reference, "Identifiers" - [[the-reference]], https://doc.rust-lang.org/reference/identifiers.html
- The Rust Style Guide - https://doc.rust-lang.org/style-guide/
- How to write documentation - [[rustdoc-book]], https://doc.rust-lang.org/rustdoc/how-to-write-documentation.html
- Rust API Guidelines, "Naming" - https://rust-lang.github.io/api-guidelines/naming.html
