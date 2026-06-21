# Dependency & Supply-Chain Security

Rust's safety story stops at the language boundary. `cargo` will happily pull in
hundreds of transitive crates, run their `build.rs` scripts and proc-macros inside
your compiler, and link their code into your binary — all with no mandatory review,
no sandbox, and the full privileges of whoever runs `cargo build`. The borrow
checker does nothing about a dependency that exfiltrates your SSH keys at build
time. Supply-chain security is therefore a *separate discipline* layered on top of
memory safety, and in 2024–2026 it has become a first-class concern for the Rust
project itself, with real malware appearing on crates.io and new platform defenses
shipping in response.[1][2]

This report is opinionated and practical. Each section gives the good practice, the
common mistake, the rationale, and (where useful) a sketch.

## The threat model: why Rust isn't special

Rust shares npm's worst structural property: dependencies can execute arbitrary code
on the developer's and CI machine, not just at runtime but *at build time*. Build
scripts (`build.rs`) and procedural macros run inside the compiler with full
filesystem and network access, using the permissions of the developer or CI
runner.[3] A proc-macro can read environment variables (your `AWS_SECRET_ACCESS_KEY`,
your crates.io token) during macro expansion and POST them to an attacker.[3] crates.io
has *no mandatory code review* — anyone can publish anything — and there is no Go-style
module-proxy quarantine or npm-style audit gate by default.[3]

The 2025 incidents made this concrete. In September 2025 the crates.io team removed
`faster_log` and `async_println`, typosquats of the popular `fast_log` crate that
cloned its source, features, and docs verbatim, then scanned files for Ethereum and
Solana private keys and exfiltrated them to a C2 server. They were downloaded 7,181
and 1,243 times respectively (8,424 total) and lived undetected for four
months.[1] Notably, the payload ran *at runtime*, not build time — so build-script
sandboxing alone would not have caught it.[1] A December 2025 pair (`finch-rust`,
`sha-rust`) and the April 2025 `evm-units` crate (>7,000 downloads) repeated the
pattern.[2]

**Mistake to avoid:** assuming "it's Rust, it's safe." The safety model covers
undefined behavior, not malice or compromised maintainers. Treat every dependency as
code you are choosing to run with your privileges.

## cargo-audit + the RustSec advisory database

