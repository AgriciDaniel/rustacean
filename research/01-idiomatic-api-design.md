# Idiomatic Rust & API Design

A practical, opinionated field guide to designing Rust APIs that feel native to the language, age
gracefully across SemVer releases, and push correctness into the type system. Targets **Rust edition
2024** on stable (~1.85+). Every section pairs the **good practice** with the **mistake to avoid**.

The single most important external reference is the official **Rust API Guidelines** [1], a community
checklist [2] that codifies the conventions below into citable rule IDs (`C-CASE`, `C-CONV`, etc.).
Treat that checklist as a PR review tool, not a one-time read.

---

## 1. Naming: predictability beats cleverness

Casing follows RFC 430 / `C-CASE` [3][14]: `UpperCamelCase` for types and traits, `snake_case` for
functions/methods/modules, `SCREAMING_SNAKE_CASE` for consts. Note the subtle rule that acronyms are
treated as one word — `Uuid`, `HttpClient`, not `UUID` or `HTTPClient` [3]. In `snake_case`, a single
letter is never its own word: `btree_map`, not `b_tree_map` [3].

**Word order is a crate-wide contract (`C-WORD-ORDER`)** [3]. The std library uses verb-object-error:
`ParseIntError`, `StripPrefixError` — not `IntParseError`. Pick one ordering and apply it everywhere.

- **Good:** name getters after the property, no `get_` prefix (`C-GETTER`): `fn first(&self) -> &T`,
  `fn first_mut(&mut self) -> &mut T` [3]. Reserve bare `get()` for the one obvious thing a type wraps,
  like `Cell::get` [3][15].
- **Mistake:** Java-style `get_name()`/`set_name()` everywhere. It reads as noise to Rust users and
  violates `C-GETTER` [3].

### Conversion prefixes encode cost and ownership (`C-CONV`)

This is the highest-leverage naming rule in the language [3]:

| Prefix  | Cost      | Ownership                          | Example                |
|---------|-----------|------------------------------------|------------------------|
| `as_`   | Free      | borrowed → borrowed                | `str::as_bytes`        |
| `to_`   | Expensive | borrowed → owned (usually clones)  | `str::to_lowercase`    |
| `into_` | Variable  | owned → owned (consumes `self`)    | `String::into_bytes`   |

- **Mistake:** a `to_*` method that's actually free (mislabels cost), or an `as_*` that allocates. The
  prefix is a performance promise; breaking it surprises callers [3].

Iterator methods come as a trio (`C-ITER`): `iter()` yields `&T`, `iter_mut()` yields `&mut T`,
`into_iter()` yields `T` [3]. The returned types are named correspondingly (`C-ITER-TY`): a method
named `into_iter()` returns a type named `IntoIter` [3].

---

## 2. The newtype pattern

A newtype is a single-field tuple struct — `struct Meters(f64)` — that creates a *distinct* type with
zero runtime cost [4][5]. Three canonical jobs [4][6][7]:

1. **Type safety / unit safety:** `Meters` and `Seconds` can't be swapped even though both wrap `f64`.
2. **Bypassing the orphan rule:** implement a foreign trait on a foreign type by wrapping it.
3. **Encapsulating invariants:** make fields private so the only way to construct the value runs
   validation.

```rust
pub struct Email(String);              // field private => cannot be built raw outside the module
impl Email {
    pub fn new(s: String) -> Result<Self, EmailError> {
        if s.contains('@') { Ok(Email(s)) } else { Err(EmailError::Missing) }
    }
}
```

- **Good:** validate at construction and return `Result`; once you hold an `Email`, it is *always*
  valid — "handle errors at the lowest possible level" [8][16]. This is `C-NEWTYPE` / `C-NEWTYPE-HIDE`:
  newtypes also hide the inner representation so you can change it without breaking callers [9].
- **Mistake 1:** leaving the field public (`pub struct Email(pub String)`) — anyone can construct an
  invalid value, defeating the point and violating `C-STRUCT-PRIVATE` [9].
- **Mistake 2:** blindly forwarding everything from the inner type. Newtypes have *no* behavior by
  default; be deliberate about which methods/operators you re-expose, or you reintroduce the very
  confusions you wrapped away [5][6]. Conversely, the `thing.0` boilerplate is the known ergonomic tax —
  use `Deref` sparingly and only when the newtype is a transparent smart-pointer-like wrapper [6].

