---
type: meta
title: "index"
status: evergreen
created: 2026-06-21
updated: 2026-06-21
tags: [rust, index, meta]
---

# Master Index

Every note by domain. Hub: [[Rust Brain Home]].

## Tooling & Getting Started  ·  [[Tooling & Getting Started]]
**Concepts:** [[Anatomy of a Cargo Project]] · [[Cargo Basics]] · [[Cargo Build Run Check Test]] · [[The Guessing Game Tutorial]] · [[crates.io and Dependencies Intro]] · [[rustfmt and Clippy]] · [[rustup and Installation]]
**Patterns:** [[Keep Application Logic Testable]] · [[Start Projects with cargo new]] · [[Use cargo check While Editing]]
**Anti-patterns:** [[Using rustc Directly for Cargo-Sized Projects]]

## Basic Concepts & Syntax  ·  [[Basic Concepts & Syntax]]
**Concepts:** [[Arrays]] · [[Boolean Logic]] · [[Build-Time Code Execution]] · [[Comments]] · [[Constants]] · [[Control Flow]] · [[Functions]] · [[Generic Functions]] · [[If Expressions]] · [[Integer Overflow]] · [[Iterator Method Trio]] · [[Loop Expressions]] · [[Name Resolution]] · [[PartialEq]] · [[Private Fields with Public Constructors]] · [[Readable Generic APIs]] · [[Scalar Types]] · [[Shadowing]] · [[Statements vs Expressions]] · [[Static Items]] · [[The Debug Trait]] · [[The Display Trait]] · [[Tuples]] · [[Type Inference]] · [[UnsafeCell]] · [[Variables and Mutability]] · [[While and For Loops]]
**Patterns:** [[Documentation Comments]]
**Anti-patterns:** [[Relying on Integer Overflow]]

## Ownership & Memory  ·  [[Ownership & Memory]]
**Concepts:** [[Borrowing]] · [[Copy and Clone]] · [[Move Semantics]] · [[Mutable References]] · [[Ownership]] · [[References]] · [[The Drop Trait]] · [[The Slice Type]] · [[The Stack and the Heap]]
**Patterns:** [[Borrowed Parameter APIs]]
**Anti-patterns:** [[Returning References to Locals]] · [[Stale Slice Indices]]

## Structs  ·  [[Structs]]
**Concepts:** [[Associated Functions]] · [[Methods]] · [[Named Field Structs]] · [[Tuple Structs]] · [[Unit-Like Structs]]
**Patterns:** [[Deriving Traits on Structs]] · [[Field Init Shorthand]] · [[Struct Update Syntax]]
**Anti-patterns:** [[Expecting Per-Field Mutability in Structs]] · [[Partially Moved Structs with Update Syntax]] · [[Storing References in Structs Without Lifetimes]]

## Enums & Pattern Matching  ·  [[Enums & Pattern Matching]]
**Concepts:** [[Binding with @]] · [[Destructuring]] · [[Enum Variants with Data]] · [[Enums]] · [[Exhaustiveness]] · [[Match Guards]] · [[Option]] · [[Patterns]] · [[Refutable and Irrefutable Patterns]] · [[The match Expression]]
**Patterns:** [[Catch-All and Wildcard Patterns]] · [[if let]] · [[let else]]
**Anti-patterns:** [[Overbroad Catch-All Match Arms]] · [[Pattern Variable Shadowing]]

## Collections & Strings  ·  [[Collections & Strings]]
**Concepts:** [[BTreeMap and BTreeSet]] · [[Capacity and Reallocation]] · [[HashMap]] · [[String and str]] · [[Vec]] · [[VecDeque]]
**Patterns:** [[Borrowing Strings and Slices]] · [[Choosing Collection Types]] · [[Iterating Collections]] · [[The Entry API]]
**Anti-patterns:** [[Holding Collection Element References Across Mutation]] · [[String Byte Indexing]]

## Modules & Project Structure  ·  [[Modules & Project Structure]]
**Concepts:** [[Crate Roots]] · [[Module Paths]] · [[Modules]] · [[Packages and Crates]] · [[Splitting Modules into Files]] · [[The use Keyword]] · [[Visibility and Privacy]]
**Patterns:** [[Library and Binary Package Layout]] · [[Re-exporting with pub use]] · [[Workspace Project Structure]]
**Anti-patterns:** [[Glob Imports in Public Code]] · [[Treating mod as include]]

