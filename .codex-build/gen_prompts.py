#!/usr/bin/env python3
"""Generate one Codex prompt file per domain for the Rust-brain atomic ingestion.
Each prompt mirrors the validated pilot template (.codex-build/prompts/error-handling.txt).
Run: python3 .codex-build/gen_prompts.py   (writes .codex-build/prompts/<slug>.txt)
"""
import pathlib

OUT = pathlib.Path(__file__).parent / "prompts"
OUT.mkdir(parents=True, exist_ok=True)

TEMPLATE = """You are a meticulous Rust technical writer contributing to an Obsidian "Rust brain" vault. Your working directory is the vault root.

STEP 1 — read and obey these exactly (the contract):
- wiki/meta/CONVENTIONS.md  (note types, frontmatter schema, body structure, linking rules, quality bar)
- wiki/concepts/Ownership.md  (the GOLD-STANDARD exemplar — match its depth, format, example quality, citation style)

YOUR DOMAIN: "{domain}"

SOURCES (read the relevant parts before writing):
{sources}

TASK — produce a thorough, ATOMIC set of notes for THIS domain only (one note per distinct concept / idiom / pitfall):
- concept notes  -> wiki/concepts/
- pattern notes (idioms / best practices) -> wiki/patterns/
- antipattern notes (footguns + the correct alternative) -> wiki/antipatterns/
- exactly ONE map-of-content -> wiki/mocs/{domain}.md  (type: moc) linking every note you create, grouped by Concepts / Patterns / Antipatterns.

Seed titles to cover (expand/rename as the sources warrant; split anything broad into atomic notes):
{seeds}

HARD RULES:
- Write ONLY notes for THIS domain. Do NOT create notes for other domains — other writers own those. You MAY [[link]] to them; dangling links are expected and fine.
- Every note MUST have complete flat-YAML frontmatter per CONVENTIONS: type, title, status, created: 2026-06-21, updated: 2026-06-21, tags (include rust), domain: "{domain}", difficulty, related (>=3 wikilinks), sources, source_urls (real doc.rust-lang.org URLs), rust_version: "edition 2024 / 1.85+".
- Body: answer-first first line; the section skeleton from CONVENTIONS; a MINIMAL COMPILABLE ```rust example; "Best practice" (✅) and "Pitfalls" (⚠️) bullets; a "See also" line with >=6 [[wikilinks]]; a "Sources" section with doc.rust-lang.org URLs.
- Target edition 2024 / stable 1.85+. Be correct and current. Do NOT invent APIs; if unsure, mark status: seed and add a "> [!todo]" line instead of guessing.
- Filenames must equal the note title. Do NOT overwrite or modify any existing file. If a name would collide with an existing note, SKIP it (another writer already made the canonical one) — just [[link]] to it.
- Aim for {target} notes, each >=40 lines of real substance. Atomic: one idea per note.
- Do not touch anything outside wiki/. Do not edit .raw/, sources/, research/, rust/, specs/.

FINISH: print the list of file paths you created (one per line).
"""