---

## 3. The builder pattern (and when to reach for typestate)

Builders solve optional/named parameters, which Rust lacks natively [10]. The hand-rolled form returns
`Self` from each setter and a `build()` at the end [10].

- **Mistake:** a `build()` that returns `Result` *only* because a required field might be unset — that
  pushes a compile-time error to runtime.

**Typestate builders** fix this by encoding "which fields are set" in the type parameters, so calling
`build()` before required fields are provided is a *compile error* with no `Option`/`Result` needed
[11][12][13]. The cost is more generics, which inflates binary size and compile time — usually worth it
[11].

In 2024–2026, prefer a macro crate over hand-rolling:

- **`bon`** is the current go-to: `#[derive(Builder)]` for structs and `#[builder]` for functions,
  generating typestate builders that enforce required params and forbid setting the same field twice;
  it also supports named/optional function arguments [17][18]. It absorbed lessons from `typed-builder`,
  `buildstructor`, and `derive_builder` [17].
- **`typed-builder`** encodes state in generics so the compiler only instantiates the path you use [18].

- **Good:** reach for `bon`/`typed-builder` when a struct has 4+ fields, several optional, or required
  fields that must all be present. Keep `Foo::new(a, b)` for the 2–3 mandatory-arg case (`C-CTOR`) [15].
- **Mistake:** a builder for a two-field struct — pure ceremony. And don't bound the builder/struct on
  `Clone`/`Debug` etc. (`C-STRUCT-BOUNDS`); derive them instead so adding more derives stays
  non-breaking [9].

---

## 4. Conversions: `From` / `Into` / `TryFrom`

Implement **`From`**, get **`Into`** for free (blanket impl). The guideline (`C-CONV-TRAITS`) is:
implement the standard conversion traits where they apply, because they compose with generic code [1][2].

- **Good:** `impl From<u16> for MyId` — then any `T: Into<MyId>` works, including `fn f(x: impl Into<MyId>)`.
- **Good:** use **`TryFrom`** when conversion can fail (`String -> Email`), returning a real error type;
  never panic in a `From` impl, because `From` promises infallibility [1][8].
- **Mistake:** implementing `Into` directly instead of `From`. You lose the free blanket impl and the
  more ergonomic call site. Prefer the `to_`/`as_`/`into_` inherent methods over a `from_` static method
  when offering an ergonomic API (`C-CONV-SPECIFIC`), and put conversions on the *more specific* type —
  `str` is more specific than `&[u8]`, so the method lives on `str` [15].
- **Mistake:** a `From` that silently lossily truncates (e.g., `i64 -> i32`). If it can lose data, it's
  a `TryFrom`.

Constructors: `new()` is the inherent primary constructor; alternates get domain names (`File::open`,
`TcpStream::connect`) or `_with_*` suffixes; fallible "conversion constructors" use a `from_*` prefix
and may take extra args or be `unsafe`, which is exactly what distinguishes them from the `From` trait
(`C-CTOR`) [15].

---

## 5. `AsRef` vs `Borrow`: same shape, different contract

Both convert `&Self -> &T`, but their *semantic contracts* differ, and choosing wrong is a common bug
source [19][20].

- **`AsRef<T>`** is a cheap reference-to-reference conversion for **generic argument flexibility**. Use
  it to accept "anything that can be viewed as a `T`": `fn open(p: impl AsRef<Path>)` lets callers pass
  `&str`, `String`, `PathBuf`, `&Path` [19][21].
- **`Borrow<T>`** carries an *extra invariant the type system can't check*: `Hash`, `Eq`, and `Ord` of
  the borrowed view must be **identical** to the owned value's [19][20]. That's why `HashMap<String, _>`
  lookups take `&str` (via `Borrow`), and why `String: Borrow<str>` exists but `String: Borrow<[u8]>`
  does *not* — bytes don't hash like the `str` [19][20].

- **Good default:** take `impl AsRef<T>` in function signatures for ergonomics; this is `C-GENERIC` —
  fewer assumptions about inputs means wider usability [22]. Implement `Borrow` only for true
  borrow-equivalence (hash-map-key use cases) [20].
