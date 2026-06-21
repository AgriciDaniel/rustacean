# Tooling & Project Hygiene

A Rust project that compiles is not the same as a Rust project that is healthy. Hygiene is the set of mechanical, automatable disciplines that keep a codebase buildable, reproducible, and safe to evolve over years. This report is opinionated: for each topic it states the practice to adopt, the mistake that bites teams in practice, and why. It targets stable Rust ~1.85+ and the now-stable Rust 2024 edition [1].

## Cargo Workspaces

A workspace is a set of packages sharing one `Cargo.lock` and one `target/` directory [2]. The single most valuable feature is **inheritance**: define versions, metadata, and dependencies once in the root and pull them into members.

**Good practice — centralize with `[workspace.package]` and `[workspace.dependencies]`.** Declare shared metadata and every third-party dependency at the root, then reference with `.workspace = true` [2]:

```toml
# root Cargo.toml
[workspace]
members = ["crates/*"]
resolver = "3"

[workspace.package]
edition = "2024"
rust-version = "1.85"
license = "MIT OR Apache-2.0"

[workspace.dependencies]
serde = { version = "1", features = ["derive"] }
tokio = { version = "1", default-features = false }
```

```toml
# crates/api/Cargo.toml
[package]
name = "api"
edition.workspace = true
rust-version.workspace = true

[dependencies]
serde.workspace = true
tokio = { workspace = true, features = ["rt-multi-thread"] }
```

Inheriting a dependency guarantees every member uses the *same version*, which saves build time and disk and prevents incompatible duplicate copies in the dependency graph [3].

**Mistake to avoid — per-crate version drift.** Letting each member pin `serde = "1.0.190"` independently invites multiple semver-compatible versions to coexist, bloating builds and occasionally producing two incompatible `serde::Serialize` traits at type boundaries. Centralization is the cure.

**Edition-2024 gotcha:** you may no longer set `default-features = false` on an *inherited* dependency in a member unless the workspace declared it; specify `default-features = false` in `[workspace.dependencies]` and let members opt features back in [4]. The 2024 resolver also rejects this combination as an error rather than silently ignoring it [4].

## Feature Flags & Additive Features

Cargo unifies features: a crate is compiled with the **union** of every feature requested anywhere in the build graph [5]. With *N* independent features, all 2^N combinations can occur in practice [5].

**Good practice — keep features strictly additive.** A feature should only *add* capability, never remove or change behavior [5][6]. Enabling a feature must never cause a different feature's code to stop compiling or behave differently — because the consumer enabling feature `A` and a transitive dependency enabling feature `B` will get both, and neither can opt out of the other's effects [5].

**Mistake to avoid — mutually exclusive features.** A common anti-pattern is `features = ["std"]` and `features = ["no_std"]` as opposites. Because features unify, some crate deep in the graph enabling `std` forces it on everyone, and a `#[cfg(feature = "no_std")]` build breaks with no way to recover [5][6]. Model the default as the additive case (`std` on by default, `no_std` expressed as `default-features = false`) instead.

**Mistake to avoid — feature-gating public items carelessly.** Putting a public struct field or trait method behind a non-default feature, or *removing* a feature in a minor release, is a SemVer break: downstream code that depended on the feature stops compiling [6][7]. Removing a feature from the `default` set is likewise breaking [7]. If you must reduce features, do it in a major release.

## Clippy: Lints Worth Enabling

Clippy ships 550+ lints in groups: `correctness` and `style` (on by default), plus opt-in `pedantic`, `nursery`, `cargo`, and `restriction` [8][9].

**Good practice — enable `pedantic` and `cargo` at the workspace level, then allow exceptions.** Configure once in the root manifest so every member inherits it [9]:

```toml
[workspace.lints.clippy]
pedantic = { level = "warn", priority = -1 }
cargo = { level = "warn", priority = -1 }
# targeted allows for the few pedantic lints you reject:
module_name_repetitions = "allow"
```

```toml
# each member:
[lints]
workspace = true
```

The negative `priority` is required so that group-level settings apply *before* individual lint overrides [9]. `pedantic` catches real readability and correctness smells (e.g. `must_use_candidate`, `needless_pass_by_value`), and `cargo` flags manifest problems like missing metadata or wildcard dependencies [8].

**Mistake to avoid — enabling the whole `nursery` or `restriction` group.** `nursery` lints are unstable and known to have false positives; the Clippy maintainers explicitly advise against enabling the group wholesale and recommend cherry-picking individual lints instead [8]. `restriction` is even more extreme — many of its lints are mutually contradictory and are meant to be opted into one at a time, never as a group [8].