## Error Handling  ·  [[Error Handling]]
**Concepts:** [[Custom Error Types]] · [[Error Sources and Chains]] · [[Option vs Result]] · [[Panic Unwinding and Abort]] · [[Recoverable vs Unrecoverable Errors]] · [[Result]] · [[The Error Trait]] · [[The Question Mark Operator]] · [[panic!]]
**Patterns:** [[Adding Error Context]] · [[Application Errors with anyhow]] · [[Boxing Errors]] · [[Error Handling with thiserror]] · [[Propagating Errors]] · [[Returning Result from main]]
**Anti-patterns:** [[Panicking in Libraries]] · [[Stringly-Typed Errors]] · [[Swallowing Errors]] · [[Unwrap and Expect Overuse]]

## Generics, Traits & Lifetimes  ·  [[Generics, Traits & Lifetimes]]
**Concepts:** [[Associated Types]] · [[Blanket Implementations]] · [[Coherence and the Orphan Rule]] · [[Default Implementations]] · [[Generic Associated Types]] · [[Generics]] · [[Lifetime Elision]] · [[Lifetimes]] · [[Marker Traits]] · [[Supertraits]] · [[The 'static Lifetime]] · [[Trait Bounds]] · [[Traits]] · [[Where Clauses]]
**Patterns:** [[Sealed Traits]] · [[Static Dispatch with Generics]] · [[Use a Newtype to Implement Foreign Traits]]
**Anti-patterns:** [[Overconstraining Lifetimes]] · [[Overgeneric Public APIs]] · [[Unnecessary Bounds on Data Types]]

## Closures & Iterators  ·  [[Closures & Iterators]]
**Concepts:** [[Capturing the Environment]] · [[Closure Type Inference]] · [[Closures]] · [[Consuming Adapters]] · [[Fn, FnMut, FnOnce]] · [[Iterator Adapters]] · [[Iterators]] · [[Lazy Evaluation]] · [[The Iterator Trait]] · [[Zero-Cost Abstractions]] · [[move Closures]]
**Patterns:** [[Prefer Iterator Pipelines to Manual Indexing]] · [[Return Iterators Instead of Collecting]]
**Anti-patterns:** [[Manual Index Loops for Speed]] · [[Moving Out of FnMut Closures]] · [[Unconsumed Iterator Adapters]]

## Smart Pointers & Interior Mutability  ·  [[Smart Pointers & Interior Mutability]]
**Concepts:** [[Box]] · [[Cell]] · [[Cow]] · [[Deref and DerefMut]] · [[Interior Mutability]] · [[Rc]] · [[RefCell]] · [[Reference Cycles and Weak]]
**Patterns:** [[Weak Back References]]
**Anti-patterns:** [[Long-Lived RefCell Borrows]]

## OOP & Trait Objects  ·  [[OOP & Trait Objects]]
**Concepts:** [[Encapsulation in Rust]] · [[Object-Oriented Rust]] · [[Static vs Dynamic Dispatch]] · [[Trait Objects]] · [[dyn Compatibility (Object Safety)]]
**Patterns:** [[Composition over Inheritance]] · [[The State Pattern]] · [[Type-State State Machines]]
**Anti-patterns:** [[Non-dyn-Compatible Traits as Trait Objects]] · [[Overusing Trait Objects]]

## Advanced Types & Features  ·  [[Advanced Types & Features]]
**Concepts:** [[Associated Constants]] · [[Dynamically Sized Types]] · [[Fully Qualified Syntax]] · [[Function Pointers]] · [[Operator Overloading]] · [[Returning Closures]] · [[The Never Type]] · [[Type Aliases]]
**Patterns:** [[Boxed Closure Returns]] · [[Newtype Pattern]] · [[Result Type Aliases]]
**Anti-patterns:** [[Using Type Aliases as Newtypes]]

## Macros  ·  [[Macros]]
**Concepts:** [[Attribute Macros]] · [[Declarative Macros]] · [[Derive Macros]] · [[Function-like Macros]] · [[Macro Diagnostics]] · [[Macro Fragment Specifiers]] · [[Macro Hygiene]] · [[Macro Repetitions]] · [[Procedural Macros]] · [[macro_rules!]] · [[syn and quote]]
**Patterns:** [[Exporting macro_rules Macros]] · [[Procedural Macro Crate Structure]] · [[Testing Macros with trybuild]]
**Anti-patterns:** [[Ambiguous macro_rules Matchers]] · [[Unhygienic Procedural Macro Output]]

## Concurrency  ·  [[Concurrency]]
**Concepts:** [[Arc]] · [[Atomics]] · [[Barrier]] · [[Channels]] · [[Condvar]] · [[OnceLock and LazyLock]] · [[RwLock]] · [[Scoped Threads]] · [[Send and Sync]] · [[Shared State with Mutex]] · [[Threads]] · [[thread_local!]]
**Patterns:** [[Arc Mutex Shared State]] · [[Deadlock Avoidance]] · [[Move Closures with Threads]] · [[Mutex Poisoning and Recovery]]
**Anti-patterns:** [[Holding Locks Too Long]] · [[Ignoring Channel Disconnects]] · [[Lock Order Reversal]] · [[Unsafe Send and Sync Implementations]]

## Async Rust  ·  [[Async Rust]]
**Concepts:** [[Async Closures]] · [[Async Traits]] · [[Cancellation Safety]] · [[Futures]] · [[Pinning]] · [[Shared State in Async]] · [[Streams]] · [[Tasks and spawn]] · [[The Tokio Runtime]] · [[async and await]] · [[select!]]
**Patterns:** [[Async Message Passing]] · [[Async Timeouts]] · [[LocalSet and Non-Send Futures]] · [[Scoping Non-Send Values Before Await]] · [[Structured Task Sets with JoinSet]] · [[spawn_blocking]]
**Anti-patterns:** [[Blocking the Async Executor]] · [[Fire-and-Forget Tokio Tasks]] · [[Holding Locks Across Await]] · [[Non-Cancellation-Safe select! Branches]]

## Unsafe Rust & FFI  ·  [[Unsafe Rust & FFI]]
**Concepts:** [[Aliasing and Provenance]] · [[Dereferencing Raw Pointers]] · [[Extern statics]] · [[FFI with C]] · [[ManuallyDrop]] · [[MaybeUninit]] · [[Miri]] · [[Raw Pointers]] · [[Soundness vs Safety]] · [[Undefined Behavior]] · [[Unions]] · [[Unsafe Rust]] · [[unsafe extern Blocks]] · [[unsafe fn]]
**Patterns:** [[FFI Wrapper Types]] · [[Pin projection]] · [[SAFETY Comments]] · [[Safe Abstractions over Unsafe Code]]
**Anti-patterns:** [[The static mut Footgun and &raw]] · [[Transmute as a Shortcut]]

## Testing & Documentation  ·  [[Testing & Documentation]]
**Concepts:** [[Assertion Macros in Tests]] · [[Doctest Attributes]] · [[Documentation Tests]] · [[Ignored Tests]] · [[Integration Tests]] · [[Intra-doc Links]] · [[Test Functions]] · [[Test Harness and cargo test]] · [[Unit Tests]] · [[rustdoc]]
**Patterns:** [[Result Returning Tests]] · [[Snapshot Testing]] · [[Test Organization]] · [[Test-Driven Development in Rust]] · [[Testable Documentation Examples]]
**Anti-patterns:** [[Broad should_panic Tests]] · [[Shared State Between Parallel Tests]] · [[Untested Documentation Examples]]

## Idioms & API Design  ·  [[Idioms & API Design]]
**Concepts:** [[Conversion Traits]]
**Patterns:** [[Accepting impl Trait vs Generics]] · [[AsRef for Flexible Arguments]] · [[Borrow for Equivalent Keys]] · [[Builder Pattern]] · [[Constructor Naming]] · [[Conversion Method Prefixes]] · [[From and Into]] · [[Making Invalid States Unrepresentable]] · [[Naming Conventions (Rust API Guidelines)]] · [[TryFrom and TryInto]] · [[Type-State Pattern]]
**Anti-patterns:** [[Implementing Borrow for Partial Views]] · [[Panicking From Implementations]]

## Anti-patterns & Footguns  ·  [[Anti-patterns & Footguns]]
**Anti-patterns:** [[Blocking in Async]] · [[Deref Polymorphism Antipattern]] · [[Index Panics vs get]] · [[Integer Overflow Assumptions]] · [[Is Some Then Unwrap]] · [[Needless Clone]] · [[Premature Arc Mutex]] · [[Rc RefCell Overuse]] · [[Sentinel Values]] · [[Stringly-Typed Code]] · [[Unnecessary Collect]]

## Cargo & Dependencies  ·  [[Cargo & Dependencies]]
**Concepts:** [[Build Scripts (build.rs)]] · [[Cargo Configuration Hierarchy]] · [[Cargo Source Overrides]] · [[Cargo Workspaces]] · [[Cargo.lock]] · [[Cargo.toml Manifest]] · [[Dependencies and Version Requirements]] · [[Feature Flags]] · [[Feature Resolver]] · [[MSRV Policy]] · [[Profiles and Optimization Settings]] · [[Publishing to crates.io]] · [[Semantic Versioning]]
**Patterns:** [[Minimizing Dependencies]] · [[Workspace Dependency Inheritance]] · [[cargo publish, yank and owners]] · [[cargo-audit and cargo-deny]]
**Anti-patterns:** [[Non-Additive Feature Flags]] · [[Overbroad Version Requirements]]

## Performance & Optimization  ·  [[Performance & Optimization]]
**Concepts:** [[Iterator Performance]] · [[Profiling Rust Programs]] · [[SIMD and target_feature]] · [[The inline Attribute]]
**Patterns:** [[Allocator Choices]] · [[Arena Allocation]] · [[Benchmarking with Criterion]] · [[Bounds-Check Elimination]] · [[Cache-Friendly Data Layout]] · [[Flamegraph and perf Workflow]] · [[LTO and codegen-units]] · [[Reducing Heap Allocations]] · [[SmallVec for Inline Storage]]
**Anti-patterns:** [[Avoiding Premature Optimization]] · [[Speculative Micro-Optimization]]

## Editions & Compiler  ·  [[Editions & Compiler]]
**Concepts:** [[Codegen and Optimization Flags]] · [[Conditional Compilation (cfg)]] · [[Edition 2024]] · [[Lints and Lint Levels]] · [[Rust Editions]] · [[Target Triples]] · [[The rustc Compiler]]
**Patterns:** [[Enforcing Expected cfgs]] · [[Inspecting rustc Configuration]] · [[Migrating Editions]]
**Anti-patterns:** [[Silencing Edition Migration Lints]] · [[Unchecked cfg Names]]

## Embedded Rust  ·  [[Embedded Rust]]
**Concepts:** [[Bare-Metal Programming]] · [[Embedded Rust Basics]] · [[Interrupts and Concurrency (Embedded)]] · [[Memory-Mapped IO]] · [[Peripheral Access Crates]] · [[no_std]]
**Patterns:** [[Critical Sections in Embedded Rust]] · [[Heapless Collections in Embedded Rust]]
**Anti-patterns:** [[Unsynchronized static mut in Interrupts]]

## std: I/O & Formatting  ·  [[std IO & Formatting]]
**Concepts:** [[Buffered IO with BufReader and BufWriter]] · [[Files in std::fs]] · [[Format Specifiers]] · [[Format Strings and format!]] · [[IO Errors and io::Result]] · [[OsStr and OsString]] · [[Path and PathBuf]] · [[Seek and Cursor]] · [[The Read and Write Traits]]
**Patterns:** [[Implementing Display by Hand]] · [[Locking Stdin and Stdout]] · [[Reading Standard Input]] · [[Writing Standard Output]]

## std: Collections Deep  ·  [[std: Collections Deep]]
**Concepts:** [[BTreeMap Ordering and Ranges]] · [[BinaryHeap Priority Queues]] · [[HashMap Hashers and Key Invariants]] · [[HashMap Method Families]] · [[HashSet]] · [[LinkedList]] · [[Set Collections with HashSet and BTreeSet]] · [[VecDeque Ring Buffers]]
**Patterns:** [[Choosing Standard Collections]] · [[Entry API for Accumulator Maps]] · [[try_reserve and Fallible Allocation]]
**Anti-patterns:** [[HashMap Iteration Order Is Arbitrary]] · [[Mutating Collection Keys In Place]]

## std: Core Trait Catalog  ·  [[std: Core Trait Catalog]]
**Concepts:** [[Arithmetic Operator Traits Add and Mul]] · [[AsRef and AsMut Conversion Traits]] · [[Clone Semantics in std]] · [[Destructor Semantics with Drop]] · [[Display and Debug Formatting Traits]] · [[Equality Traits PartialEq and Eq]] · [[Fallible Conversion Traits (std)]] · [[Hash and Eq Contracts]] · [[Index and IndexMut Traits]] · [[Infallible Conversion Traits (std)]] · [[Iterator Conversion Traits IntoIterator and FromIterator]] · [[Ordering Traits PartialOrd and Ord]] · [[The Default Trait]]

## std: Iterator Adapter Catalog  ·  [[std: Iterator Adapter Catalog]]
**Concepts:** [[Iterator chain cycle and step_by]] · [[Iterator collect and FromIterator]] · [[Iterator flat_map and flatten]] · [[Iterator fold and reduce]] · [[Iterator map and filter]] · [[Iterator partition and unzip]] · [[Iterator predicate search adapters]] · [[Iterator rev and last]] · [[Iterator scan and peekable]] · [[Iterator sum product and count]] · [[Iterator take skip and while bounds]] · [[Iterator zip and enumerate]]

## std: Option & Result Combinators  ·  [[std: Option & Result Combinators]]
**Concepts:** [[Converting Between Option and Result]] · [[Option Combinators]] · [[Result Combinators]] · [[Transpose and Flatten]]
**Patterns:** [[Chaining with and_then]] · [[Converting Option to Result with ok_or]] · [[Defaulting with unwrap_or Variants]] · [[Fallback Chains with or_else]] · [[Mapping Present Values with map]] · [[Predicate Checks with is_some_and and matches]] · [[Question Mark with Option]]
**Anti-patterns:** [[Eager Work in Option and Result Defaults]]

## std: Vec, String & Slices  ·  [[std: Vec, String & Slices]]
**Concepts:** [[Bytes Chars and Unicode]] · [[Slicing and Range Indexing]] · [[String vs str Methods]] · [[Vec Capacity and Growth]] · [[Vec Methods Reference]]
**Patterns:** [[Building Strings Efficiently]] · [[Filtering Vecs with dedup retain and drain]] · [[Sorting and Binary Search on Slices]] · [[Splitting Strings Without Collecting]] · [[Using chunks windows and split_at]]
**Anti-patterns:** [[Assuming String Indexes Are Characters]]

## Advanced Type System  ·  [[Advanced Type System]]
**Concepts:** [[Const Generics and Const Parameters]] · [[Drop Check]] · [[Higher-Ranked Trait Bounds]] · [[PhantomData]] · [[Required Bounds on Generic Associated Types]] · [[Return-Position impl Trait in Traits]] · [[Trait Coherence and Covered Implementations]] · [[Type Layout and repr]] · [[Type layout]] · [[Variance]] · [[Zero-Sized Types]]
**Patterns:** [[Lending Iterators with GATs]] · [[Phantom Type Parameters]]
**Anti-patterns:** [[Uncovered Type Parameters in Foreign Impl]]

## Ecosystem & Crate Playbooks  ·  [[Ecosystem & Crate Playbooks]]
**Concepts:** [[Choosing the Right Rust Crate]]
**Patterns:** [[Axum Web Service Playbook]] · [[Command-Line Parsing]] · [[Configuration Loading]] · [[Debugging]] · [[Itertools Iterator Helpers Playbook]] · [[Rayon Data Parallelism Playbook]] · [[Regex Text Matching Playbook]] · [[Reqwest HTTP Client Playbook]] · [[Serde Data Format Playbook]] · [[Tokio Runtime Playbook]] · [[Tracing and Structured Logging Playbook]] · [[clap Command Line Playbook]]

## WebAssembly, no_std & Targets  ·  [[WebAssembly, no_std & Targets]]
**Concepts:** [[Global Allocators]] · [[Panic Handlers]] · [[Panic Strategy Selection]] · [[Rust WebAssembly Targets]] · [[Target Features and CPU Baselines]] · [[Using alloc without std]] · [[alloc Collections in no_std]] · [[no_std Crate Design]] · [[wasm-bindgen Basics]]
**Patterns:** [[Cargo Cross-Compilation Setup]] · [[Target-Specific cfg Boundaries]]
**Anti-patterns:** [[Assuming wasm32 Means Browser]]