- **Mistake:** implementing `Borrow<T>` for "borrow just one field" of a struct — the hash/eq/ord
  equivalence won't hold and you'll get silent map-lookup misses. Use `AsRef` there [19][20].
- **Mistake:** going overboard — taking `impl AsRef<str>` on a hot path where every caller already has
  `&str` just adds monomorphization bloat. Plain `&str` is fine then.

---

## 6. Sealed traits: extensibility you control

A trait is **sealed** if it can't be implemented outside its defining crate [23][24]. The canonical
pattern (`C-SEALED`) adds a private supertrait that downstream crates can't name [9][23]:

```rust
pub trait TheTrait: private::Sealed {
    fn method(&self);
}
mod private {
    pub trait Sealed {}
    impl Sealed for SomeType {}   // only here, so only SomeType can impl TheTrait
}
impl TheTrait for SomeType { /* ... */ }
```

Why seal [9][23]:

1. **Forward compatibility** — you can add methods to the trait later without it being a breaking
   change, because no external impls exist that would break.
2. **Invariant safety** — when correct impls must uphold an invariant the compiler can't verify (and a
   bad one would be UB).

- **Good:** seal traits that are meant to be *used* but not *implemented* by downstream code; the
  `sealed` crate's `#[sealed]` attribute automates the boilerplate [24][25].
- **Mistake:** sealing a trait you actually want users to implement (e.g., a plugin/extension hook) —
  you've locked out the whole point. Sealing is for closed sets, not extension points [23].

---

## 7. Generics vs trait objects: dispatch is a design decision

- **Generics → static dispatch.** Monomorphization generates a specialized copy per concrete type:
  fastest possible calls, inlining, full optimization. The default and usually-right choice [26][27].
- **Trait objects (`dyn Trait`, `Box<dyn Trait>`) → dynamic dispatch.** One vtable lookup per call, no
  inlining across the boundary, but enables **heterogeneous collections** (`Vec<Box<dyn Widget>>`) and
  smaller code [26][27].

Decide **early** whether a trait is meant for `dyn` use or as a generic bound (`C-OBJECT`) — it shapes
the design [28]. Object-safe ("dyn-compatible") traits can't have generic methods or return/take `Self`
by value; you can carve out non-object-safe methods with `where Self: Sized`, the trick `Iterator`
uses to stay usable both ways [28].

- **Good:** generics + trait bounds for homogeneous data and hot paths [26]. `dyn` for plugin
  registries, GUI widget trees, or when the concrete type is only known at runtime [26][27].
- **Mistake 1:** `Box<dyn Trait>` reflexively "to keep it simple" in a tight numeric loop — you pay
  vtable + missed inlining for no flexibility benefit [27].
- **Mistake 2:** over-generic public APIs. Every `<T: Trait>` parameter monomorphizes into the caller's
  binary and leaks into signatures; a single `&dyn Trait` argument can dramatically cut compile time and
  binary size when the perf doesn't matter. Generics aren't free either.

---

## 8. Make invalid states unrepresentable

The capstone principle: shrink the gap between *representable* states and *valid* states so the
compiler rejects nonsense [29][30]. Rust's enums (sum types), structs, privacy, and exhaustive
`match` are the tools [30][31].

- **Enum over boolean soup.** Replace `is_active: bool, is_banned: bool` (4 combos, 1–2 illegal) with
  `enum AccountStatus { Active, Banned { reason: String } }` — illegal combinations literally can't be
  written [29][30].
- **`Option<T>` over sentinel values.** No `-1 means missing`; the absence is in the type [30].
- **Newtypes for validated scalars** (Section 2): once `Email` exists, no function downstream re-checks
  it [8][16].
- **Typestate for protocols.** Encode "connection is open vs closed" in the type so `send()` only
  exists on `Connection<Open>` — calling it on a closed connection won't compile [31][11].
- **"Parse, don't validate."** Convert unstructured input into a precise type at the boundary and pass
  the *type* around, rather than re-validating a loose `String` everywhere [8][30].

- **Good:** prefer a richer type today over a runtime check (and a unit test for that check) tomorrow —
  the invariant becomes compiler-enforced and certain tests disappear entirely [30][8].