**Mistake to avoid — `#[allow(...)]` scattered everywhere.** Prefer `#[expect(...)]` (stable since 1.81): it warns if the lint *stops* firing, so stale suppressions get cleaned up automatically [8].

## rustfmt

**Good practice — commit a `rustfmt.toml` and enforce `cargo fmt --check` in CI.** Pin both `edition` and `style_edition` explicitly; when invoked directly (as some CI scripts do) `rustfmt` defaults to edition 2015 and may format differently than `cargo fmt`, which reads the edition from `Cargo.toml` [10]. Keep formatting decisions out of code review entirely — a formatter that runs everywhere makes "style nits" disappear.

**Mistake to avoid — relying on nightly-only options in a stable workflow.** Useful options such as `imports_granularity` and `group_imports` are still unstable and require a nightly toolchain plus `unstable_features = true` [10][11]. If your CI uses stable, those keys silently do nothing locally and surprise contributors. Either run `cargo +nightly fmt` for formatting specifically (a widespread pattern) or restrict yourself to stable options [11]. Decide deliberately and document it.

## MSRV Policy

The `rust-version` field declares the Minimum Supported Rust Version; building on an older toolchain becomes a hard error with a clear message rather than a confusing diagnostic [12].

**Good practice — declare `rust-version` and adopt resolver 3.** Set an explicit MSRV and a written support policy: common choices are "N-2" (latest minus two releases), every even release, or a one-year window [12]. Then enable the **MSRV-aware resolver**, stabilized in 1.84 and default for edition 2024 [13][1]. It prefers dependency versions compatible with your declared `rust-version`, so you no longer hand-pin old dependency versions to keep an old toolchain working [13]. Opt in without raising your edition via `.cargo/config.toml`:

```toml
[resolver]
incompatible-rust-versions = "fallback"
```

or set `resolver = "3"` in the manifest (which itself requires Rust 1.84+) [13]. The Clippy `incompatible_msrv` lint flags standard-library calls newer than your MSRV [12].

**Mistake to avoid — claiming an MSRV you do not test.** A declared `rust-version` is a *commitment*: the package must be complete and verified on that toolchain, ideally with a CI job pinning the exact MSRV (`dtolnay/rust-toolchain@1.85`) [12]. An untested MSRV rots immediately the first time someone uses a newer `std` method. Raising MSRV is treated as a minor (not major) SemVer change by convention, so you can bump it when your policy allows — but do it deliberately, not accidentally [12][7].

## Edition 2024 Migration

Rust 2024 shipped with 1.85.0 and is the largest edition to date [1]. Migration is mechanical for most projects.

**Good practice — migrate with `cargo fix --edition`.** Run it, then bump `edition = "2024"`, then `cargo build`/`cargo test` to confirm [14]. The automated fixes are deliberately conservative — they never change semantics — so anything they cannot safely rewrite is printed as a warning for you to handle by hand [14].

Notable behavior changes to review manually: RPIT (`impl Trait` in return position) now captures all in-scope generic parameters by default unless `use<..>` says otherwise; `if let` temporary scope and tail-expression temporary drop order changed; `extern` blocks must be written `unsafe extern`; never-type fallback changed and its lint is now deny-level; and `Future`/`IntoFuture` joined the prelude [1][15].

**Mistake to avoid — migrating a whole workspace in one shot.** Editions are per-crate and fully interoperable across the dependency graph [16], so migrate member by member, committing each, rather than flipping every crate at once and drowning in mixed diffs. Also re-run your full test suite — `cargo fix` cannot catch behavioral changes like altered drop timing [14].

## CI Setup

**Good practice — a fast, layered GitHub Actions pipeline.** Use the maintained `dtolnay/rust-toolchain` action and `Swatinem/rust-cache` for dependency/artifact caching; the older `actions-rs/*` family is unmaintained and buggy [17]. A pragmatic gate set:

```yaml
- uses: dtolnay/rust-toolchain@stable
  with: { components: rustfmt, clippy }
- uses: Swatinem/rust-cache@v2
- run: cargo fmt --all --check
- run: cargo clippy --all-targets --all-features -- -D warnings
- run: cargo test --all-features   # or: cargo nextest run
```

`-D warnings` turns any Clippy or compiler warning into a build failure, so warnings cannot accumulate [17]. Put cheap checks (fmt) first and use `needs:` so an expensive test matrix is skipped when formatting fails [17]. Add a separate job pinned to your MSRV toolchain, and run `cargo doc` with `RUSTDOCFLAGS="-D warnings"` to catch broken intra-doc links.

