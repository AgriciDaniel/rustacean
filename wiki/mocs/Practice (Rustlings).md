---
type: moc
title: "Practice (Rustlings)"
status: seed
created: 2026-06-21
updated: 2026-06-21
tags: [rust, practice, rustlings, moc]
domain: "Practice (Rustlings)"
difficulty: basic
related: ["[[Practice: Intro]]", "[[Practice: Move Semantics]]", "[[Practice: Error Handling]]", "[[Practice: Iterators]]", "[[Practice: Traits]]", "[[Practice: Lifetimes]]"]
sources: ["[[rustlings]]"]
source_urls: ["https://github.com/rust-lang/rustlings"]
rust_version: "edition 2024 / 1.85+"
---

# Practice (Rustlings)

Rustlings is the short-feedback practice track for turning Rust concepts into compiler-guided habits. Use this MOC to jump from each exercise group to the matching concept notes in the brain.

## Exercise Map
| Rustlings group | Practice note | Skills drilled | Concept and pattern links |
|---|---|---|---|
| `00_intro` | [[Practice: Intro]] | Editing small Rust files, reading compiler output, using `rustlings` feedback. | [[The rustc Compiler]], [[Cargo Build Run Check Test]], [[rustup and Installation]], [[Comments]], [[The Guessing Game Tutorial]], [[Tooling & Getting Started]] |
| `01_variables` | [[Practice: Variables]] | `let`, `mut`, constants, shadowing, simple type annotations. | [[Variables and Mutability]], [[Constants]], [[Shadowing]], [[Type Inference]], [[Scalar Types]], [[Statements vs Expressions]] |
| `02_functions` | [[Practice: Functions]] | Function definitions, parameters, return values, expression tails. | [[Functions]], [[Statements vs Expressions]], [[Type Inference]], [[Methods]], [[Associated Functions]], [[The Never Type]] |
| `03_if` | [[Practice: If]] | Boolean conditions, branch expressions, compatible branch types. | [[If Expressions]], [[Statements vs Expressions]], [[The match Expression]], [[Patterns]], [[Scalar Types]], [[Option]] |
| `04_primitive_types` | [[Practice: Primitive Types]] | Scalars, tuples, arrays, slices, indexing, destructuring. | [[Scalar Types]], [[Tuples]], [[Arrays]], [[The Slice Type]], [[Slicing and Range Indexing]], [[Destructuring]] |
| `05_vecs` | [[Practice: Vecs]] | Creating vectors, pushing values, iterating and transforming elements. | [[Vec]], [[Vec Methods Reference]], [[Vec Capacity and Growth]], [[Iterator map and filter]], [[Iterating Collections]], [[std: Vec, String & Slices]] |
| `06_move_semantics` | [[Practice: Move Semantics]] | Moves, borrows, mutable borrows, cloning only when intentional. | [[Move Semantics]], [[Ownership]], [[Borrowing]], [[References]], [[Mutable References]], [[Copy and Clone]] |
| `07_structs` | [[Practice: Structs]] | Named fields, tuple structs, methods, update syntax, derived traits. | [[Named Field Structs]], [[Tuple Structs]], [[Unit-Like Structs]], [[Methods]], [[Struct Update Syntax]], [[Deriving Traits on Structs]] |
| `08_enums` | [[Practice: Enums]] | Defining variants, carrying data, matching exhaustively. | [[Enums]], [[Enum Variants with Data]], [[The match Expression]], [[Exhaustiveness]], [[Patterns]], [[Refutable and Irrefutable Patterns]] |
| `09_strings` | [[Practice: Strings]] | Owned strings, string slices, borrowing, Unicode-aware access. | [[String and str]], [[String vs str Methods]], [[Bytes Chars and Unicode]], [[The Slice Type]], [[Borrowing Strings and Slices]], [[Building Strings Efficiently]] |
| `10_modules` | [[Practice: Modules]] | Module paths, `use`, visibility, splitting namespaces. | [[Modules]], [[Module Paths]], [[The use Keyword]], [[Visibility and Privacy]], [[Name Resolution]], [[Splitting Modules into Files]] |
| `11_hashmaps` | [[Practice: HashMaps]] | Inserting, updating, counting, entry API, key invariants. | [[HashMap]], [[HashMap Method Families]], [[The Entry API]], [[Entry API for Accumulator Maps]], [[Hash and Eq Contracts]], [[Choosing Standard Collections]] |
| `12_options` | [[Practice: Options]] | `Option<T>`, `match`, `if let`, combinators, avoiding unchecked unwraps. | [[Option]], [[Option Combinators]], [[if let]], [[let else]], [[Predicate Checks with is_some_and and matches]], [[Question Mark with Option]] |
| `13_error_handling` | [[Practice: Error Handling]] | `Result<T, E>`, parsing failures, `?`, custom errors, panic boundaries. | [[Result]], [[The Question Mark Operator]], [[Recoverable vs Unrecoverable Errors]], [[Custom Error Types]], [[The Error Trait]], [[Propagating Errors]] |
| `14_generics` | [[Practice: Generics]] | Generic structs/functions, type parameters, avoiding duplicated code. | [[Generics]], [[Trait Bounds]], [[Where Clauses]], [[Type Inference]], [[Static Dispatch with Generics]], [[Readable Generic APIs]] |
| `15_traits` | [[Practice: Traits]] | Trait definitions, impl blocks, default methods, trait bounds. | [[Traits]], [[Default Implementations]], [[Trait Bounds]], [[The Display Trait]], [[The Debug Trait]], [[Blanket Implementations]] |
| `16_lifetimes` | [[Practice: Lifetimes]] | Borrow relationships, explicit lifetime parameters, returned references. | [[Lifetimes]], [[Lifetime Elision]], [[References]], [[Borrowing]], [[The 'static Lifetime]], [[Returning References to Locals]] |
| `17_tests` | [[Practice: Tests]] | Unit tests, assertions, expected panics, `Result` tests. | [[Test Harness and cargo test]], [[Test Functions]], [[Assertion Macros in Tests]], [[Unit Tests]], [[Result Returning Tests]], [[Test Organization]] |
| `18_iterators` | [[Practice: Iterators]] | Adapter chains, collecting, consuming adapters, custom iterator thinking. | [[Iterators]], [[The Iterator Trait]], [[Iterator Adapters]], [[Iterator map and filter]], [[Iterator collect and FromIterator]], [[Consuming Adapters]] |
| `19_smart_pointers` | [[Practice: Smart Pointers]] | `Box`, `Rc`, `Arc`, deref, reference counts, interior mutability. | [[Box]], [[Rc]], [[Arc]], [[Deref and DerefMut]], [[RefCell]], [[Smart Pointers & Interior Mutability]] |
| `20_threads` | [[Practice: Threads]] | Spawning threads, moving captured values, channels, shared state. | [[Threads]], [[Scoped Threads]], [[Channels]], [[Send and Sync]], [[Shared State with Mutex]], [[Move Closures with Threads]] |
| `21_macros` | [[Practice: Macros]] | `macro_rules!`, fragments, repetition, expansion hygiene basics. | [[macro_rules!]], [[Declarative Macros]], [[Macro Fragment Specifiers]], [[Macro Repetitions]], [[Macro Hygiene]], [[Function-like Macros]] |
| `22_clippy` | [[Practice: Clippy]] | Reading lints, improving idioms, removing needless allocations or branches. | [[rustfmt and Clippy]], [[Lints and Lint Levels]], [[Use cargo check While Editing]], [[Needless Clone]], [[Borrowed Parameter APIs]], [[Idioms & API Design]] |
| `23_conversions` | [[Practice: Conversions]] | `From`, `Into`, `TryFrom`, string parsing, conversion API design. | [[Conversion Traits]], [[From and Into]], [[TryFrom and TryInto]], [[Fallible Conversion Traits (std)]], [[Infallible Conversion Traits (std)]], [[AsRef and AsMut Conversion Traits]] |
| `quizzes` | [[Practice: Quizzes]] | Combining earlier topics under compiler and test feedback. | [[Ownership]], [[Named Field Structs]], [[Enums]], [[Result]], [[Iterators]], [[Trait Bounds]] |

## Learning Path
Work in folder order when building a first pass: the groups deliberately move from syntax, to ownership, to data modeling, to abstraction. For review, jump by concept: ownership problems are usually in `06_move_semantics`, API shape problems in `14_generics` and `15_traits`, and workflow problems in `17_tests`, `22_clippy`, and `23_conversions`.

## See also
[[Tooling & Getting Started]] · [[Basic Concepts & Syntax]] · [[Ownership & Memory]] · [[Collections & Strings]] · [[Enums & Pattern Matching]] · [[Error Handling]] · [[Generics, Traits & Lifetimes]] · [[Testing & Documentation]]

## Sources
- Rustlings exercise repository — [[rustlings]],
  https://github.com/rust-lang/rustlings
