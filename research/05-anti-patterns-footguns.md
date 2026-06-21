# Anti-Patterns & Footguns

> Scope: idiomatic Rust as of Rust 1.85+ and the 2024 edition. Each section gives the **good practice**, the **mistake to avoid**, a short rationale, and (where useful) a tiny sketch. Citations map to the **Sources** list at the end.

Rust eliminates whole classes of memory bugs, but it does *not* prevent bad architecture. Most "footguns" are not compiler holes — they are habits carried over from other languages that the type system allows but quietly punishes with runtime panics, lost performance, or unmaintainable code. The recurring theme below: **push invariants into the type system; reach for runtime escape hatches only when the compiler genuinely can't help.**

---

## 1. `unwrap()` / `expect()` Overuse

**Good practice.** Use `unwrap`/`expect` only to assert an invariant that *cannot* fail given correct program logic — i.e., where a panic means "the programmer was wrong," not "the input was bad." Prefer `expect("...")` over `unwrap()` so the panic message documents *why* the value should exist [1][3]. For everything caller- or environment-driven, propagate with `?` and a real `Result` type.

**Mistake to avoid.** Using `unwrap()` as your default for I/O, parsing, env vars, locks, or anything touching the outside world. Andrew Gallant (BurntSushi) is blunt: *"Panicking should not be used for error handling in either applications or libraries"* — panics are great for *bug detection*, terrible as a recovery strategy, and produce context-free, unprofessional crashes for end users [1].

**Rationale.** The legitimate use is **runtime invariants** that can't be encoded in types: *"it is impossible or impractical to move every invariant into the type system"* [1]. When a panic *does* fire it should *"correspond to a violation of the expectations of the programmer"* [1]. `unwrap` is also fine as scaffolding while prototyping — but should be removed before the patch ships [3].

```rust
// MISTAKE: silent crash on bad input, no context
let port: u16 = std::env::var("PORT").unwrap().parse().unwrap();

// GOOD: propagate; the caller decides
let port: u16 = std::env::var("PORT")?.parse()?;

// GOOD: assert a true invariant with a reason
let re = Regex::new(r"^\d+$").expect("hardcoded regex is valid");
```

A nuance: `expect`-with-reason is so clearly the right default that some argue `unwrap` should never have existed as a separate method [2]. Conversely, `unwrap` is *not* problematic when the surrounding code trivially shows it can't panic [1] — e.g. immediately after a `is_some()`-equivalent guard inside the same expression.

---

## 2. Needless `clone()`

**Good practice.** Borrow first (`&T`, `&str`, `&[T]`); clone only when you genuinely need a second owned value or to break a lifetime you've decided is worth the cost. Run `clippy` — `redundant_clone`, `clone_on_copy`, and `needless_borrow` catch the easy cases [5].

**Mistake to avoid.** Reaching for `.clone()` to silence the borrow checker. The Rust community's own framing: such copies are *"mostly caused by a lack of familiarity with lifetimes, or an architecture issue which forces the programmer to make more copies than they need to"* [6]. Defensive `clone()` is a smell, not a fix [4].

**Rationale.** *"Unnecessary cloning can make the program slower for no good reason"* [5]. More importantly, a `clone()` sprinkled to dodge an error usually hides a real ownership-design question (who *owns* this data?). Cloning a `String` per request, or a whole `Vec` to read one element, scales badly.

```rust
// MISTAKE: clones to satisfy the borrow checker
fn greet(name: String) { println!("hi {name}"); }
greet(user.name.clone());

// GOOD: borrow — accept &str / impl AsRef<str>
fn greet(name: &str) { println!("hi {name}"); }
greet(&user.name);
```

Caveat: don't over-rotate. Clippy's `needless_borrows_for_generic_args` can suggest removing a borrow that you'll want back after a refactor, occasionally producing "value moved" errors later [5]; treat lints as advice, not law.

---

## 3. `Rc<RefCell<T>>` Overuse

**Good practice.** Model ownership as a tree; pass `&`/`&mut` references down it. Reach for `Rc<RefCell<T>>` only for genuine **shared-ownership graphs with mutation** that the borrow checker can't express (e.g., observer graphs, some interpreters).

**Mistake to avoid.** Using `Rc<RefCell<T>>` as a reflex to recreate Java/Python object soup. The official Book warns this *"often leads to code patterns that are basically a 1:1 translation of patterns used in other procedural or object-based languages"* [7], and that pervasive interior mutability means *"you'd find problems later (possibly in production rather than during development)"* [7].