**Mistake to avoid — testing only on `stable` with `--all-features` and calling it done.** Feature unification means a green `--all-features` build can still hide a broken individual feature combination [5]. Test the default feature set, `--no-default-features`, and key combinations; tools like `cargo-hack` automate the matrix.

## cargo-nextest

`cargo-nextest` is a drop-in test *runner* that is up to 3× faster than `cargo test` and adds capabilities the built-in runner lacks [18].

**Good practice — adopt nextest for any non-trivial test suite, especially in CI.** It runs each test in its own process, giving true isolation for tests that touch global state, the filesystem, or external resources; `cargo test` can only run separate test *binaries* serially, while nextest parallelizes across them [18]. It also auto-detects and optionally retries flaky tests, flags slow/leaky tests (processes the test failed to clean up — usually a real bug), and emits JUnit XML/JSON for CI dashboards [18].

**Mistake to avoid — assuming nextest runs doctests.** Nextest does **not** execute documentation tests [18]; keep a `cargo test --doc` step alongside `cargo nextest run` so doctests are still verified.

## Documentation Tests

Doctests compile and run the code in your `///` examples, so they are tests *and* always-correct documentation in one [19].

**Good practice — write doctests as complete, runnable programs and hide the boilerplate.** Lines prefixed with `# ` are compiled but hidden from rendered output, letting you show only the meaningful lines while keeping the example a full program [19]:

