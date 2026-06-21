---
type: pattern
title: "Builder Pattern"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, builder, constructors, api-design]
domain: "Idioms & API Design"
difficulty: intermediate
related: ["[[Constructor Naming]]", "[[Type-State Pattern]]", "[[Making Invalid States Unrepresentable]]", "[[Accepting impl Trait vs Generics]]", "[[Conversion Traits]]"]
sources: ["[[the-book]]", "[[rust-by-example]]"]
source_urls: ["https://doc.rust-lang.org/book/ch05-03-method-syntax.html", "https://doc.rust-lang.org/std/default/trait.Default.html", "https://doc.rust-lang.org/std/option/enum.Option.html"]
rust_version: "edition 2024 / 1.85+"
---

# Builder Pattern

A builder is a separate construction API that names fields, supplies defaults, and delays validation until all inputs have been collected.

## What it is
Rust has no named or optional function parameters.
For public APIs with several configuration fields, a builder gives callers named setter methods instead of a long positional `new(a, b, c, d)` call.

The ordinary builder stores optional required fields, stores defaulted optional fields directly, and exposes a final `build()` method.
If the required-field set is small and simple, returning `Result` from `build()` is clear enough.
If calling `build()` too early would be an important API bug, consider [[Type-State Pattern]] so the compiler tracks which fields have been supplied.

## How it works
Each setter takes `mut self` and returns `Self`, allowing fluent chaining while still moving the builder.
The final `build()` consumes the builder, validates the accumulated state, and produces the target type.
For simple types, a plain [[Constructor Naming]] pattern such as `new` or `with_capacity` is usually better than a builder.

Consuming setters are the common default because they compose cleanly in chains and make ownership of temporary inputs straightforward.
`&mut self` setters are also valid when callers need to configure a named builder across branches; choose one style and keep it consistent for the builder.
When a setter accepts `impl Into<String>` or `impl AsRef<Path>`, it should convert once and store the representation the final type needs.

The builder's stored shape should reflect what is not known yet.
Required fields are often `Option<T>` until `build()`.
Optional settings can store their real default directly so `build()` is mostly validation instead of a maze of fallback logic.

## Example
```rust
#[derive(Debug, PartialEq, Eq)]
struct HttpClient {
    base_url: String,
    timeout_ms: u64,
    user_agent: Option<String>,
}

#[derive(Default)]
struct HttpClientBuilder {
    base_url: Option<String>,
    timeout_ms: u64,
    user_agent: Option<String>,
}

impl HttpClientBuilder {
    fn base_url(mut self, url: impl Into<String>) -> Self {
        self.base_url = Some(url.into());
        self
    }

    fn timeout_ms(mut self, timeout_ms: u64) -> Self {
        self.timeout_ms = timeout_ms;
        self
    }

    fn user_agent(mut self, user_agent: impl Into<String>) -> Self {
        self.user_agent = Some(user_agent.into());
        self
    }

    fn build(self) -> Result<HttpClient, &'static str> {
        let base_url = self.base_url.ok_or("missing base_url")?;
        Ok(HttpClient { base_url, timeout_ms: self.timeout_ms, user_agent: self.user_agent })
    }
}

fn main() {
    let client = HttpClientBuilder::default()
        .base_url("https://example.com")
        .timeout_ms(1_000)
        .user_agent("rust-client")
        .build()
        .unwrap();

    assert_eq!(client.timeout_ms, 1_000);
}
```

## More realistic example
Use `&mut self` setters when configuration is naturally conditional.
The final API is less fluent but easier to use from ordinary control flow.

```rust
#[derive(Debug, PartialEq, Eq)]
struct RetryPolicy {
    attempts: u8,
    backoff_ms: u64,
}

#[derive(Debug, PartialEq, Eq)]
struct Job {
    name: String,
    retry: RetryPolicy,
}

struct JobBuilder {
    name: Option<String>,
    attempts: u8,
    backoff_ms: u64,
}

impl Default for JobBuilder {
    fn default() -> Self {
        Self { name: None, attempts: 3, backoff_ms: 250 }
    }
}

impl JobBuilder {
    fn name(&mut self, name: impl Into<String>) -> &mut Self {
        self.name = Some(name.into());
        self
    }

    fn retry(&mut self, attempts: u8, backoff_ms: u64) -> &mut Self {
        self.attempts = attempts;
        self.backoff_ms = backoff_ms;
        self
    }

    fn build(self) -> Result<Job, &'static str> {
        let name = self.name.ok_or("missing name")?;
        if self.attempts == 0 {
            return Err("attempts must be nonzero");
        }
        Ok(Job { name, retry: RetryPolicy { attempts: self.attempts, backoff_ms: self.backoff_ms } })
    }
}

fn main() {
    let mut builder = JobBuilder::default();
    builder.name("sync-index");
    if cfg!(debug_assertions) {
        builder.retry(1, 10);
    }
    assert_eq!(builder.build().unwrap().name, "sync-index");
}
```

## Common errors
Moving a consuming builder through a branch and then using it again often triggers:

```text
error[E0382]: use of moved value: `builder`
```

Fix it by rebinding the returned builder in every branch, by using `&mut self` setters, or by making the branch compute only the value passed to one setter.
Do not add `Clone` to the builder just to recover from unclear ownership flow.

## Best practice
- ✅ Use builders when a type has many fields, several optional settings, or a configuration surface that will grow.
- ✅ Keep required-field validation close to `build()` or encode it with [[Type-State Pattern]].
- ✅ Accept flexible inputs in setters with [[From and Into]] or [[AsRef for Flexible Arguments]] when that improves call sites.
- ✅ Keep the constructed type's fields private if the builder enforces invariants.
- ✅ Return a named error type for public builders when callers need to inspect which field failed.
- ✅ Document defaults on the builder methods or type docs, because defaults are part of the public API contract.

## Pitfalls
- ⚠️ Avoid a builder for a two-field type when `new(a, b)` is clearer.
- ⚠️ Do not use a builder to hide invalid states that could be made unrepresentable; see [[Making Invalid States Unrepresentable]].
- ⚠️ Do not make every setter generic by habit; excessive generics can increase compile time and code size.
- ⚠️ Do not expose public builder fields unless skipping setter validation is harmless.
- ⚠️ Avoid silently accepting contradictory options; reject them in `build()` or encode legal combinations with types.

## See also
[[Constructor Naming]] · [[Type-State Pattern]] · [[Making Invalid States Unrepresentable]] · [[Accepting impl Trait vs Generics]] · [[From and Into]] · [[AsRef for Flexible Arguments]] · [[The Default Trait]] · [[Option vs Result]] · [[Idioms & API Design]]

## Sources
- The Rust Programming Language, "Method Syntax" - [[the-book]], https://doc.rust-lang.org/book/ch05-03-method-syntax.html
- `Default` - https://doc.rust-lang.org/std/default/trait.Default.html
- `Option` - https://doc.rust-lang.org/std/option/enum.Option.html
