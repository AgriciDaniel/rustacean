#!/usr/bin/env python3
"""Gap-fill prompts: create the missing notes the Secretary Review identified, in EXISTING domains."""
import pathlib
OUT=pathlib.Path(__file__).parent/"prompts"; OUT.mkdir(exist_ok=True)

TMPL="""You are the Rust Secretary FILLING COVERAGE GAPS in the Rust brain. Working dir = vault root.
Read AGENTS.md, wiki/meta/CONVENTIONS.md, and wiki/concepts/Ownership.md (the standard) first.

YOUR DOMAIN: "{domain}"  (an EXISTING domain; its MOC is wiki/mocs/ — find it by `domain:` field).

Create these MISSING atomic notes (one idea per note, >=80 lines each), correct & current
(edition 2024 / stable 1.85+). These were flagged as gaps / dead-link targets; some other notes already
[[link]] to these exact titles, so use these titles EXACTLY so the links resolve:
{notes}

Put concept notes in wiki/concepts/, pattern/playbook notes in wiki/patterns/, antipattern notes in
wiki/antipatterns/ (choose by nature). Then ADD each new note to this domain's MOC (wiki/mocs/<this domain>.md)
under the right section.

SOURCES (read what's relevant): {sources}

RULES (same contract as the rest of the brain):
- Full flat-YAML frontmatter (type,title,status,created:2026-06-21,updated:2026-06-21,tags incl rust,
  domain:"{domain}",difficulty,related>=3,sources,source_urls real,rust_version:"edition 2024 / 1.85+").
- Answer-first first line; CONVENTIONS skeleton; a MINIMAL COMPILABLE ```rust example; ✅ Best practice;
  ⚠️ Pitfalls; "See also" with >=8 [[wikilinks]]; "Sources".
- SKIP-IF-EXISTS: never overwrite an existing note; if a title already exists, just [[link]] to it.
- Title must equal filename. Correct & current; never invent APIs; for crates cite docs.rs + "verify latest version".
- Do not edit other domains' notes. Do not touch .raw/, sources/, research/, rust/, specs/, references/.

FINISH: print the file paths you created.
"""

G=[
 ("Basic Concepts & Syntax",
  ["Control Flow","Boolean Logic","Generic Functions"],
  ".raw/books/the-book.md (control flow, generics), .raw/books/the-reference.md"),
 ("Advanced Type System",
  ["Drop Check","Type layout","Type Layout and repr"],
  ".raw/books/rustonomicon.md (dropck, layout), .raw/books/the-reference.md (type layout / repr)"),
 ("Unsafe Rust & FFI",
  ["Unions","Extern statics","Pin projection"],
  ".raw/books/the-reference.md (unions, external blocks), .raw/books/rustonomicon.md, .raw/research/06-unsafe-and-ffi.md"),
 ("Testing & Documentation",
  ["Snapshot Testing","Doctest Attributes","Intra-doc Links"],
  ".raw/books/rustdoc-book.md, .raw/books/the-book.md (testing); for snapshot testing cite insta on docs.rs"),
 ("Cargo & Dependencies",
  ["Cargo Source Overrides","Cargo Configuration Hierarchy","Feature Resolver","Workspace Dependency Inheritance","cargo publish, yank and owners"],
  ".raw/books/cargo-book.md"),
 ("std: I/O & Formatting",
  ["Seek and Cursor","OsStr and OsString","Locking Stdin and Stdout","I/O Error Kinds"],
  ".raw/std/io-index.md, .raw/books/the-reference.md"),
 ("std: Collections Deep",
  ["HashSet","LinkedList","try_reserve and Fallible Allocation"],
  ".raw/std/collections-index.md"),
 ("Concurrency",
  ["Condvar","OnceLock and LazyLock","Barrier","thread_local!","Mutex Poisoning and Recovery"],
  ".raw/books/the-book.md (concurrency), .raw/std/sync-Mutex.md, .raw/research/08-concurrency.md"),
 ("Async Rust",
  ["Async Closures","LocalSet and Non-Send Futures","Async Timeouts","Cancellation-Safe I/O"],
  ".raw/research/04-async-rust.md, .raw/books/the-book.md (async); cite tokio.rs"),
 ("Macros",
  ["Procedural Macro Crate Structure","syn and quote","Macro Diagnostics","Testing Macros with trybuild"],
  ".raw/books/the-reference.md (procedural macros); cite docs.rs for syn/quote/trybuild + 'verify latest version'"),
 ("WebAssembly, no_std & Targets",
  ["Global Allocators","Panic Handlers","alloc Collections in no_std"],
  ".raw/books/embedded-book.md, .raw/books/the-reference.md; cite rustwasm docs + 'verify latest version'"),
 ("Ecosystem & Crate Playbooks",
  ["Command-Line Parsing","Debugging","Configuration Loading"],
  ".raw/research/09-tooling-project-hygiene.md; cite docs.rs (clap/config/figment) + 'verify latest version'"),
 ("Performance & Optimization",
  ["Flamegraph and perf Workflow","Allocator Choices","SIMD and target_feature","Cache-Friendly Data Layout"],
  ".raw/research/07-performance-optimization.md, .raw/books/the-reference.md"),
]
import re
for dom,notes,src in G:
    slug=re.sub(r'[^a-z0-9]+','-',dom.lower()).strip('-')
    (OUT/f"gap-{slug}.txt").write_text(TMPL.format(domain=dom,
        notes="\n".join(f"  - {n}" for n in notes), sources=src))
print("wrote",len(G),"gap-fill prompts:",[re.sub(r'[^a-z0-9]+','-',d.lower()).strip('-') for d,_,_ in G])