```rust
/// Doubles a number.
/// ```
/// # use mycrate::double;
/// assert_eq!(double(3), 6);
/// ```
```

Examples may end with `?` if the hidden wrapper returns a `Result`; for code that must compile but should not execute (network calls, `panic!` demos), annotate the fence with `no_run` (compiles, doesn't run) or `compile_fail`/`should_panic` as appropriate [19][20].

**Mistake to avoid — `ignore` to silence a failing doctest.** `ignore` removes both compilation and execution, so the example silently rots until it no longer even compiles [20]. Reach for `no_run` (still type-checked) instead, and reserve `ignore` for genuinely non-Rust fences. Also remember doctests do not run under nextest (above) — wire `--doc` into CI.

## SemVer Discipline

Accidental SemVer violations are common — a lower bound of ~3% of releases — and happen to maintainers of every skill level [21]. The Cargo SemVer reference is the canonical classification of what is breaking [7].

**Good practice — run `cargo-semver-checks` before every publish.** It compares your crate's public API against the last published version using rustdoc and tells you whether the change is patch/minor/major, failing if your version bump is too small [21]. Wire it into CI and pre-publish. The cargo team intends to fold it into `cargo publish` itself [21].

**Defensive API design that buys you headroom** [7]:

- Mark enums and structs `#[non_exhaustive]` from day one. Adding a variant or field later is then *minor* instead of *major* [7].
- Keep at least one private field in structs so adding fields stays minor (callers can't use struct-literal construction anyway) [7].
- Give every new trait method a default implementation; an undefaulted method is a breaking change for all implementors [7].

**Mistakes to avoid (all are silent major breaks):** adding a variant to a plain `enum`; adding any field to an all-public struct; adding a non-defaulted trait method; tightening a generic bound (e.g. adding `T: Copy`) so previously-valid callers no longer compile; or retroactively adding `#[non_exhaustive]` to an all-public type [7]. Loosening bounds, generalizing a function while still accepting the old type, and making an `unsafe fn` safe are all *minor* and safe to do [7].

## The Hygiene Checklist

Adopt these once and they pay forever: workspace inheritance for versions and deps; `pedantic` + `cargo` Clippy at workspace level with `#[expect]` over `#[allow]`; committed `rustfmt.toml` enforced in CI; additive-only features tested across combinations; an explicit, CI-verified MSRV with resolver 3; edition 2024 migrated crate-by-crate; a layered CI that denies warnings; nextest for the suite plus `--doc` for doctests; and `cargo-semver-checks` guarding every release.

## Sources

[1] Announcing Rust 1.85.0 and Rust 2024 — Rust Blog: https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/
[2] Workspaces — The Cargo Book: https://doc.rust-lang.org/cargo/reference/workspaces.html
[3] Cargo Workspaces — The Rust Programming Language: https://doc.rust-lang.org/book/ch14-03-cargo-workspaces.html
[4] Cargo: Reject unused inherited default-features — The Rust Edition Guide: https://doc.rust-lang.org/edition-guide/rust-2024/cargo-inherited-default-features.html
[5] Features — The Cargo Book: https://doc.rust-lang.org/cargo/reference/features.html
[6] Item 26: Be wary of feature creep — Effective Rust: https://effective-rust.com/features.html
[7] SemVer Compatibility — The Cargo Book: https://doc.rust-lang.org/cargo/reference/semver.html
[8] rust-clippy README and lint groups — GitHub: https://github.com/rust-lang/rust-clippy
[9] Clippy Configuration / lints in Cargo.toml — Clippy Documentation: https://doc.rust-lang.org/clippy/configuration.html
[10] Rustfmt Configurations — GitHub: https://github.com/rust-lang/rustfmt/blob/main/Configurations.md
[11] Rustfmt configuration docs: https://rust-lang.github.io/rustfmt/
[12] Rust version (MSRV) — The Cargo Book: https://doc.rust-lang.org/cargo/reference/rust-version.html
[13] Cargo: Rust-version aware resolver — The Rust Edition Guide: https://doc.rust-lang.org/edition-guide/rust-2024/cargo-resolver.html
[14] Transitioning an existing project to a new edition — The Rust Edition Guide: https://doc.rust-lang.org/edition-guide/editions/transitioning-an-existing-project-to-a-new-edition.html
[15] Additions to the prelude (Rust 2024) — The Rust Edition Guide: https://doc.rust-lang.org/edition-guide/rust-2024/prelude.html
[16] What are editions? — The Rust Edition Guide: https://doc.rust-lang.org/edition-guide/editions/
[17] GitHub Actions — Rust Project Primer / Clippy CI docs: https://rustprojectprimer.com/ci/github.html
[18] cargo-nextest documentation: https://nexte.st/
[19] Documentation testing — Rust By Example: https://doc.rust-lang.org/rust-by-example/testing/doc_testing.html
[20] Documentation tests — The rustdoc Book: https://doc.rust-lang.org/rustdoc/documentation-tests.html
[21] cargo-semver-checks — GitHub: https://github.com/obi1kenobi/cargo-semver-checks

## Verification notes

Adversarially fact-checked on 2026-06-21 against current stable Rust (1.85+) and the now-stable Rust 2024 edition. A sample of cited URLs was fetched and cross-checked, and questionable claims were searched for the current truth. The report is substantially accurate and current; every load-bearing technical claim verified. Only minor precision/citation nits were found, none of which change the report's guidance:

1. **Clippy group defaults — minor imprecision (line 57).** The report says `correctness` and `style` are "on by default," grouping them together. More precisely, `correctness` is *deny*-by-default (it aborts compilation when triggered), whereas `style` is *warn*-by-default. Both are indeed enabled by default, so the report is not wrong, but the two groups differ in level. Source: https://doc.rust-lang.org/stable/clippy/lints.html and https://github.com/rust-lang/rust-clippy

2. **SemVer ~3% statistic — citation could be more precise (lines 157, 159, 195).** The "~3% of releases" figure and the "cargo team intends to fold it into `cargo publish`" claim are both *correct*, but neither appears on the cited cargo-semver-checks README [21]. The canonical source for both is the Rust Project Goals documentation, where folding cargo-semver-checks into cargo is a tracked 2026 goal that explicitly cites the lower-bound ~3% accidental-violation rate. Recommend adding: https://rust-lang.github.io/rust-project-goals/2026/cargo-semver-checks.html

No outdated or incorrect claims were found. Specifically confirmed as current/accurate: Rust 2024 shipped with 1.85.0 and is "the largest edition" [1]; the MSRV-aware resolver was stabilized in 1.84, `resolver = "3"` is the edition-2024 default and requires Rust 1.84+ (https://doc.rust-lang.org/edition-guide/rust-2024/cargo-resolver.html); the `.cargo/config.toml` key is `[resolver] incompatible-rust-versions` (plural, value `"fallback"`) (https://doc.rust-lang.org/cargo/reference/config.html); inherited `default-features = false` is now a hard error in 2024 (https://doc.rust-lang.org/edition-guide/rust-2024/cargo-inherited-default-features.html); `#[expect]` is stable since 1.81 (https://blog.rust-lang.org/2024/09/05/Rust-1.81.0/); rustfmt defaults to edition 2015 when invoked directly and `imports_granularity`/`group_imports` remain nightly-only/unstable (https://github.com/rust-lang/rustfmt/blob/main/Configurations.md); nextest is "up to 3× faster," runs per-test processes, does not run doctests (https://nexte.st/); and the listed edition-2024 behavior changes (RPIT capture, `if let` temporary scope, `unsafe extern`, never-type-fallback deny lint, `Future`/`IntoFuture` in prelude) are all confirmed (https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/).