- **Mistake:** the "stringly-typed" API — passing `String`/`i32` for things that are really emails,
  states, or IDs — then sprinkling `if !valid { panic!() }` guards. That's representable-but-invalid
  state waiting to leak [8][30]. Also avoid a catch-all `Unknown`/`Other` enum variant unless the domain
  truly has one; it reopens the invalid-state hole `match` was protecting [30].

---

## 9. Quick review checklist

Run the official checklist on every public API [2]. The highest-signal items:

- Names: `C-CASE`, `C-CONV` (cost/ownership prefixes), `C-GETTER` (no `get_`), `C-ITER` trio [3].
- Conversions: `From`/`TryFrom` impls, never panic in `From`, conversions on the specific type [1][15].
- Future-proofing: private fields (`C-STRUCT-PRIVATE`), seal use-only traits (`C-SEALED`), don't bound
  structs on derivable traits (`C-STRUCT-BOUNDS`) [9].
- Flexibility: accept `impl AsRef<_>`/`impl IntoIterator` (`C-GENERIC`), decide `dyn`-vs-generic up
  front (`C-OBJECT`), let callers control ownership (`C-CALLER-CONTROL`) [22][28].
- Correctness: push invariants into types; make invalid states unrepresentable [29][30].

---

## Sources

1. Rust API Guidelines (about) — https://rust-lang.github.io/api-guidelines/
2. Rust API Guidelines, Checklist — https://rust-lang.github.io/api-guidelines/checklist.html
3. Rust API Guidelines, Naming — https://rust-lang.github.io/api-guidelines/naming.html
4. New Type Idiom, Rust By Example — https://doc.rust-lang.org/rust-by-example/generics/new_types.html
5. Newtype, Rust Design Patterns (rust-unofficial) — https://rust-unofficial.github.io/patterns/patterns/behavioural/newtype.html
6. Item 6: Embrace the newtype pattern, Effective Rust — https://www.lurklurk.org/effective-rust/newtype.html
7. Newtype Pattern, Comprehensive Rust (Google) — https://google.github.io/comprehensive-rust/idiomatic/leveraging-the-type-system/newtype-pattern.html
8. Make Illegal States Unrepresentable, corrode.dev — https://corrode.dev/blog/illegal-state/
9. Rust API Guidelines, Future-proofing — https://rust-lang.github.io/api-guidelines/future-proofing.html
10. Builder, Rust Design Patterns (rust-unofficial) — https://rust-unofficial.github.io/patterns/patterns/creational/builder.html
11. Typestate builder pattern in Rust — https://n1ghtmare.github.io/2024-05-31/typestate-builder-pattern-in-rust/
12. Build with Naz: Rust typestate pattern, developerlife.com — https://developerlife.com/2024/05/28/typestate-pattern-rust/
13. Design Patterns in Rust: Upgrading the Builder Pattern using the Typestate Pattern — https://blog.ediri.io/design-patterns-in-rust-upgrading-the-builder-pattern-using-the-typestate-pattern
14. RFC 0430, Finalizing naming conventions — https://rust-lang.github.io/rfcs/0430-finalizing-naming-conventions.html
15. Rust API Guidelines, Predictability — https://rust-lang.github.io/api-guidelines/predictability.html
16. Type-Driven Development in Rust, ruggero.io — https://www.ruggero.io/blog/rust_type_driven_development_guide/
17. bon (docs.rs) — https://docs.rs/bon/latest/bon/
18. typed-builder (crates.io) — https://crates.io/crates/typed-builder
19. Rust Traits: Borrow vs AsRef, Medium (TechHara) — https://medium.com/@techhara/rust-tip-and-trick-borrow-37c8b0426a04
20. Should my crate use Borrow or AsRef, users.rust-lang.org — https://users.rust-lang.org/t/should-my-crate-use-borrow-or-asref/111932
21. AsRef, std::convert — https://doc.rust-lang.org/std/convert/trait.AsRef.html
22. Rust API Guidelines, Flexibility — https://rust-lang.github.io/api-guidelines/flexibility.html
23. A definitive guide to sealed traits in Rust, predr.ag — https://predr.ag/blog/definitive-guide-to-sealed-traits-in-rust/
24. The Sealed Trait Pattern in Rust, mxncmr.com — https://mxncmr.com/blog/the-sealed-trait-pattern-in-rust/
25. sealed (docs.rs) — https://docs.rs/sealed
26. Introduction to Rust generics: Trait Objects (Static vs Dynamic dispatch), kerkour.com — https://kerkour.com/rust-generics-trait-objects
27. Using Trait Objects to Abstract over Shared Behavior, The Rust Book — https://doc.rust-lang.org/book/ch18-02-trait-objects.html
28. Rust API Guidelines, Flexibility (C-OBJECT) — https://rust-lang.github.io/api-guidelines/flexibility.html
29. Make invalid states unrepresentable, Dev Radar — https://dev-radar.com/articles/2023/07/20/make-invalid-states-unrepresentable-in-rust/
30. Make Illegal States Unrepresentable, corrode.dev — https://corrode.dev/blog/illegal-state/
31. Generic Finite State Machines with Rust's Type State Pattern, Medium — https://medium.com/@alfred.weirich/generic-finite-state-machines-with-rusts-type-state-pattern-04593bba34a8

