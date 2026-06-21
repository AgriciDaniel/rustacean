---
type: pattern
title: "Configuration Loading"
status: developing
created: 2026-06-21
updated: 2026-06-21
tags: [rust, configuration, config, figment, serde, ecosystem]
domain: "Ecosystem & Crate Playbooks"
difficulty: intermediate
related: ["[[Command-Line Parsing]]", "[[Serde Data Format Playbook]]", "[[Application Errors with anyhow]]", "[[Feature Flags]]", "[[Ecosystem & Crate Playbooks]]"]
sources: ["[[tooling-project-hygiene]]", "docs.rs/config", "docs.rs/figment", "serde derive guide"]
source_urls: ["https://docs.rs/config/latest/config/", "https://docs.rs/config/latest/config/struct.Config.html", "https://docs.rs/figment/latest/figment/", "https://docs.rs/figment/latest/figment/struct.Figment.html", "https://docs.rs/serde/latest/serde/", "https://serde.rs/derive.html"]
rust_version: "edition 2024 / 1.85+"
---

# Configuration Loading

Configuration loading is the pattern of merging defaults, files, environment variables, and sometimes CLI values into one validated Rust type before application work begins.

## What it is
Applications often need settings that vary by environment.
Examples include bind addresses, database URLs, log filters, retry counts, timeouts, feature toggles, and file paths.
Those settings may come from compiled defaults, config files, environment variables, command-line flags, or test fixtures.

The idiomatic Rust shape is a typed configuration struct.
Use `serde` to deserialize external values into that struct.
Use a crate such as `config` or `figment` when you need layered sources.
Then validate cross-field invariants and pass a borrowed `&Settings` or narrower sub-configs into the rest of the program.

Configuration is not a global variable by default.
Load it near `main`, report clear errors, and inject it into components.
This keeps tests deterministic and keeps library crates independent from process environment and filesystem policy.

## How it works
The `config` crate builds a prioritized repository from sources.
It supports defaults, files, environment variables, string literals, other `Config` values, and programmatic overrides.
After sources are added, call `build`, then `try_deserialize` into a typed value.
It is a straightforward choice for conventional application configuration.

The `figment` crate combines providers and tracks metadata about where values came from.
It distinguishes `merge` and `join` conflict behavior.
`merge` lets later providers replace existing values.
`join` fills holes without replacing existing values.
Figment is useful when provenance, profiles, or library-provided configuration composition matter.

Both crates rely on feature flags for file formats and providers.
For example, TOML support and environment providers may require explicit features.
Centralize those features in a workspace when several crates need them.
Verify latest crate versions and feature names on docs.rs before editing dependencies.
On 2026-06-21, docs.rs `latest` resolved to config 0.15.24 and figment 0.10.19; recheck before using these dependency lines.

## Example
```rust
use config::{Config, File, FileFormat};
use serde::Deserialize;

#[derive(Debug, Deserialize, PartialEq, Eq)]
struct Settings {
    host: String,
    port: u16,
    workers: usize,
}

fn load_settings() -> Result<Settings, config::ConfigError> {
    Config::builder()
        .set_default("host", "127.0.0.1")?
        .set_default("workers", 4)?
        .add_source(File::from_str(
            r#"
            port = 8080
            workers = 8
            "#,
            FileFormat::Toml,
        ))
        .build()?
        .try_deserialize()
}

fn main() -> Result<(), config::ConfigError> {
    let settings = load_settings()?;

    assert_eq!(
        settings,
        Settings {
            host: "127.0.0.1".to_owned(),
            port: 8080,
            workers: 8,
        }
    );

    Ok(())
}
```

Cargo dependencies for this example:
```toml
[dependencies]
config = { version = "0.15", features = ["toml"] }
serde = { version = "1", features = ["derive"] }
```

## Figment shape
Use Figment when source provenance and explicit conflict strategy matter:

```rust
use figment::{
    providers::{Format, Serialized, Toml},
    Figment,
};
use serde::{Deserialize, Serialize};

#[derive(Debug, Deserialize, Serialize)]
struct Settings {
    port: u16,
}

fn figment() -> Figment {
    Figment::from(Serialized::defaults(Settings { port: 8080 }))
        .merge(Toml::string("port = 9000"))
}
```

Cargo dependencies for the Figment shape:
```toml
[dependencies]
figment = { version = "0.10", features = ["toml"] }
serde = { version = "1", features = ["derive"] }
```

## Layering order
Pick a precedence order and document it.
A common order is:
compiled defaults, default config file, environment-specific config file, environment variables, then command-line overrides.
This gives operators a predictable override ladder.

Avoid reading environment variables all over the codebase.
The process environment is global mutable input from the program's point of view.
Collect it once during startup, deserialize it, validate it, and pass typed values inward.
For tests, prefer string or temporary-file sources so test cases do not depend on the developer's shell.

## Best practice
- ✅ Deserialize into a typed settings struct with `serde`.
- ✅ Load configuration at startup and pass it explicitly to components.
- ✅ Use defaults for non-secret operational values.
- ✅ Validate cross-field rules after deserialization.
- ✅ Keep secrets out of logs, panic messages, and derived `Debug` output.
- ✅ Document source precedence and environment variable prefixes.
- ✅ Prefer optional config files only when missing files are truly acceptable.
- ✅ Verify `config`, `figment`, and format-provider feature flags on docs.rs before dependency updates.

## Pitfalls
- ⚠️ Reading `std::env::var` deep inside library code.
- ⚠️ Treating every configuration value as `String` and parsing repeatedly at use sites.
- ⚠️ Logging the whole settings struct when it may contain credentials.
- ⚠️ Letting command-line flags, config files, and environment variables use inconsistent names.
- ⚠️ Making config files silently optional in production when the application cannot run safely without them.
- ⚠️ Mixing precedence rules across modules so later overrides are unpredictable.
- ⚠️ Forgetting that crate provider and format support often depends on [[Feature Flags]].

## See also
[[Ecosystem & Crate Playbooks]] · [[Command-Line Parsing]] · [[Serde Data Format Playbook]] · [[Application Errors with anyhow]] · [[Adding Error Context]] · [[Feature Flags]] · [[Cargo Workspaces]] · [[Workspace Dependency Inheritance]] · [[The Debug Trait]] · [[Stringly-Typed Code]] · [[Choosing the Right Rust Crate]] · [[Minimizing Dependencies]]

## Sources
- config crate docs — https://docs.rs/config/latest/config/; verify the latest version before editing `Cargo.toml`.
- config `Config` docs — https://docs.rs/config/latest/config/struct.Config.html
- figment crate docs — https://docs.rs/figment/latest/figment/; verify the latest version before editing `Cargo.toml`.
- figment `Figment` docs — https://docs.rs/figment/latest/figment/struct.Figment.html
- Serde derive guide — https://serde.rs/derive.html
- Tooling and project hygiene — [[tooling-project-hygiene]].
- Latest-version check: docs.rs `latest` resolved to config 0.15.24 and figment 0.10.19 on 2026-06-21; verify again before dependency updates.