**Rationale.** `RefCell` moves the borrow check from compile time to **runtime**: violate it and you get a `panic!`, not a compile error [7]. There's a per-access cost (it maintains a borrow flag like a single-threaded lock) [7], and **re-entrancy** can cause subtle double-borrow panics where a closure unexpectedly runs while a borrow is live [7]. `Rc<RefCell<Vec<T>>>` also locks the *whole* `Vec` — you can't borrow two elements mutably from different handles [7]. Michael-F-Bryan lists excessive `Rc<RefCell<T>>` among the top bad habits, showing callbacks or "return a summary" designs that avoid it entirely [4].

```rust
// MISTAKE: shared mutable graph by default → runtime borrow panics
type Node = Rc<RefCell<NodeData>>;

// GOOD: prefer ownership + indices (arena/slotmap) for graphs,
// or pass &mut down a tree. Reserve Rc<RefCell> for real DAGs.
```

For thread-shared data the parallel mistake is `Arc<Mutex<T>>` — see §5.

---

## 4. Stringly-Typed Code

**Good practice.** Encode meaning in **types**, not strings. Use the **newtype pattern** to distinguish values that share a representation, and **enums** for closed sets of states/kinds. The API guidelines: *"Newtypes can statically distinguish between different interpretations of an underlying type"* and *"Core types like `bool`, `u8` and `Option` have many possible interpretations"* — so prefer dedicated types [9][10].

**Mistake to avoid.** Passing `String`/`&str` (or bare `bool`/`i32`) where the domain has structure: stringly-typed IDs, `match`-on-magic-string state machines, error messages as `String`, or `fn(bool, bool, bool)` call sites. Stringly-typed errors *"make it hard for callers to programmatically handle specific errors"* [8].

**Rationale.** Newtypes give *"type-safety at compile time without any performance overhead at runtime"* [8] — a `UserId(u64)` can't be passed where an `OrderId(u64)` is expected. Critically, **type aliases do *not* do this**: *"type aliases don't provide the type-checking benefits that the newtype pattern does"* [8][10]. Making invalid states unrepresentable is the recurring idiom [4].

```rust
// MISTAKE: any string goes anywhere; bools are positional mysteries
fn render(content: String, draft: bool, escaped: bool) {}

// GOOD: distinct types + enums carry intent
struct Markdown(String);
enum Visibility { Draft, Published }
fn render(content: Markdown, vis: Visibility, esc: Escaping) {}
```

For sets of independent flags the guidelines recommend the `bitflags` crate over abusing enums [10].

---

## 5. Premature `Arc<Mutex<T>>`

**Good practice.** In concurrent/async code, **prefer message passing**: move ownership through channels (`mpsc` for many-producers-one-worker, `oneshot` for a single reply, `broadcast` for fan-out) and let one task own the state [11]. Use `Arc<Mutex<T>>` for genuinely shared resources — a cache, connection pool, config — where per-task copies would be wasteful [11].

**Mistake to avoid.** Defaulting every shared value to `Arc<Mutex<T>>`, and — the classic async footgun — **holding a `std::sync::MutexGuard` across an `.await`**. A `std::sync::MutexGuard` is `!Send`, so this often fails to compile; and if a guard *is* made `Send`, *"The code compiles, but it deadlocks!"* [11].

**Rationale.** Lock contention throttles throughput, and holding a lock across `.await` can stall the whole scheduler or deadlock [11]. Tokio's own guidance: for I/O or work that must hold state across awaits, *"spawn a dedicated task to manage state"* via message passing rather than a shared mutex [11]. Choose the lock type deliberately — `std::sync::Mutex` for short, synchronous critical sections (it's faster); `tokio::sync::Mutex` only when you *must* hold the lock across `.await`, and even then it's *"typically better to use one of the two other approaches"* [11].

```rust
// MISTAKE: lock held across await → scheduler stall / deadlock
let mut g = state.lock().unwrap();
g.value = fetch().await;   // guard still alive across .await

// GOOD: drop the guard before awaiting...
let snapshot = { let g = state.lock().unwrap(); g.clone() };
let v = fetch().await;
// ...or hand state to one owning task and talk to it over a channel.
```

---

## 6. Deref Polymorphism

**Good practice.** Implement `Deref`/`DerefMut` *only* for genuine smart-pointer types, taking `&Pointer<T> -> &T` [12]. For code reuse / "inheritance," use **traits** (shared behavior) and **composition**, writing explicit facade methods or using a delegation crate (`delegate`, `ambassador`) to cut boilerplate [12].

**Mistake to avoid.** `impl Deref for Wrapper { type Target = Inner; ... }` purely to make `Inner`'s methods callable on `Wrapper` — i.e., faking inheritance. This is a recognized anti-pattern [12].

