#!/usr/bin/env python3
"""Generate Wave-2 'new coverage' Codex prompts (create new atomic notes for new domains)."""
import pathlib
OUT=pathlib.Path(__file__).parent/"prompts"; OUT.mkdir(exist_ok=True)

TEMPLATE="""You are a meticulous Rust technical writer EXTENDING an Obsidian "Rust brain". Working dir = vault root.

STEP 1 — read and obey:
- wiki/meta/CONVENTIONS.md  (the authoring contract)
- wiki/concepts/Ownership.md  (gold-standard depth/format)

YOUR DOMAIN: "{domain}"

SOURCES (read what's relevant before writing):
{sources}

TASK — create a thorough, ATOMIC set of NEW notes for this domain (one idea per note), >=80 lines each:
- concept notes -> wiki/concepts/   ·   pattern notes -> wiki/patterns/   ·   antipattern notes -> wiki/antipatterns/
- exactly ONE map-of-content -> wiki/mocs/{domain}.md (type: moc) linking everything you create.

Seed titles to cover (rename/split as sources warrant; one atomic idea per note):
{seeds}

HARD RULES:
- Each note: full flat-YAML frontmatter per CONVENTIONS (type, title, status, created: 2026-06-21,
  updated: 2026-06-21, tags incl. rust, domain: "{domain}", difficulty, related >=3, sources, source_urls real, rust_version "edition 2024 / 1.85+").
- Body: answer-first first line; CONVENTIONS skeleton; a MINIMAL COMPILABLE ```rust example (a second example or edge cases is great); ✅ Best practice; ⚠️ Pitfalls; "See also" with >=8 [[wikilinks]]; "Sources".
- Correct & CURRENT (edition 2024 / 1.85+). For crates, cite docs.rs and note "verify the latest version"; do not invent APIs.
- SKIP-IF-EXISTS: if a note with a title already exists anywhere in wiki/, do NOT overwrite it — just [[link]] to it. Choose distinct, canonical titles to avoid collisions.
- Write ONLY this domain's notes (+ its MOC). Do not edit other domains. Do not touch .raw/, sources/, research/, rust/, specs/, references/.
- Aim for {target} notes.

FINISH: print the list of file paths you created (one per line).
"""

D=[
 ("std-core-types","std: Vec, String & Slices",
  ['- .raw/std/vec-Vec.md, .raw/std/string-String.md, .raw/std/primitive-slice.md, .raw/std/primitive-str.md'],
  ["Vec Methods Reference","Vec Capacity and Growth","Slicing and Ranges","String vs str Methods",
   "Building and Splitting Strings","sort, sort_by and binary_search","dedup, retain and drain",
   "chunks, windows and split_at","Bytes, Chars and Unicode"],"9-14"),
 ("std-option-result","std: Option & Result Combinators",
  ['- .raw/std/option-Option.md, .raw/std/result-Result.md'],
  ["Option Combinators","Result Combinators","ok_or and ok_or_else","unwrap_or, unwrap_or_else, unwrap_or_default",
   "map, and_then, or_else","Converting Between Option and Result","transpose and flatten",
   "is_some_and and matches!","Question Mark with Option"],"9-13"),
 ("std-iterators","std: Iterator Adapter Catalog",
  ['- .raw/std/iter-Iterator.md'],
  ["map and filter (reference)","fold and reduce","flat_map and flatten","zip and enumerate",
   "take, skip, take_while, skip_while","chain, cycle, step_by","collect and FromIterator",
   "scan and peekable","partition and unzip","sum, product, count","any, all, find, position","rev and last"],"10-16"),
 ("std-collections","std: Collections Deep",
  ['- .raw/std/collections-index.md, .raw/std/collections-HashMap.md, .raw/std/collections-BTreeMap.md'],
  ["HashMap Methods","The Entry API","BTreeMap and Ordering","HashSet and BTreeSet","VecDeque",
   "BinaryHeap","Choosing a Collection","Custom Hashers and Hashing"],"8-12"),
 ("std-traits","std: Core Trait Catalog",
  ['- .raw/std/convert-From.md, .raw/std/clone-Clone.md, .raw/std/default-Default.md, .raw/std/cmp-Ord.md, .raw/std/hash-Hash.md, .raw/std/ops-index.md, .raw/std/error-Error.md'],
  ["From and Into (std)","TryFrom and TryInto (std)","The Default Trait","Clone and Copy (std)",
   "Display and Debug (std)","PartialEq and Eq","PartialOrd and Ord","The Hash Trait",
   "IntoIterator and FromIterator","Operator Traits (Add, Mul, Index)","AsRef and AsMut (std)","The Drop Trait (std)"],"10-16"),
 ("std-io-fmt","std: I/O & Formatting",
  ['- .raw/std/io-index.md, .raw/std/fmt-index.md'],
  ["Reading Standard Input","Writing Standard Output","The Read and Write Traits","BufReader and BufWriter",
   "Working with Files (fs)","Paths: Path and PathBuf","format! and the Formatting Syntax",
   "Format Specifiers","Implementing Display by Hand","Error Handling in I/O"],"9-13"),
 ("ecosystem-crates","Ecosystem & Crate Playbooks",
  ['- .raw/research/09-tooling-project-hygiene.md, .raw/research/10-dependency-supply-chain-security.md',
   '- use your knowledge of major crates; CITE docs.rs and note "verify the latest version"'],
  ["Tokio Playbook","Serde Playbook","clap Playbook","reqwest Playbook","rayon Playbook",
   "tracing and Structured Logging","regex Playbook","itertools Playbook","Choosing the Right Crate","axum Web Service Playbook"],"9-14"),
 ("advanced-type-system","Advanced Type System",
  ['- .raw/books/the-reference.md (types, generics), .raw/books/rustonomicon.md (variance, phantom data)'],
  ["Const Generics","Generic Associated Types (GATs)","PhantomData","Zero-Sized Types","Variance",
   "Higher-Ranked Trait Bounds (HRTB)","impl Trait in Associated Types","Trait Coherence and the Orphan Rule (deep)"],"8-12"),
 ("wasm-targets-nostd","WebAssembly, no_std & Targets",
  ['- .raw/books/embedded-book.md, .raw/books/rustc-book.md; use your knowledge of wasm tooling, CITE official docs'],
  ["WebAssembly with Rust","wasm-bindgen Basics","no_std Programming (deep)","Using alloc without std",
   "Cross-Compilation","Target Triples and Target Features","Panic Strategy (abort vs unwind)","Conditional Compilation for Targets"],"7-11"),
]
for slug,dom,src,seeds,target in D:
    (OUT/f"new-{slug}.txt").write_text(TEMPLATE.format(domain=dom,sources="\n".join(src),
        seeds="\n".join(f"  - {s}" for s in seeds),target=target))
print("wrote",len(D),"new-coverage prompts:",[s for s,*_ in D])