`cargo-audit` reads your `Cargo.lock` and compares every locked version against the
[RustSec Advisory Database](https://rustsec.org), a community-maintained repository of
security advisories for crates published on crates.io.[4][5] RustSec mirrors its data
into the OSV (Open Source Vulnerabilities) format in real time, so the same advisories
feed Trivy, Dependabot, GitHub's Security tab, and others.[4]

**Good practice:** run it in CI on every PR and on a schedule (advisories appear
*after* you've already shipped a version, so a nightly run catches newly disclosed
issues in code you haven't touched).

```yaml
# .github/workflows/audit.yml
- run: cargo install cargo-audit --locked
- run: cargo audit --deny warnings
```

**Mistake to avoid:** running `cargo audit` only locally, or treating its output as
advisory. Without `--deny warnings` (or the equivalent in `cargo-deny`), unmaintained
and yanked-crate warnings get ignored until they become exploits. Equally, do *not*
blanket-ignore advisories with `--ignore RUSTSEC-XXXX` without a tracked reason and an
expiry — silent ignores rot.

Note `cargo-audit` only knows about *disclosed* vulnerabilities. The `faster_log`
malware was never in RustSec until after discovery, so audit tooling is necessary but
not sufficient — it is a lagging indicator.[1]

## cargo-deny: the policy gate

Where `cargo-audit` answers "are any of my deps known-vulnerable?", `cargo-deny`
(EmbarkStudios) is a configurable *policy linter* with four independent checks driven by
a `deny.toml`:[6][7]

- **advisories** — wraps the RustSec DB; also flags `unmaintained` and `unsound` crates.
- **bans** — deny/allow specific crates, ban duplicate versions, ban wildcard (`*`)
  version requirements.
- **licenses** — allowlist acceptable SPDX licenses with a confidence threshold for
  inferred ones.
- **sources** — restrict where crates may come from (e.g. only crates.io, only
  specific git orgs).[7]

```toml
# deny.toml
[advisories]
unmaintained = "workspace"   # flag unmaintained first-party-reachable deps
yanked = "deny"

[bans]
multiple-versions = "warn"
wildcards = "deny"           # forbid "*" requirements
deny = [
  { crate = "openssl", use-instead = "rustls" },
]

[licenses]
allow = ["MIT", "Apache-2.0", "ISC", "BSD-3-Clause"]
confidence-threshold = 0.93

[sources]
unknown-registry = "deny"
unknown-git = "deny"
```

**Good practice:** make `sources.unknown-git = "deny"` and `bans.wildcards = "deny"`
non-negotiable. A `git = "..."` dependency or a `*` requirement is an open door for an
attacker who controls (or later compromises) that endpoint. cargo-deny ships its own
config as a worked example — it bans `git2`/`openssl` in favor of `gix`/`rustls`.[7]
2025 added useful knobs: `bans.allow-workspace`, `licenses.include-build`, and
`advisories.unsound`.[6]

**Mistake to avoid:** treating cargo-deny's license check as security theater and
allow-listing everything. License non-compliance is a real legal supply-chain risk,
and a sudden license change in a transitive dep is also a useful *signal* that
something changed upstream.

## cargo-vet: positive auditing at scale

`cargo-audit`/`cargo-deny` are *negative* — they catch known-bad. `cargo-vet`
(Mozilla) is *positive*: it ensures every third-party dependency has been **audited by
a trusted entity** before it can enter your tree.[8] Audits are stored in-tree
(`supply-chain/audits.toml`), so developers never authenticate with an external system,
and you can *import* audits from organizations you trust — Mozilla, Google, etc. — so
the ecosystem shares the auditing burden rather than everyone re-reviewing
`serde`.[8][9]

The killer feature for adoption is **exemptions**: when you first run `cargo vet`, your
existing deps are added to an exception list you can ratchet down over time, so onboarding
is trivial while still gating *new* additions and *upgrades*.[8] cargo-vet's diff-based
audits mean reviewing `1.0.3 → 1.0.4` is a small diff review, not a full re-audit.[8]

**Good practice:** adopt cargo-vet with full exemptions on day one, then make CI fail on
any *unvetted new dependency or version bump*. This turns "did anyone look at this code?"
from a vibe into a tracked invariant.

**Mistake to avoid:** trying to reach 100% coverage immediately, getting overwhelmed,
and abandoning it. The whole design philosophy is incrementalism — exemptions exist
precisely so you don't have to boil the ocean.[8] Also avoid importing audits from
entities you can't actually justify trusting; a transitive trust relationship is still
trust.

`cargo-vet` and `cargo-deny` are complementary, not competing: vet covers "has a human
looked at this?", deny covers "does this match my policy + known advisories?"

## Minimizing dependency surface

The cheapest dependency to secure is the one you don't have. Every crate is more
`build.rs`, more proc-macros, more maintainers who could be compromised, more code you'd
have to vet.

**Good practice:**
- Prune *unused* deps with `cargo-machete` (fast regex scan, stable toolchain) or
  `cargo-udeps` (compiler-accurate, needs nightly).[10] `cargo-machete` is great for CI
  because it's fast; be aware its text matching produces false positives for deps used
  only via proc-macros or `build.rs`, so maintain an ignore list.[10] `cargo-shear` also
  finds misplaced dev/build deps.[10]
- Trim **feature flags**: `default-features = false` and enable only what you use. A
  default feature often drags in `tokio`, `openssl`, or `serde_derive` you don't need.
- Prefer the std library or a small focused crate over a mega-framework when the need is
  small.

```toml
# pull in only what you use
reqwest = { version = "0.12", default-features = false, features = ["rustls-tls", "json"] }
```

**Mistake to avoid:** adding a heavyweight crate for a ten-line utility (the
`left-pad`/`is-even` antipattern), or copy-pasting `Cargo.toml` snippets that enable all
default features. Audit your `cargo tree` periodically — duplicate versions of the same
crate (caught by `cargo-deny`'s `multiple-versions`) bloat the surface and the binary.

## Vetting individual crates before you add them

Before `cargo add somecrate`, do a quick trust pass:

- **Provenance & popularity:** download counts, reverse-deps, whether it's in
  Mozilla/Google's audit set. crates.io now surfaces a **Security tab** showing RustSec
  advisories directly on the crate page.[11]
- **Maintenance:** recent commits, responsive issues, more than one maintainer (bus
  factor). An `unmaintained` flag from cargo-deny is a yellow card.
- **Build-time code:** does it ship a `build.rs` or proc-macros? That's the highest-risk
  surface (next section).
- **Source ↔ registry match:** does the published crate actually correspond to the git
  repo? (Reproducible builds, below, are how you *verify* this rather than assume it.)

**Mistake to avoid:** picking by download count alone. The malicious typosquats had
thousands of downloads.[1][2] Download numbers measure popularity, not safety — and
crates.io itself now filters bot/scraper traffic precisely because the raw numbers were
gameable.[11] Also avoid trusting the *name*: `tokio-utils` vs `tokio_utils`, `serde-yaml`
vs `serde_yaml` — confirm the exact crate and author you intend.

## Typosquatting risks

Typosquatting is the dominant *named* attack on crates.io: clone a popular crate, change
one character or a `-`/`_`, copy the README so it looks legit, wait. `faster_log` mimicked
`fast_log`; the historical `rustdecimal` mimicked `rust_decimal`.[1] crates.io applies
some name-similarity restrictions, but they are not a complete defense.

**Good practice:** pin exact crate names in review, prefer `cargo add <name>` (which
resolves the canonical name) over hand-typing into `Cargo.toml`, and lock down sources so a
typo can't silently resolve to a different registry. Adopt a **version cooldown** habit:
don't auto-upgrade to a brand-new release on the day it's published. crates.io is building
infrastructure for this — the new `pubtime` index field exists to support future Cargo
cooldown features.[11]

**Mistake to avoid:** copy-pasting dependency lines from a blog post or LLM output without
verifying the crate exists and is the real one. Many malicious crates are seeded
specifically to catch fat-fingered or AI-hallucinated names.

## build.rs and proc-macro trust

This is the sharpest edge. `build.rs` runs at *every* `cargo build`; proc-macros run
inside `rustc` (and inside `rust-analyzer` in your editor — there's an open issue about
exactly this arbitrary-code-execution-on-open vector).[3] Both have full ambient
authority. There is currently **no built-in sandbox**; sandboxing build scripts and
proc-macros (via Wasm, Miri, or the CTFE engine) has been repeatedly proposed in Rust
internals but is not yet shipped.[3]

**Good practice:**
- Treat any dependency with a `build.rs` or proc-macros as requiring *human review*
  (this is exactly what `cargo-vet` formalizes).
- Run untrusted builds in a disposable, network-restricted container or VM, *especially*
  in CI. Don't expose long-lived secrets to the build environment; use short-lived,
  least-privilege credentials.
- Prefer crates that *don't* need build-time codegen when a pure-library alternative
  exists.

**Mistake to avoid:** running `cargo build` / `cargo test` on an untrusted repo on your
main workstation with your real environment loaded. The `faster_log` payload was runtime,
but build-time payloads are equally possible and strictly more dangerous because `cargo
test` triggers them before you've inspected anything.[1][3] Also: storing your crates.io
token or cloud secrets as plain env vars in a build that pulls untrusted deps hands them
to any malicious proc-macro.

## Publishing securely: trusted publishing & lockfiles

If *you* publish crates, the supply chain includes your release pipeline. crates.io now
supports **Trusted Publishing** via OIDC (RFC 3691): your CI exchanges a short-lived
(e.g. 15-minute) OIDC token for a scoped publish token, so there is no long-lived
crates.io API token to leak.[12][13] As of the Jan 2026 update, owners can **enforce**
trusted-publishing-only mode (disabling classic API tokens entirely), GitLab CI is
supported alongside GitHub Actions, and the dangerous `pull_request_target` /
`workflow_run` triggers are blocked.[14][11]

**Good practice:** enable trusted publishing, enforce it, and pin the *exact* claims
(repo, workflow, environment) allowed to publish. Commit `Cargo.lock` for binaries and
applications so builds are reproducible and auditable.

**Mistake to avoid:** keeping a long-lived `CARGO_REGISTRY_TOKEN` in CI secrets when
trusted publishing is available — that token is a single credential that publishes
*anything* under your name. For libraries, also avoid the reflex of *not* committing
`Cargo.lock`; while historically debated for libs, committing it aids reproducible
auditing of *your* CI.

## Reproducible builds

Reproducible (deterministic) builds let anyone recompile the source and get a
bit-identical artifact, which is how you *verify* that a published binary or crate
actually corresponds to its source rather than trusting the publisher.[15] As of 2024,
Rust does not produce reproducible builds fully out of the box; the practical recipe is to
pin the exact toolchain and tools (often via a tagged Docker image) and set
`SOURCE_DATE_EPOCH` to fix timestamps.[15][16] There is active work toward a crates.io
service that verifies a crate's sources reproduce its published artifact before the
release becomes available.[15]

**Good practice:** pin `rust-toolchain.toml`, build release artifacts in a controlled
container, set `SOURCE_DATE_EPOCH`, and (for high-assurance projects) verify a rebuild
matches the published hash.

**Mistake to avoid:** shipping binaries whose provenance can't be reproduced, then having
no way to prove a tampered artifact from a legitimate one after an incident.

## A pragmatic baseline

For most teams, a defensible 2026 baseline is:

1. CI runs `cargo audit --deny warnings` on every PR **and** nightly.
2. `cargo-deny` with `sources`/`wildcards`/`licenses` enforced.
3. `cargo-vet` adopted with exemptions, gating new deps and upgrades.
4. `cargo-machete` in CI to keep the surface minimal.
5. Untrusted builds sandboxed; no real secrets in build envs.
6. Trusted publishing enforced for anything you ship; `Cargo.lock` committed.
7. A version-cooldown habit so you're never the first to run a fresh release.

No single tool is sufficient — audit is lagging, deny is policy, vet is human review,
sandboxing is containment, and trusted publishing protects your outbound side. Layer
them.

## Sources

1. Rust Blog — *crates.io: Malicious crates faster_log and async_println* (2025-09-24): https://blog.rust-lang.org/2025/09/24/crates.io-malicious-crates-fasterlog-and-asyncprintln/
2. The Hacker News — *Malicious Rust Crates Steal Solana and Ethereum Keys* (2025): https://thehackernews.com/2025/09/malicious-rust-crates-steal-solana-and.html
3. Rust Internals — *Sandbox build.rs and proc macros*: https://internals.rust-lang.org/t/sandbox-build-rs-and-proc-macros/16345
4. RustSec — *About RustSec Advisory Database*: https://rustsec.org/
5. rustsec/cargo-audit — README: https://github.com/rustsec/rustsec/blob/main/cargo-audit/README.md
6. cargo-deny CHANGELOG: https://github.com/EmbarkStudios/cargo-deny/blob/main/CHANGELOG.md
7. cargo-deny — Configuration reference: https://embarkstudios.github.io/cargo-deny/checks/cfg.html
8. Cargo Vet — *How it Works* / Introduction: https://mozilla.github.io/cargo-vet/how-it-works.html
9. mozilla/supply-chain — Aggregated Rust crate audits: https://github.com/mozilla/supply-chain
10. cargo-machete: https://github.com/bnjbvr/cargo-machete · cargo-udeps: https://github.com/est31/cargo-udeps · cargo-shear: https://crates.io/crates/cargo-shear
11. Rust Blog — *crates.io: development update* (2026-01-21): https://blog.rust-lang.org/2026/01/21/crates-io-development-update/
12. Rust RFC Book — *RFC 3691: Trusted Publishing for crates.io*: https://rust-lang.github.io/rfcs/3691-trusted-publishing-cratesio.html
13. crates.io — Trusted Publishing docs: https://crates.io/docs/trusted-publishing
14. Socket.dev — *crates.io Implements Trusted Publishing Support*: https://socket.dev/blog/crates-launches-trusted-publishing
15. Rust Internals — *Pre-RFC: Sandboxed, deterministic, reproducible Wasm compilation of proc macros*: https://internals.rust-lang.org/t/pre-rfc-sandboxed-deterministic-reproducible-efficient-wasm-compilation-of-proc-macros/19359
16. Reproducible Builds (concept) — Wikipedia: https://en.wikipedia.org/wiki/Reproducible_builds

## Verification notes

Adversarially fact-checked on 2026-06-21 against current authoritative sources (crates.io
official blog/docs, Rust RFC book, RustSec, cargo-deny CHANGELOG/config, cargo-vet docs).
The report is accurate and current for late-2025/early-2026 Rust. The body makes no
edition-2024- or stable-version-specific claims that have since changed. Verified claims
include: the `faster_log`/`async_println` incident (7,181 + 1,243 downloads, runtime payload,
crypto-key exfiltration), the Jan 2026 crates.io trusted-publishing enforcement mode + GitLab
CI support + blocked `pull_request_target`/`workflow_run` triggers + `pubtime` field + Security
tab + bot/scraper download filtering, the `evm-units` April-2025 crate (>7,000 downloads),
cargo-deny's `unmaintained`/`yanked`/`include-build` knobs, and cargo-vet's Mozilla origin,
`supply-chain/audits.toml` storage, imports, exemptions, and diff-based audits. Two cosmetic
nitpicks, neither affecting the technical content:

- **Source [12] label.** The report labels RFC 3691 as "Trusted Publishing for crates.io." Its
  actual published title is "Security Improvements for CI Publishing to crates.io." The URL,
  RFC number, and described mechanism (OIDC token exchange; ~15-minute access token cited only
  as an illustrative example, with the real lifetime left to implementation) are correct.
  Source: https://rust-lang.github.io/rfcs/3691-trusted-publishing-cratesio.html
- **`finch-rust`/`sha-rust` framing.** Described as "a December 2025 pair." The disclosure blog
  is dated 2025-12-05, but the crates were actually published 2025-11-20 to 2025-11-25 and had
  low download counts (28 and 153 respectively) — much smaller than the report's other examples;
  "December 2025" reflects the disclosure date, not the upload date.
  Source: https://blog.rust-lang.org/2025/12/05/crates.io-malicious-crates-finch-rust-and-sha-rust/