---

## Verification notes

Adversarially fact-checked on 2026-06-21 against the official Rust API Guidelines, std docs, the `bon`
crate docs, and Rust release notes. The report is **substantively accurate and current** for edition
2024 / stable Rust 1.85+ (1.85.0 + the 2024 Edition shipped 2025-02-20 —
https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/). The cited URLs that were sampled resolve and
support their claims. A few minor corrections:

1. **`to_` conversion row in the Section 1 table is slightly narrower than the official rule.** The
   report lists `to_` as "borrowed → owned (usually clones)". The official C-CONV table actually says
   `to_` ownership is **"borrowed → borrowed or owned"** with cost "Expensive" — i.e. `to_` does not
   *require* producing an owned value (it can stay a reference-to-reference, just at non-trivial cost; the
   distinction from `as_`/`into_` is that `to_` "stays at the same level of abstraction"). The report's
   example (`str::to_lowercase`, which does allocate) is correct, but the ownership cell overstates the
   rule. Source: https://rust-lang.github.io/api-guidelines/naming.html (C-CONV).

2. **`C-NEWTYPE` is not an official rule ID.** Section 2 cites "`C-NEWTYPE` / `C-NEWTYPE-HIDE` [9]".
   Only **`C-NEWTYPE-HIDE`** exists on the future-proofing page; there is no `C-NEWTYPE` rule. The
   newtype-for-encapsulation guidance is real, but the bare `C-NEWTYPE` ID should be dropped. Source:
   https://rust-lang.github.io/api-guidelines/future-proofing.html.

3. **Citation imprecision for `C-CONV-TRAITS` (Section 4).** The text attributes C-CONV-TRAITS to
   "[1][2]" (the about/checklist pages). The rule actually lives on the **Interoperability** page
   (https://rust-lang.github.io/api-guidelines/interoperability.html). The substance is correct and even
   understated: the guideline explicitly says `Into`/`TryInto` should **never** be implemented directly
   (only `From`/`TryFrom`/`AsRef`/`AsMut`), which matches the report's "implement From, not Into" point.

4. **Citation imprecision for `C-GETTER` in the checklist (Section 9 / Section 1).** `C-GETTER` and its
   `Cell::get` example live on the **Naming** page (correctly cited as [3] in Section 1), not on
   Predictability — the report never miscites this, but note Predictability ([15]) does **not** cover
   getters, so any reader chasing `C-GETTER` should use the naming page.

5. **Terminology is current.** Section 7's "object-safe (dyn-compatible)" phrasing is correct: the
   official term was renamed from "object safety" to **"dyn compatibility"** (landed Rust 1.83,
   Nov 2024). Using both is appropriate for a 2024/2025 audience. Source:
   https://doc.rust-lang.org/std/keyword.dyn.html.

No claim was found to be outright wrong or dangerously outdated. The `bon` recommendation (v3.x,
typestate builders, named/optional args, lessons from typed-builder/buildstructor/derive_builder) is
accurate as of June 2026 — https://docs.rs/bon/latest/bon/. AsRef-vs-Borrow contract (Section 5),
the sealed-trait pattern (Section 6), C-STRUCT-BOUNDS (Section 3/9), and C-GENERIC/C-OBJECT (Section 7)
all match their sources.