**Rationale.** It's *"a surprising idiom — future programmers reading this in code will not expect this to happen"* [12], because method resolution happens implicitly through the dot operator. It abuses a trait *"designed for the implementation of custom pointer types"* [12], introduces **no real subtyping** (traits on `Inner` don't transfer to `Wrapper`), supports only single "inheritance" with no interfaces or privacy, and pollutes error messages with types the reader never wrote [12].

```rust
// MISTAKE: Deref to borrow methods from a field (fake inheritance)
impl Deref for Bar { type Target = Foo; fn deref(&self) -> &Foo { &self.f } }

// GOOD: a trait for the shared behavior, implemented explicitly
trait Draw { fn draw(&self); }
impl Draw for Bar { fn draw(&self) { self.f.draw(); } }
```

---

## 7. Integer Overflow Assumptions

**Good practice.** Treat overflow as a **bug** and choose explicit semantics with `checked_*` (→ `Option`), `saturating_*` (clamp to bounds), `overflowing_*` (value + overflow flag), or `wrapping_*` / `Wrapping<T>` when you *intend* modular arithmetic [13]. For release builds where you still want detection, enable `overflow-checks = true` in the profile.

**Mistake to avoid.** Assuming `a + b` either always panics or always wraps. By default it **panics in debug and silently wraps (two's complement) in release** [13][14]. So code that passes all debug tests can produce wrong-but-not-crashing results in production.

**Rationale.** RFC 0560 is explicit: overflow is *"known to be a common source of error"* and *"code which encounters an error condition is still considered buggy"* — checks are on by default in debug and *"compiled out whenever an optimized build is produced"* for speed [13]. Relying on the wrap is therefore an error unless you opt into it via a `wrapping_*` method [14]. Related beginner footgun: indexing with `i32` instead of `usize`, then casting everywhere — collections index by `usize` by design [4].

```rust
// MISTAKE: assumes one behavior; differs debug vs release
let total = a + b;

// GOOD: be explicit about intent
let total = a.checked_add(b).ok_or(Error::Overflow)?;   // reject
let clamped = a.saturating_add(b);                       // clamp
let hash = a.wrapping_add(b);                            // intend wrap
```

---

## 8. Other Common Beginner→Intermediate Mistakes

**Fighting the borrow checker by cloning or `unsafe`.** Beginners hit "cannot borrow as mutable while borrowed immutably" and iterator-invalidation errors, then escape via `clone()` or `unsafe` [15]. The mature path is to restructure scopes — experienced devs report they *"fight the borrow checker less and less"* once they design *with* ownership [15]. `unsafe` *"is **not** a magical escape hatch which will make the compiler stop complaining"* [4], and "I know it's single-threaded so `static mut` is fine" is a classic trap [15].

**Sentinel / post-construction states.** Returning `-1`, `""`, or building a half-initialized object then filling fields later. Idiomatic Rust uses `Option`/`Result` so the check can't be forgotten, and constructs objects fully so *"invalid states [are] unrepresentable"* [4].

**Manual index loops over iterators (and panicking indexing).** Prefer `iter()`, `windows()`, `enumerate()` and `.get()` (returns `Option`) over `arr[i]`, which panics out of bounds and invites off-by-one bugs [4].

**Returning tuples of owned values instead of borrowing.** *"Returning ownership of multiple values is not idiomatic Rust, as it doesn't take advantage of borrowing"* [15]; it also signals overengineering / premature optimization [15].

**`.is_some()` + `.unwrap()` instead of pattern matching.** Two checks that can drift out of sync; `if let`/`match`/`let ... else` keep them coupled [4]. Likewise, carrying C-style **Hungarian notation** (`strName`, `bFlag`) is pointless when *"Rust's syntax guarantees that it just isn't possible to confuse a trait for a normal type"* [4].

**General antidote.** Lean on the tooling: `cargo clippy` ships *"over 400 diagnostic lints"* targeting redundant clones, needless `mut`, and potential runtime panics [5]; `rustfmt` for style; and `#![deny(clippy::all)]` (or selective `warn`) in CI catches most of the above before review.

---

## Sources

1. Andrew Gallant (BurntSushi), "Using unwrap() in Rust is Okay" — https://burntsushi.net/unwrap/
2. The Coded Message, "Why Rust should only have provided `expect`... and not also `unwrap`" — https://www.thecodedmessage.com/posts/2022-07-14-programming-unwrap/
3. Rust Users Forum, "Best practices for unwrap" — https://users.rust-lang.org/t/best-practices-for-unwrap/101335
4. Michael-F-Bryan, "Common Newbie Mistakes and Bad Practices in Rust: Bad Habits" — https://adventures.michaelfbryan.com/posts/rust-best-practices/bad-habits/
5. rust-clippy issues/lints (redundant_clone, needless_borrow, needless_borrows_for_generic_args) — https://github.com/rust-lang/rust-clippy/issues/17 and https://github.com/rust-lang/rust-clippy/issues/12454
6. Rust Users Forum, "How to avoid interior mutability" (clones from lifetime/architecture issues) — https://users.rust-lang.org/t/how-to-avoid-interior-mutability/61910
7. The Rust Programming Language (Book), "RefCell<T> and the Interior Mutability Pattern" — https://doc.rust-lang.org/book/ch15-05-interior-mutability.html
8. Rust Design Patterns / Eze Sunday, "Newtype pattern: adding type safety" — https://rust-unofficial.github.io/patterns/patterns/behavioural/newtype.html and https://ezesunday.com/rusts-newtype-pattern-adding-type-safety-and-clarity/
9. The Rust Programming Language (Book), "Advanced Types" (type aliases vs newtypes) — https://doc.rust-lang.org/book/ch20-03-advanced-types.html
10. Rust API Guidelines, "Type safety" — https://rust-lang.github.io/api-guidelines/type-safety.html
11. Tokio Tutorial, "Shared state" (Arc<Mutex>, guards across .await, message passing) — https://tokio.rs/tokio/tutorial/shared-state
12. Rust Design Patterns, "Deref Polymorphism" anti-pattern — https://rust-unofficial.github.io/patterns/anti_patterns/deref.html
13. The Rust RFC Book, "RFC 0560: Integer overflow" — https://rust-lang.github.io/rfcs/0560-integer-overflow.html
14. The Rust Programming Language (Book), "Data Types" (overflow debug vs release, wrapping/checked/saturating/overflowing) — https://doc.rust-lang.org/book/ch03-02-data-types.html
15. Rust Users Forum, "Beginner — Fighting the borrow checker" — https://users.rust-lang.org/t/beginner-fighting-the-borrow-checker/91945

---

## Verification notes

Adversarially fact-checked on 2026-06-21 against current stable Rust (1.85.0, released 2025-02-20) and the 2024 edition. A sample of cited primary sources was re-fetched; the body's technical claims hold up. Only one minor, non-blocking accuracy nit was found.

- **Scope/baseline (line 3) — confirmed.** Rust 1.85.0 shipped 2025-02-20 and stabilized the Rust 2024 edition, so the report's "Rust 1.85+ and the 2024 edition" framing is current. Source: https://blog.rust-lang.org/2025/02/20/Rust-1.85.0/
- **§1 unwrap/expect (BurntSushi quotes) — verified verbatim.** "Panicking should not be used for error handling…", panics "correspond to a violation of the expectations of the programmer", and "it is impossible or impractical to move every invariant into the type system" all appear in the source. Source: https://burntsushi.net/unwrap/
- **§4 newtype vs type alias — verified.** The Book confirms type aliases do not give the newtype's type-checking benefits ("if we mix up `Kilometers` and `i32`… the compiler will not give us an error"). Source: https://doc.rust-lang.org/book/ch20-03-advanced-types.html
- **§5 Arc<Mutex> / guard across .await — verified.** Tokio's tutorial confirms `std::sync::MutexGuard` is `!Send`, that a `Send` guard yields "The code compiles, but it deadlocks!", and the std-vs-tokio Mutex / message-passing guidance. Source: https://tokio.rs/tokio/tutorial/shared-state
- **§6 Deref polymorphism — verified.** The anti-patterns book confirms "a surprising idiom", that `Deref` "is designed for the implementation of custom pointer types", and recommends traits/explicit dispatcher methods. Source: https://rust-unofficial.github.io/patterns/anti_patterns/deref.html
- **§7 integer overflow — verified.** The Book confirms panic-in-debug / two's-complement-wrap-in-release and the `checked_/saturating_/overflowing_/wrapping_` families; relying on the wrap "is considered an error". Source: https://doc.rust-lang.org/book/ch03-02-data-types.html
- **MINOR — §8 "over 400 diagnostic lints" [5] is understated and slightly mis-cited.** Clippy now ships **over 800** lints (the official repo/lint index), so "over 400" is stale though not false. Also, source [5] points at two clippy GitHub *issues* (#17, #12454) rather than the lint list itself; the count would be better cited to the lint index. Suggested correction: "over 800 diagnostic lints", cited to https://rust-lang.github.io/rust-clippy/master/index.html (repo: https://github.com/rust-lang/rust-clippy). Not load-bearing to any argument.

Verdict: solid. The report is accurate and current for Rust 1.85+/2024 edition; the only issue is the conservative/stale clippy lint count noted above.