DOMAINS = [
  ("tooling-getting-started", "Tooling & Getting Started",
   ['- .raw/books/the-book.md -> "Getting Started" (Installation, Hello World, Hello Cargo) and "Programming a Guessing Game"',
    '- .raw/books/command-line-book.md -> project basics'],
   ["rustup and Installation", "Cargo Basics", "Anatomy of a Cargo Project", "cargo build run check test",
    "The Guessing Game (Tutorial)", "crates.io and Dependencies (intro)", "rustfmt and clippy (intro)"], "8-15"),

  ("basic-concepts", "Basic Concepts & Syntax",
   ['- .raw/books/the-book.md -> "Common Programming Concepts" (Variables and Mutability, Data Types, Functions, Comments, Control Flow)',
    '- .raw/books/the-reference.md -> types and expressions for precise semantics'],
   ["Variables and Mutability", "Shadowing", "Constants", "Scalar Types", "Compound Types (Tuples and Arrays)",
    "Functions", "Statements vs Expressions", "Control Flow (if)", "Loops (loop, while, for)", "Comments and Docs"], "10-16"),

  ("ownership-memory", "Ownership & Memory",
   ['- .raw/books/the-book.md -> "Understanding Ownership" (References and Borrowing, The Slice Type)',
    '- .raw/books/the-reference.md -> destructors / memory',
    '- .raw/research/02-ownership-borrowing-lifetimes.md -> pitfalls (verified)'],
   ["Borrowing", "References", "Mutable References", "The Slice Type", "Move Semantics", "Copy and Clone",
    "The Drop Trait", "The Stack and the Heap"], "8-14 (NOTE: Ownership.md already exists — do NOT recreate it; link to it)"),

  ("structs", "Structs",
   ['- .raw/books/the-book.md -> "Using Structs to Structure Related Data"'],
   ["Structs", "Tuple Structs", "Unit-Like Structs", "Methods", "Associated Functions", "Field Init Shorthand",
    "Struct Update Syntax", "Deriving Traits on Structs"], "8-12"),

  ("enums-pattern-matching", "Enums & Pattern Matching",
   ['- .raw/books/the-book.md -> "Enums and Pattern Matching" and "Patterns and Matching"'],
   ["Enums", "Option", "The match Expression", "if let", "let else", "Patterns", "Match Guards",
    "Destructuring", "Binding with @", "Exhaustiveness"], "10-16"),

  ("modules-project-structure", "Modules & Project Structure",
   ['- .raw/books/the-book.md -> "Managing Growing Projects with Packages, Crates, and Modules"',
    '- .raw/books/the-reference.md -> Items / Modules / Use declarations'],
   ["Packages and Crates", "Modules", "Paths", "The use Keyword", "Visibility and Privacy",
    "Splitting Modules into Files", "Re-exporting with pub use", "Workspaces"], "8-12"),

  ("collections-strings", "Collections & Strings",
   ['- .raw/books/the-book.md -> "Common Collections"',
    '- .raw/books/the-reference.md / std for exact behavior'],
   ["Vec", "String and str", "HashMap", "The Entry API", "Iterating Collections", "BTreeMap and BTreeSet",
    "VecDeque", "Capacity and Reallocation"], "8-14"),

  ("generics-traits-lifetimes", "Generics, Traits & Lifetimes",
   ['- .raw/books/the-book.md -> "Generic Types, Traits, and Lifetimes"',
    '- .raw/books/the-reference.md -> Traits, Generic parameters, Associated items',
    '- .raw/research/01-idiomatic-api-design.md and .raw/research/02-ownership-borrowing-lifetimes.md (verified)'],
   ["Generics", "Traits", "Trait Bounds", "Default Implementations", "Associated Types", "Generic Associated Types",
    "Lifetimes", "Lifetime Elision", "The 'static Lifetime", "Where Clauses", "Blanket Implementations",
    "Marker Traits", "Supertraits", "Coherence and the Orphan Rule"], "14-22"),

  ("closures-iterators", "Closures & Iterators",
   ['- .raw/books/the-book.md -> "Functional Language Features: Iterators and Closures" (incl. perf: loops vs iterators)',
    '- .raw/research/07-performance-optimization.md (verified)'],
   ["Closures", "Fn, FnMut, FnOnce", "Capturing the Environment", "move Closures", "Iterators",
    "The Iterator Trait", "Iterator Adapters", "Consuming Adapters", "Zero-Cost Abstractions", "Lazy Evaluation"], "10-16"),

  ("smart-pointers", "Smart Pointers & Interior Mutability",
   ['- .raw/books/the-book.md -> "Smart Pointers"'],
   ["Box", "Deref and DerefMut", "Rc", "RefCell", "Interior Mutability", "Cell", "Reference Cycles and Weak",
    "Cow (Clone on Write)"], "8-12"),

  ("concurrency", "Concurrency",
   ['- .raw/books/the-book.md -> "Fearless Concurrency"',
    '- .raw/books/the-reference.md -> Send/Sync',
    '- .raw/research/08-concurrency.md (verified)'],
   ["Threads", "move Closures with Threads", "Channels", "Shared State with Mutex", "Arc", "Send and Sync",
    "RwLock", "Atomics", "Scoped Threads", "Deadlock Avoidance"], "10-16"),

  ("async-rust", "Async Rust",
   ['- .raw/books/the-book.md -> "Fundamentals of Asynchronous Programming" / Async and Await',
    '- .raw/research/04-async-rust.md (verified) -> Tokio, cancellation, Send bounds'],
   ["Futures", "async and await", "The Tokio Runtime", "Tasks and spawn", "select!", "Pinning", "Streams",
    "Cancellation Safety", "spawn_blocking", "Async Traits", "Shared State in Async"], "12-18"),

  ("oop-trait-objects", "OOP & Trait Objects",
   ['- .raw/books/the-book.md -> "Object-Oriented Programming Features of Rust"',
    '- .raw/research/01-idiomatic-api-design.md (dyn compatibility)'],
   ["Trait Objects", "dyn Compatibility (Object Safety)", "Static vs Dynamic Dispatch", "The State Pattern",
    "Encapsulation in Rust", "Composition over Inheritance"], "6-10"),

  ("advanced-types-features", "Advanced Types & Features",
   ['- .raw/books/the-book.md -> "Advanced Features" (advanced traits, advanced types, advanced functions/closures)'],
   ["Type Aliases", "The Never Type", "Dynamically Sized Types", "Function Pointers", "Returning Closures",
    "Operator Overloading", "Fully Qualified Syntax", "Associated Constants"], "8-12"),
   # NOTE: "Newtype Pattern" intentionally lives only in idioms-api-design to avoid a parallel write race.

  ("macros", "Macros",
   ['- .raw/books/the-book.md -> "Macros"',
    '- .raw/books/the-reference.md -> Macros by example, Procedural macros'],
   ["Declarative Macros", "macro_rules!", "Procedural Macros", "Derive Macros", "Attribute Macros",
    "Function-like Macros", "Macro Hygiene"], "7-10"),

  ("unsafe-ffi", "Unsafe Rust & FFI",
   ['- .raw/books/rustonomicon.md (whole book)',
    '- .raw/books/the-reference.md -> unsafety, external blocks',
    '- .raw/books/the-book.md -> "Unsafe Rust"',
    '- .raw/research/06-unsafe-and-ffi.md (verified) -> edition 2024 unsafe extern, &raw, static_mut_refs'],
   ["Unsafe Rust", "Raw Pointers", "Dereferencing Raw Pointers", "unsafe fn", "Undefined Behavior",
    "FFI with C", "unsafe extern Blocks", "MaybeUninit", "Aliasing and Provenance", "Miri",
    "Soundness vs Safety", "The static mut Footgun and &raw"], "12-18"),

  ("testing-documentation", "Testing & Documentation",
   ['- .raw/books/the-book.md -> "Writing Automated Tests"',
    '- .raw/books/rustdoc-book.md',
    '- .raw/books/the-reference.md -> testing attributes'],
   ["Writing Tests", "assert Macros", "Unit Tests", "Integration Tests", "Test Organization",
    "Controlling How Tests Are Run", "Documentation Comments", "Doctests", "rustdoc", "Test-Driven Development in Rust"], "9-14"),

  ("idioms-api-design", "Idioms & API Design",
   ['- .raw/research/01-idiomatic-api-design.md (verified)',
    '- .raw/books/rust-by-example.md -> idioms'],
   ["Newtype Pattern", "Builder Pattern", "From and Into", "TryFrom and TryInto", "AsRef and Borrow",
    "Sealed Traits", "Making Invalid States Unrepresentable", "Naming Conventions (Rust API Guidelines)",
    "Type-State Pattern", "Accepting impl Trait vs Generics"], "10-16 (mostly patterns)"),

  ("antipatterns-footguns", "Anti-patterns & Footguns",
   ['- .raw/research/05-anti-patterns-footguns.md (verified)'],
   ["Needless Clone", "Rc RefCell Overuse", "Premature Arc Mutex", "Deref Polymorphism Antipattern",
    "Stringly-Typed Code", "Integer Overflow Assumptions", "Blocking in Async", "Index Panics vs get",
    "Unnecessary Collect", "Overusing unwrap in Libraries"], "8-14 (mostly antipatterns; SKIP any that already exist)"),

  ("cargo-dependencies", "Cargo & Dependencies",
   ['- .raw/books/cargo-book.md',
    '- .raw/research/09-tooling-project-hygiene.md and .raw/research/10-dependency-supply-chain-security.md (verified)'],
   ["Cargo.toml Manifest", "Dependencies and Version Requirements", "Semantic Versioning", "Feature Flags",
    "Cargo Workspaces", "Build Scripts (build.rs)", "Publishing to crates.io", "cargo-audit and cargo-deny",
    "Minimizing Dependencies", "Cargo.lock", "Profiles and Optimization Settings", "MSRV Policy"], "10-16"),

  ("performance-optimization", "Performance & Optimization",
   ['- .raw/research/07-performance-optimization.md (verified)',
    '- .raw/books/the-book.md -> performance sections'],
   ["Profiling Rust", "Reducing Allocations", "Iterators vs Loops (Performance)", "The inline Attribute",
    "Bounds-Check Elimination", "SmallVec and Arena Allocation", "LTO and codegen-units",
    "Benchmarking with criterion", "Avoiding Premature Optimization"], "8-12"),

  ("editions-compiler", "Editions & Compiler",
   ['- .raw/books/edition-guide.md',
    '- .raw/books/rustc-book.md'],
   ["Rust Editions", "Edition 2024", "Migrating Editions", "The rustc Compiler", "Lints and Lint Levels",
    "Conditional Compilation (cfg)", "Target Triples", "Codegen and Optimization Flags"], "8-12"),

  ("embedded-rust", "Embedded Rust",
   ['- .raw/books/embedded-book.md'],
   ["no_std", "Embedded Rust Basics", "Bare-Metal Programming", "Peripheral Access Crates",
    "Interrupts and Concurrency (Embedded)", "Memory-Mapped I/O"], "6-10"),
]

for slug, domain, sources, seeds, target in DOMAINS:
    text = TEMPLATE.format(
        domain=domain,
        sources="\n".join(sources),
        seeds="\n".join(f"  - {s}" for s in seeds),
        target=target,
    )
    (OUT / f"{slug}.txt").write_text(text)
print(f"Wrote {len(DOMAINS)} prompt files to {OUT}")
for slug, domain, *_ in DOMAINS:
    print(f"  {slug}  ->  {domain}")
