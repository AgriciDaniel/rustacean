---
type: antipattern
title: "Overbroad Catch-All Match Arms"
status: mature
created: 2026-06-21
updated: 2026-06-21
tags: [rust, match, wildcard, footgun]
domain: "Enums & Pattern Matching"
difficulty: intermediate
related: ["[[Exhaustiveness]]", "[[The match Expression]]", "[[Catch-All and Wildcard Patterns]]", "[[Enums]]", "[[Patterns]]", "[[Enums & Pattern Matching]]"]
sources: ["[[the-book]]"]
source_urls: ["https://doc.rust-lang.org/book/ch06-02-match.html#catch-all-patterns-and-the-_-placeholder", "https://doc.rust-lang.org/book/ch06-02-match.html#matches-are-exhaustive"]
rust_version: "edition 2024 / 1.85+"
---

# Overbroad Catch-All Match Arms

An overbroad catch-all arm uses `_` or a generic binding where explicit cases would let the compiler protect you from missed decisions.

## The mistake
The mistake is ending a match over a domain enum with `_ => ...` before you truly know all remaining variants share one behavior.
The code compiles today, but future variants can silently fall into the fallback.
That defeats much of the value of [[Exhaustiveness]].

This is especially risky for enums you own.
When you add a variant, you usually want the compiler to point at every match that needs an update.
A broad wildcard turns those compiler errors into runtime behavior you may not have intended.

## Why it happens
Catch-all arms are convenient.
They reduce boilerplate, especially while prototyping or when matching large primitive spaces.
They are also required for genuinely open-ended input such as unknown integers or strings.

The problem is using them for closed domain decisions.
If every variant has business meaning, name every variant.
Save `_` for "all remaining values are intentionally identical."

The failure mode is usually delayed. The original match is correct when the enum has three variants.
Months later, a fourth variant is added and the compiler cannot point to this match because `_` still
covers it. The new case silently receives fallback behavior, which is dangerous for audit logs, state
machines, permissions, migrations, and protocol handling.

This antipattern is different from a legitimate fallback for open-ended data. Matching `u16` status
codes, external `#[non_exhaustive]` enums, or user-provided strings often requires a fallback. The
question is whether the fallback is a deliberate domain rule or a way to avoid naming cases.

## Example
```rust
enum ApiEvent {
    Login,
    Logout,
    PasswordReset,
}

fn audit_label(event: ApiEvent) -> &'static str {
    match event {
        ApiEvent::Login => "login",
        ApiEvent::Logout => "logout",
        ApiEvent::PasswordReset => "password-reset",
    }
}

fn main() {
    assert_eq!(audit_label(ApiEvent::PasswordReset), "password-reset");
}
```

## Worked example
```rust
enum InvoiceEvent {
    Created,
    Paid,
    Refunded,
    Voided,
}

fn should_notify_customer(event: InvoiceEvent) -> bool {
    match event {
        InvoiceEvent::Created => true,
        InvoiceEvent::Paid => true,
        InvoiceEvent::Refunded => true,
        InvoiceEvent::Voided => false,
    }
}

fn main() {
    assert!(should_notify_customer(InvoiceEvent::Paid));
    assert!(!should_notify_customer(InvoiceEvent::Voided));
}
```

## Common errors
After adding a variant, the safer explicit match produces:

```text
error[E0004]: non-exhaustive patterns: `ApiEvent::PasswordReset` not covered
```

That error is useful. Fix it by deciding behavior for the new variant. Avoid changing the code to
`_ => ...` unless the fallback is the actual policy for all future cases too.

## Best practice
- ✅ Match every variant explicitly for small enums you own.
- ✅ Use `_` only after deciding the ignored cases are truly equivalent.
- ✅ For external non-exhaustive APIs, use an explicit fallback because the upstream crate may add variants.
- ✅ Group equivalent known variants with `|` so future variants still trigger exhaustiveness errors.
- ✅ In public APIs, document whether unknown/future variants should be ignored, rejected, or logged.

## Pitfalls
- ⚠️ Do not write `_ => "ignored"` on security, persistence, protocol, or billing events without a deliberate policy.
- ⚠️ Do not use a wildcard just to silence a compiler error after adding a variant.
- ⚠️ Do not place the catch-all before specific arms; those arms become unreachable.
- ⚠️ Do not confuse a fallback required by `#[non_exhaustive]` with a fallback in your own closed enum.
- ⚠️ Do not hide `todo!()` behind `_`; it makes every future case fail the same way at runtime.

## See also
[[Exhaustiveness]] · [[The match Expression]] · [[Catch-All and Wildcard Patterns]] · [[Enums]] · [[Patterns]] · [[Enum Variants with Data]] · [[Match Guards]] · [[Sentinel Values]] · [[Pattern Variable Shadowing]] · [[Enums & Pattern Matching]]

## Sources
- The Rust Programming Language, ch. 6.2 "Catch-All Patterns and the _ Placeholder" - [[the-book]], https://doc.rust-lang.org/book/ch06-02-match.html#catch-all-patterns-and-the-_-placeholder
- The Rust Programming Language, ch. 6.2 "Matches Are Exhaustive" - [[the-book]], https://doc.rust-lang.org/book/ch06-02-match.html#matches-are-exhaustive
