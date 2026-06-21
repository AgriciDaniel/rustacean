# Rust By Example

- [English](https://doc.rust-lang.org/rust-by-example/print.html)
- [日本語](https://doc.rust-lang.org/rust-by-example/ja/print.html)
- [中文](https://doc.rust-lang.org/rust-by-example/zh/print.html)
- [Español](https://doc.rust-lang.org/rust-by-example/es/print.html)
- [한국어](https://doc.rust-lang.org/rust-by-example/ko/print.html)

[Print this book](https://doc.rust-lang.org/rust-by-example/print.html "Print this book")[Git repository](https://github.com/rust-lang/rust-by-example "Git repository")

# Rust by Example

[Rust](https://www.rust-lang.org/) is a modern systems programming language focusing on safety, speed,
and concurrency. It accomplishes these goals by being memory safe without using
garbage collection.

Rust by Example (RBE) is a collection of runnable examples that illustrate various Rust
concepts and standard libraries. To get even more out of these examples, don’t forget
to [install Rust locally](https://www.rust-lang.org/tools/install) and check out the [official docs](https://doc.rust-lang.org/std/).
Additionally for the curious, you can also [check out the source code for this site](https://github.com/rust-lang/rust-by-example).

Now let’s begin!

- [Hello World](https://doc.rust-lang.org/rust-by-example/print.html#hello-world) \- Start with a traditional Hello World program.

- [Primitives](https://doc.rust-lang.org/rust-by-example/print.html#primitives) \- Learn about signed integers, unsigned integers and other primitives.

- [Custom Types](https://doc.rust-lang.org/rust-by-example/print.html#custom-types) \- `struct` and `enum`.

- [Variable Bindings](https://doc.rust-lang.org/rust-by-example/print.html#variable-bindings) \- mutable bindings, scope, shadowing.

- [Types](https://doc.rust-lang.org/rust-by-example/print.html#types) \- Learn about changing and defining types.

- [Conversion](https://doc.rust-lang.org/rust-by-example/print.html#conversion) \- Convert between different types, such as strings, integers, and floats.

- [Expressions](https://doc.rust-lang.org/rust-by-example/print.html#expressions) \- Learn about Expressions & how to use them.

- [Flow of Control](https://doc.rust-lang.org/rust-by-example/print.html#flow-of-control) \- `if`/`else`, `for`, and others.

- [Functions](https://doc.rust-lang.org/rust-by-example/print.html#functions) \- Learn about Methods, Closures and Higher Order Functions.

- [Modules](https://doc.rust-lang.org/rust-by-example/print.html#modules) \- Organize code using modules

- [Crates](https://doc.rust-lang.org/rust-by-example/print.html#crates) \- A crate is a compilation unit in Rust. Learn to create a library.

- [Cargo](https://doc.rust-lang.org/rust-by-example/print.html#cargo) \- Go through some basic features of the official Rust package management tool.

- [Attributes](https://doc.rust-lang.org/rust-by-example/print.html#attributes) \- An attribute is metadata applied to some module, crate or item.

- [Generics](https://doc.rust-lang.org/rust-by-example/print.html#generics) \- Learn about writing a function or data type which can work for multiple types of arguments.

- [Scoping rules](https://doc.rust-lang.org/rust-by-example/print.html#scoping-rules) \- Scopes play an important part in ownership, borrowing, and lifetimes.

- [Traits](https://doc.rust-lang.org/rust-by-example/print.html#traits-2) \- A trait is a collection of methods defined for an unknown type: `Self`

- [Macros](https://doc.rust-lang.org/rust-by-example/print.html#macro_rules) \- Macros are a way of writing code that writes other code, which is known as metaprogramming.

- [Error handling](https://doc.rust-lang.org/rust-by-example/print.html#error-handling) \- Learn Rust way of handling failures.

- [Std library types](https://doc.rust-lang.org/rust-by-example/print.html#std-library-types) \- Learn about some custom types provided by `std` library.

- [Std misc](https://doc.rust-lang.org/rust-by-example/print.html#std-misc) \- More custom types for file handling, threads.

- [Testing](https://doc.rust-lang.org/rust-by-example/print.html#testing-1) \- All sorts of testing in Rust.

- [Unsafe Operations](https://doc.rust-lang.org/rust-by-example/print.html#unsafe-operations) \- Learn about entering a block of unsafe operations.

- [Compatibility](https://doc.rust-lang.org/rust-by-example/print.html#compatibility) \- Handling Rust’s evolution and potential compatibility issues.

- [Meta](https://doc.rust-lang.org/rust-by-example/print.html#meta) \- Documentation, Benchmarking.


# Hello World

This is the source code of the traditional Hello World program.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

`println!` is a [_macro_](https://doc.rust-lang.org/rust-by-example/print.html#macro_rules) that prints text to the
console.

A binary can be generated using the Rust compiler: `rustc`.

```bash

$ rustc hello.rs
```

`rustc` will produce a `hello` binary that can be executed.

```bash

$ ./hello
Hello World!
```

### Activity

Click ‘Run’ above to see the expected output. Next, add a new
line with a second `println!` macro so that the output shows:

```text

Hello World!
I'm a Rustacean!
```

# Comments

Any program requires comments, and Rust supports
a few different varieties:

## Regular Comments

These are ignored by the compiler:

- **Line comments**: Start with `//` and continue to the end of the line
- **Block comments**: Enclosed in `/* ... */` and can span multiple lines

## [Documentation Comments (Doc Comments) which are parsed into HTML library](https://doc.rust-lang.org/rust-by-example/print.html\#documentation-comments-doc-comments-which-are-parsed-into-html-library-documentation) [documentation](https://doc.rust-lang.org/rust-by-example/print.html\#documentation):

- `///` \- Generates docs for the item that follows it
- `//!` \- Generates docs for the enclosing item (typically used at the top of a file or module)

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[Library documentation](https://doc.rust-lang.org/rust-by-example/print.html#documentation)

# Formatted print

Printing is handled by a series of [`macros`](https://doc.rust-lang.org/rust-by-example/print.html#macro_rules) defined in
[`std::fmt`](https://doc.rust-lang.org/std/fmt/) some of which are:

- `format!`: write formatted text to [`String`](https://doc.rust-lang.org/rust-by-example/print.html#strings)
- `print!`: same as `format!` but the text is printed to the console
(io::stdout).
- `println!`: same as `print!` but a newline is appended.
- `eprint!`: same as `print!` but the text is printed to the standard error
(io::stderr).
- `eprintln!`: same as `eprint!` but a newline is appended.

All parse text in the same fashion. As a plus, Rust checks formatting
correctness at compile time.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

[`std::fmt`](https://doc.rust-lang.org/std/fmt/) contains many [`traits`](https://doc.rust-lang.org/std/fmt/#formatting-traits) which govern the display
of text. The base form of two important ones are listed below:

- `fmt::Debug`: Uses the `{:?}` marker. Format text for debugging purposes.
- `fmt::Display`: Uses the `{}` marker. Format text in a more elegant, user
friendly fashion.

Here, we used `fmt::Display` because the std library provides implementations
for these types. To print text for custom types, more steps are required.

Implementing the `fmt::Display` trait automatically implements the
[`ToString`](https://doc.rust-lang.org/std/string/trait.ToString.html) trait which allows us to [convert](https://doc.rust-lang.org/rust-by-example/print.html#to-and-from-strings) the type to [`String`](https://doc.rust-lang.org/rust-by-example/print.html#strings).

In _line 43_, `#[allow(dead_code)]` is an [attribute](https://doc.rust-lang.org/rust-by-example/print.html#attributes) which only applies to the item after it.

### Activities

- Fix the issue in the above code (see FIXME) so that it runs without
error.
- Try uncommenting the line that attempts to format the `Structure` struct
(see TODO)
- Add a `println!` macro call that prints: `Pi is roughly 3.142` by controlling
the number of decimal places shown. For the purposes of this exercise, use
`let pi = 3.141592` as an estimate for pi. (Hint: you may need to check the
[`std::fmt`](https://doc.rust-lang.org/std/fmt/) documentation for setting the number of decimals to display)

### See also:

[`std::fmt`](https://doc.rust-lang.org/std/fmt/), [`macros`](https://doc.rust-lang.org/rust-by-example/print.html#macro_rules), [`struct`](https://doc.rust-lang.org/rust-by-example/print.html#structures), [`traits`](https://doc.rust-lang.org/std/fmt/#formatting-traits), and [`dead_code`](https://doc.rust-lang.org/rust-by-example/print.html#dead_code)

# Debug

All types which want to use `std::fmt` formatting `traits` require an
implementation to be printable. Automatic implementations are only provided
for types such as in the `std` library. All others _must_ be manually
implemented somehow.

The `fmt::Debug``trait` makes this very straightforward. _All_ types can
`derive` (automatically create) the `fmt::Debug` implementation. This is
not true for `fmt::Display` which must be manually implemented.

```rust

#![allow(unused)]
fn main() {
// This structure cannot be printed either with `fmt::Display` or
// with `fmt::Debug`.
struct UnPrintable(i32);

// The `derive` attribute automatically creates the implementation
// required to make this `struct` printable with `fmt::Debug`.
#[derive(Debug)]
struct DebugPrintable(i32);
}
```

All `std` library types are automatically printable with `{:?}` too:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

So `fmt::Debug` definitely makes this printable but sacrifices some elegance.
Rust also provides “pretty printing” with `{:#?}`.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

One can manually implement `fmt::Display` to control the display.

### See also:

[`attributes`](https://doc.rust-lang.org/reference/attributes.html), [`derive`](https://doc.rust-lang.org/rust-by-example/print.html#derive), [`std::fmt`](https://doc.rust-lang.org/std/fmt/),
and [`struct`](https://doc.rust-lang.org/rust-by-example/print.html#structures)

# Display

`fmt::Debug` hardly looks compact and clean, so it is often advantageous to
customize the output appearance. This is done by manually implementing
[`fmt::Display`](https://doc.rust-lang.org/std/fmt/), which uses the `{}` print marker. Implementing it
looks like this:

```rust

#![allow(unused)]
fn main() {
// Import (via `use`) the `fmt` module to make it available.
use std::fmt;

// Define a structure for which `fmt::Display` will be implemented. This is
// a tuple struct named `Structure` that contains an `i32`.
struct Structure(i32);

// To use the `{}` marker, the trait `fmt::Display` must be implemented
// manually for the type.
impl fmt::Display for Structure {
    // This trait requires `fmt` with this exact signature.
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        // Write strictly the first element into the supplied output
        // stream: `f`. Returns `fmt::Result` which indicates whether the
        // operation succeeded or failed. Note that `write!` uses syntax which
        // is very similar to `println!`.
        write!(f, "{}", self.0)
    }
}
}
```

`fmt::Display` may be cleaner than `fmt::Debug` but this presents
a problem for the `std` library. How should ambiguous types be displayed?
For example, if the `std` library implemented a single style for all
`Vec<T>`, what style should it be? Would it be either of these two?

- `Vec<path>`: `/:/etc:/home/username:/bin` (split on `:`)
- `Vec<number>`: `1,2,3` (split on `,`)

No, because there is no ideal style for all types and the `std` library
doesn’t presume to dictate one. `fmt::Display` is not implemented for `Vec<T>`
or for any other generic containers. `fmt::Debug` must then be used for these
generic cases.

This is not a problem though because for any new _container_ type which is
_not_ generic, `fmt::Display` can be implemented.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

So, `fmt::Display` has been implemented but `fmt::Binary` has not, and therefore
cannot be used. `std::fmt` has many such [`traits`](https://doc.rust-lang.org/std/fmt/#formatting-traits) and each requires
its own implementation. This is detailed further in [`std::fmt`](https://doc.rust-lang.org/std/fmt/).

### Activity

After checking the output of the above example, use the `Point2D` struct as a
guide to add a `Complex` struct to the example. When printed in the same
way, the output should be:

```txt

Display: 3.3 +7.2i
Debug: Complex { real: 3.3, imag: 7.2 }

Display: 4.7 -2.3i
Debug: Complex { real: 4.7, imag: -2.3 }
```

Bonus: Add a space after the `+`/`-` signs.

Hints in case you get stuck:

- Check the documentation for [`Sign/#/0`](https://doc.rust-lang.org/std/fmt/#sign0) in `std::fmt`.
- Bonus: Check [`if`-`else`](https://doc.rust-lang.org/rust-by-example/print.html#ifelse) branching and the [`abs`](https://doc.rust-lang.org/std/primitive.f64.html#method.abs) function.

### See also:

[`derive`](https://doc.rust-lang.org/rust-by-example/print.html#derive), [`std::fmt`](https://doc.rust-lang.org/std/fmt/), [`macros`](https://doc.rust-lang.org/rust-by-example/print.html#macro_rules), [`struct`](https://doc.rust-lang.org/rust-by-example/print.html#structures),
[`trait`](https://doc.rust-lang.org/std/fmt/#formatting-traits), and [`use`](https://doc.rust-lang.org/rust-by-example/print.html#the-use-declaration)

# Testcase: List

Implementing `fmt::Display` for a structure where the elements must each be
handled sequentially is tricky. The problem is that each `write!` generates a
`fmt::Result`. Proper handling of this requires dealing with _all_ the
results. Rust provides the `?` operator for exactly this purpose.

Using `?` on `write!` looks like this:

```rust

// Try `write!` to see if it errors. If it errors, return
// the error. Otherwise continue.
write!(f, "{}", value)?;
```

With `?` available, implementing `fmt::Display` for a `Vec` is
straightforward:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### Activity

Try changing the program so that the index of each element in the vector is also
printed. The new output should look like this:

```rust

[0: 1, 1: 2, 2: 3]
```

### See also:

[`for`](https://doc.rust-lang.org/rust-by-example/print.html#for-loops), [`ref`](https://doc.rust-lang.org/rust-by-example/print.html#the-ref-pattern), [`Result`](https://doc.rust-lang.org/rust-by-example/print.html#result-1), [`struct`](https://doc.rust-lang.org/rust-by-example/print.html#structures),
[`?`](https://doc.rust-lang.org/rust-by-example/print.html#), and [`vec!`](https://doc.rust-lang.org/rust-by-example/print.html#vectors)

# Formatting

We’ve seen that formatting is specified via a _format string_:

- `format!("{}", foo)` -\> `"3735928559"`
- `format!("0x{:X}", foo)` -\> [`"0xDEADBEEF"`](https://en.wikipedia.org/wiki/Deadbeef#Magic_debug_values)
- `format!("0o{:o}", foo)` -\> `"0o33653337357"`

The same variable (`foo`) can be formatted differently depending on which
_argument type_ is used: `X` vs `o` vs _unspecified_.

This formatting functionality is implemented via traits, and there is one trait
for each argument type. The most common formatting trait is `Display`, which
handles cases where the argument type is left unspecified: `{}` for instance.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

You can view a [full list of formatting traits](https://doc.rust-lang.org/std/fmt/#formatting-traits) and their argument
types in the [`std::fmt`](https://doc.rust-lang.org/std/fmt/) documentation.

### Activity

Add an implementation of the `fmt::Display` trait for the `Color` struct above
so that the output displays as:

```text

RGB (128, 255, 90) 0x80FF5A
RGB (0, 3, 254) 0x0003FE
RGB (0, 0, 0) 0x000000
```

Two hints if you get stuck:

- You [may need to list each color more than once](https://doc.rust-lang.org/std/fmt/#named-parameters).
- You can [pad with zeros to a width of 2](https://doc.rust-lang.org/std/fmt/#width) with `:0>2`.
For hexadecimals, you can use `:02X`.

Bonus:

- If you would like to experiment with [type casting](https://doc.rust-lang.org/rust-by-example/print.html#casting) in advance,
the formula for [calculating a color in the RGB color space](https://www.rapidtables.com/web/color/RGB_Color.html#rgb-format) is
`RGB = (R * 65_536) + (G * 256) + B`, where `R is RED, G is GREEN, and B is BLUE`.
An unsigned 8-bit integer (`u8`) can only hold numbers up to 255. To cast `u8` to `u32`, you can write `variable_name as u32`.

### See also:

[`std::fmt`](https://doc.rust-lang.org/std/fmt/)

# Primitives

Rust provides access to a wide variety of `primitives`. A sample includes:

### Scalar Types

- Signed integers: `i8`, `i16`, `i32`, `i64`, `i128` and `isize` (pointer size)
- Unsigned integers: `u8`, `u16`, `u32`, `u64`, `u128` and `usize` (pointer
size)
- Floating point: `f32`, `f64`
- `char` Unicode scalar values like `'a'`, `'α'` and `'∞'` (4 bytes each)
- `bool` either `true` or `false`
- The unit type `()`, whose only possible value is an empty tuple: `()`

Despite the value of a unit type being a tuple, it is not considered a compound
type because it does not contain multiple values.

### Compound Types

- Arrays like `[1, 2, 3]`
- Tuples like `(1, true)`

Variables can always be _type annotated_. Numbers may additionally be annotated
via a _suffix_ or _by default_. Integers default to `i32` and floats to `f64`.
Note that Rust can also infer types from context.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[the `std` library](https://doc.rust-lang.org/std/), [`mut`](https://doc.rust-lang.org/rust-by-example/print.html#mutability), [`inference`](https://doc.rust-lang.org/rust-by-example/print.html#inference), and
[`shadowing`](https://doc.rust-lang.org/rust-by-example/print.html#scope-and-shadowing)

# Literals and operators

Integers `1`, floats `1.2`, characters `'a'`, strings `"abc"`, booleans `true`
and the unit type `()` can be expressed using literals.

Integers can, alternatively, be expressed using hexadecimal, octal or binary
notation using these prefixes respectively: `0x`, `0o` or `0b`.

Underscores can be inserted in numeric literals to improve readability, e.g.
`1_000` is the same as `1000`, and `0.000_001` is the same as `0.000001`.

Rust also supports scientific [E-notation](https://en.wikipedia.org/wiki/Scientific_notation#E_notation), e.g. `1e6`, `7.6e-4`. The
associated type is `f64`.

We need to tell the compiler the type of the literals we use. For now,
we’ll use the `u32` suffix to indicate that the literal is an unsigned 32-bit
integer, and the `i32` suffix to indicate that it’s a signed 32-bit integer.

The operators available and their precedence [in Rust](https://doc.rust-lang.org/reference/expressions.html#expression-precedence) are similar
to other [C-like languages](https://en.wikipedia.org/wiki/Operator_precedence#Programming_languages).

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Tuples

A tuple is a collection of values of different types. Tuples are constructed
using parentheses `()`, and each tuple itself is a value with type signature
`(T1, T2, ...)`, where `T1`, `T2` are the types of its members. Functions can
use tuples to return multiple values, as tuples can hold any number of values.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### Activity

1. _Recap_: Add the `fmt::Display` trait to the `Matrix` struct in the above
example, so that if you switch from printing the debug format `{:?}` to the
display format `{}`, you see the following output:


```text

( 1.1 1.2 )
( 2.1 2.2 )
```


You may want to refer back to the example for [print display](https://doc.rust-lang.org/rust-by-example/print.html#display).

2. Add a `transpose` function using the `reverse` function as a template, which
accepts a matrix as an argument, and returns a matrix in which two elements
have been swapped. For example:


```rust

println!("Matrix:\n{}", matrix);
println!("Transpose:\n{}", transpose(matrix));
```


Results in the output:


```text

Matrix:
( 1.1 1.2 )
( 2.1 2.2 )
Transpose:
( 1.1 2.1 )
( 1.2 2.2 )
```


# Arrays and Slices

An array is a collection of objects of the same type `T`, stored in contiguous
memory. Arrays are created using brackets `[]`, and their length, which is known
at compile time, is part of their type signature `[T; length]`.

Slices are similar to arrays, but their length is not known at compile time.
Instead, a slice is a two-word object; the first word is a pointer to the data,
the second word is the length of the slice. The word size is the same as usize,
determined by the processor architecture, e.g. 64 bits on an x86-64. Slices can
be used to borrow a section of an array and have the type signature `&[T]`.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Custom Types

Rust custom data types are formed mainly through the two keywords:

- `struct`: define a structure
- `enum`: define an enumeration

Constants can also be created via the `const` and `static` keywords.

# Structures

There are three types of structures (“structs”) that can be created using the
`struct` keyword:

- Tuple structs, which are, basically, named tuples.
- The classic [C structs](https://en.wikipedia.org/wiki/Struct_(C_programming_language))
- Unit structs, which are field-less, are useful for generics.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### Activity

1. Add a function `rect_area` which calculates the area of a `Rectangle` (try
using nested destructuring).
2. Add a function `square` which takes a `Point` and a `f32` as arguments, and
returns a `Rectangle` with its top left corner on the point, and a width and
height corresponding to the `f32`.

### See also

[`attributes`](https://doc.rust-lang.org/rust-by-example/print.html#attributes), [raw identifiers](https://doc.rust-lang.org/rust-by-example/print.html#raw-identifiers) and [destructuring](https://doc.rust-lang.org/rust-by-example/print.html#destructuring)

# Enums

The `enum` keyword allows the creation of a type which may be one of a few
different variants. Any variant which is valid as a `struct` is also valid in
an `enum`.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

## Type aliases

If you use a type alias, you can refer to each enum variant via its alias.
This might be useful if the enum’s name is too long or too generic, and you
want to rename it.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

The most common place you’ll see this is in `impl` blocks using the `Self` alias.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

To learn more about enums and type aliases, you can read the
[stabilization report](https://github.com/rust-lang/rust/pull/61682/#issuecomment-502472847) from when this feature was stabilized into
Rust.

### See also:

[`match`](https://doc.rust-lang.org/rust-by-example/print.html#match), [`fn`](https://doc.rust-lang.org/rust-by-example/print.html#functions), and [`String`](https://doc.rust-lang.org/rust-by-example/print.html#strings), [“Type alias enum variants” RFC](https://rust-lang.github.io/rfcs/2338-type-alias-enum-variants.html)

# use

The `use` declaration can be used to avoid typing the full module path to access a name:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[`match`](https://doc.rust-lang.org/rust-by-example/print.html#match) and [`use`](https://doc.rust-lang.org/rust-by-example/print.html#the-use-declaration)

# C-like

`enum` can also be used as C-like enums.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[casting](https://doc.rust-lang.org/rust-by-example/print.html#casting)

# Testcase: linked-list

A common way to implement a linked-list is via `enums`:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[`Box`](https://doc.rust-lang.org/rust-by-example/print.html#box-stack-and-heap) and [methods](https://doc.rust-lang.org/rust-by-example/print.html#associated-functions--methods)

# constants

Rust has two different types of constants which can be declared in any scope
including global. Both require explicit type annotation:

- `const`: An unchangeable value (the common case).
- `static`: A possibly mutable variable with [`'static`](https://doc.rust-lang.org/rust-by-example/print.html#static) lifetime.
The static lifetime is inferred and does not have to be specified.
Accessing or modifying a mutable static variable is [`unsafe`](https://doc.rust-lang.org/rust-by-example/print.html#unsafe-operations).

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[The `const`/`static` RFC](https://github.com/rust-lang/rfcs/blob/master/text/0246-const-vs-static.md),
[`'static` lifetime](https://doc.rust-lang.org/rust-by-example/print.html#static)

# Variable Bindings

Rust provides type safety via static typing. Variable bindings can be type
annotated when declared. However, in most cases, the compiler will be able
to infer the type of the variable from the context, heavily reducing the
annotation burden.

Values (like literals) can be bound to variables, using the `let` binding.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Mutability

Variable bindings are immutable by default, but this can be overridden using
the `mut` modifier.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

The compiler will throw a detailed diagnostic about mutability errors.

# Scope and Shadowing

Variable bindings have a scope, and are constrained to live in a _block_. A
block is a collection of statements enclosed by braces `{}`.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Also, [variable shadowing](https://en.wikipedia.org/wiki/Variable_shadowing) is allowed.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Declare first

It is possible to declare variable bindings first and initialize them later, but all variable bindings must be initialized before they are used: the compiler forbids use of uninitialized variable bindings, as it would lead to undefined behavior.

It is not common to declare a variable binding and initialize it later in the function.
It is more difficult for a reader to find the initialization when initialization is separated from declaration.
It is common to declare and initialize a variable binding near where the variable will be used.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Freezing

When data is bound by the same name immutably, it also _freezes_. _Frozen_ data can’t be
modified until the immutable binding goes out of scope:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Types

Rust provides several mechanisms to change or define the type of primitive and
user defined types. The following sections cover:

- [Casting](https://doc.rust-lang.org/rust-by-example/print.html#casting) between primitive types
- Specifying the desired type of [literals](https://doc.rust-lang.org/rust-by-example/print.html#literals)
- Using [type inference](https://doc.rust-lang.org/rust-by-example/print.html#inference)
- [Aliasing](https://doc.rust-lang.org/rust-by-example/print.html#aliasing) types

# Casting

Rust provides no implicit type conversion (coercion) between primitive types.
But, explicit type conversion (casting) can be performed using the `as` keyword.

Rules for converting between integral types follow C conventions generally,
except in cases where C has undefined behavior. The behavior of all casts
between integral types is well defined in Rust.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Literals

Numeric literals can be type annotated by adding the type as a suffix. As an example,
to specify that the literal `42` should have the type `i32`, write `42i32`.

The type of unsuffixed numeric literals will depend on how they are used. If no
constraint exists, the compiler will use `i32` for integers, and `f64` for
floating-point numbers.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

There are some concepts used in the previous code that haven’t been explained
yet, here’s a brief explanation for the impatient readers:

- `std::mem::size_of_val` is a function, but called with its _full path_. Code
can be split in logical units called _modules_. In this case, the
`size_of_val` function is defined in the `mem` module, and the `mem` module
is defined in the `std` _crate_. For more details, see
[modules](https://doc.rust-lang.org/rust-by-example/print.html#modules) and [crates](https://doc.rust-lang.org/rust-by-example/print.html#crates).

# Inference

The type inference engine is pretty smart. It does more than looking at the
type of the value expression
during an initialization. It also looks at how the variable is used afterwards
to infer its type. Here’s an advanced example of type inference:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

No type annotation of variables was needed, the compiler is happy and so is the
programmer!

# Aliasing

The `type` statement can be used to give a new name to an existing type. Types
must have `UpperCamelCase` names, or the compiler will raise a warning. The
exception to this rule are the primitive types: `usize`, `f32`, etc.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

The main use of aliases is to reduce boilerplate; for example the `io::Result<T>` type
is an alias for the `Result<T, io::Error>` type.

### See also:

[Attributes](https://doc.rust-lang.org/rust-by-example/print.html#attributes)

# Conversion

Primitive types can be converted to each other through [casting](https://doc.rust-lang.org/rust-by-example/print.html#casting).

Rust addresses conversion between custom types (i.e., `struct` and `enum`)
by the use of [traits](https://doc.rust-lang.org/rust-by-example/print.html#traits-2). The generic
conversions will use the [`From`](https://doc.rust-lang.org/std/convert/trait.From.html) and [`Into`](https://doc.rust-lang.org/std/convert/trait.Into.html) traits. However there are more
specific ones for the more common cases, in particular when converting to and
from `String`s.

# `From` and `Into`

The [`From`](https://doc.rust-lang.org/std/convert/trait.From.html) and [`Into`](https://doc.rust-lang.org/std/convert/trait.Into.html) traits are inherently linked, and this is actually part of
its implementation. If you are able to convert type A from type B, then it
should be easy to believe that we should be able to convert type B to type A.

## `From`

The [`From`](https://doc.rust-lang.org/std/convert/trait.From.html) trait allows for a type to define how to create itself from another
type, hence providing a very simple mechanism for converting between several
types. There are numerous implementations of this trait within the standard
library for conversion of primitive and common types.

For example we can easily convert a `str` into a `String`

```rust

#![allow(unused)]
fn main() {
let my_str = "hello";
let my_string = String::from(my_str);
}
```

We can do something similar for defining a conversion for our own type.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

## `Into`

The [`Into`](https://doc.rust-lang.org/std/convert/trait.Into.html) trait is simply the reciprocal of the `From` trait. It
defines how to convert a type into another type.

Calling `into()` typically requires us to specify the result type as the compiler is unable to determine this most of the time.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

## `From` and `Into` are interchangeable

`From` and `Into` are designed to be complementary.
We do not need to provide an implementation for both traits.
If you have implemented the `From` trait for your type, `Into` will call it
when necessary. Note, however, that the converse is not true: implementing `Into` for your type will not automatically provide it with an implementation of `From`.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# `TryFrom` and `TryInto`

Similar to [`From` and `Into`](https://doc.rust-lang.org/rust-by-example/print.html#from-and-into), [`TryFrom`](https://doc.rust-lang.org/std/convert/trait.TryFrom.html) and [`TryInto`](https://doc.rust-lang.org/std/convert/trait.TryInto.html) are
generic traits for converting between types. Unlike `From`/`Into`, the
`TryFrom`/`TryInto` traits are used for fallible conversions, and as such,
return [`Result`](https://doc.rust-lang.org/std/result/enum.Result.html) s.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# To and from Strings

## Converting to String

To convert any type to a `String` is as simple as implementing the [`ToString`](https://doc.rust-lang.org/std/string/trait.ToString.html)
trait for the type. Rather than doing so directly, you should implement the
[`fmt::Display`](https://doc.rust-lang.org/std/fmt/trait.Display.html) trait which automatically provides [`ToString`](https://doc.rust-lang.org/std/string/trait.ToString.html) and
also allows printing the type as discussed in the section on [`print!`](https://doc.rust-lang.org/rust-by-example/print.html#formatted-print).

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

## Parsing a String

It’s useful to convert strings into many types, but one of the more common string
operations is to convert them from string to number. The idiomatic approach to
this is to use the [`parse`](https://doc.rust-lang.org/std/primitive.str.html#method.parse) function and either to arrange for type inference or
to specify the type to parse using the ‘turbofish’ syntax. Both alternatives are
shown in the following example.

This will convert the string into the type specified as long as the [`FromStr`](https://doc.rust-lang.org/std/str/trait.FromStr.html)
trait is implemented for that type. This is implemented for numerous types
within the standard library.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

To obtain this functionality on a user defined type simply implement the
[`FromStr`](https://doc.rust-lang.org/std/str/trait.FromStr.html) trait for that type.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Expressions

A Rust program is (mostly) made up of a series of statements:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

There are a few kinds of statements in Rust. The most common two are declaring
a variable binding, and using a `;` with an expression:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Blocks are expressions too, so they can be used as values in
assignments. The last expression in the block will be assigned to the
place expression such as a local variable. However, if the last expression of the block ends with a
semicolon, the return value will be `()`.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Flow of Control

An integral part of any programming language are ways to modify control flow:
`if`/`else`, `for`, and others. Let’s talk about them in Rust.

# if/else

Branching with `if`-`else` is similar to other languages. Unlike many of them,
the boolean condition doesn’t need to be surrounded by parentheses, and each
condition is followed by a block. `if`-`else` conditionals are expressions,
and, all branches must return the same type.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# loop

Rust provides a `loop` keyword to indicate an infinite loop.

The `break` statement can be used to exit a loop at anytime, whereas the
`continue` statement can be used to skip the rest of the iteration and start a
new one.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Nesting and labels

It’s possible to `break` or `continue` outer loops when dealing with nested
loops. In these cases, the loops must be annotated with some `'label`, and the
label must be passed to the `break`/`continue` statement.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Returning from loops

One of the uses of a `loop` is to retry an operation until it succeeds. If the
operation returns a value though, you might need to pass it to the rest of the
code: put it after the `break`, and it will be returned by the `loop`
expression.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# while

The `while` keyword can be used to run a loop while a condition is true.

Let’s write the infamous [FizzBuzz](https://en.wikipedia.org/wiki/Fizz_buzz) using a `while` loop.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# for loops

## for and range

The `for in` construct can be used to iterate through an `Iterator`.
One of the easiest ways to create an iterator is to use the range
notation `a..b`. This yields values from `a` (inclusive) to `b`
(exclusive) in steps of one.

Let’s write FizzBuzz using `for` instead of `while`.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Alternatively, `a..=b` can be used for a range that is inclusive on both ends.
The above can be written as:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

## for and iterators

The `for in` construct is able to interact with an `Iterator` in several ways.
As discussed in the section on the [Iterator](https://doc.rust-lang.org/rust-by-example/print.html#iterators) trait, by default the `for`
loop will apply the `into_iter` function to the collection. However, this is
not the only means of converting collections into iterators.

`into_iter`, `iter` and `iter_mut` all handle the conversion of a collection
into an iterator in different ways, by providing different views on the data
within.

- `iter` \- This borrows each element of the collection through each iteration.
Thus leaving the collection untouched and available for reuse after the loop.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

- `into_iter` \- This consumes the collection so that on each iteration the exact
data is provided. Once the collection has been consumed it is no longer
available for reuse as it has been ‘moved’ within the loop.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

- `iter_mut` \- This mutably borrows each element of the collection, allowing for
the collection to be modified in place.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

In the above snippets note the type of `match` branch, that is the key
difference in the types of iteration. The difference in type then of course
implies differing actions that are able to be performed.

### See also:

[Iterator](https://doc.rust-lang.org/rust-by-example/print.html#iterators)

# match

Rust provides pattern matching via the `match` keyword, which can be used like
a C `switch`. The first matching arm is evaluated and all possible values must be
covered.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Destructuring

A `match` block can destructure items in a variety of ways.

- [Destructuring Tuples](https://doc.rust-lang.org/rust-by-example/print.html#tuples-1)
- [Destructuring Arrays and Slices](https://doc.rust-lang.org/rust-by-example/print.html#arraysslices)
- [Destructuring Enums](https://doc.rust-lang.org/rust-by-example/print.html#enums-1)
- [Destructuring Pointers](https://doc.rust-lang.org/rust-by-example/print.html#pointersref)
- [Destructuring Structures](https://doc.rust-lang.org/rust-by-example/print.html#structs)

### See also:

[The Rust Reference for Destructuring](https://doc.rust-lang.org/reference/patterns.html#r-patterns.destructure)

# tuples

Tuples can be destructured in a `match` as follows:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[Tuples](https://doc.rust-lang.org/rust-by-example/print.html#tuples)

# arrays/slices

Like tuples, arrays and slices can be destructured this way:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[Arrays and Slices](https://doc.rust-lang.org/rust-by-example/print.html#arrays-and-slices) and [Binding](https://doc.rust-lang.org/rust-by-example/print.html#binding) for `@` sigil

# enums

An `enum` is destructured similarly:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[`#[allow(...)]`](https://doc.rust-lang.org/rust-by-example/print.html#dead_code), [color models](https://en.wikipedia.org/wiki/Color_model) and [`enum`](https://doc.rust-lang.org/rust-by-example/print.html#enums)

# pointers/ref

For pointers, a distinction needs to be made between destructuring
and dereferencing as they are different concepts which are used
differently from languages like C/C++.

- Dereferencing uses `*`
- Destructuring uses `&`, `ref`, and `ref mut`

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[The ref pattern](https://doc.rust-lang.org/rust-by-example/print.html#the-ref-pattern)

# structs

Similarly, a `struct` can be destructured as shown:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[Structs](https://doc.rust-lang.org/rust-by-example/print.html#structures)

# Guards

A `match` _guard_ can be added to filter the arm.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Note that the compiler won’t take guard conditions into account when checking
if all patterns are covered by the match expression.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[Tuples](https://doc.rust-lang.org/rust-by-example/print.html#tuples) [Enums](https://doc.rust-lang.org/rust-by-example/print.html#enums)

# Binding

Indirectly accessing a variable makes it impossible to branch and use that
variable without re-binding. `match` provides the `@` sigil for binding values to
names:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

You can also use binding to “destructure” `enum` variants, such as `Option`:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[`functions`](https://doc.rust-lang.org/rust-by-example/print.html#functions), [`enums`](https://doc.rust-lang.org/rust-by-example/print.html#enums) and [`Option`](https://doc.rust-lang.org/rust-by-example/print.html#option)

# if let

For some use cases, when matching enums, `match` is awkward. For example:

```rust

#![allow(unused)]
fn main() {
// Make `optional` of type `Option<i32>`
let optional = Some(7);

match optional {
    Some(i) => println!("This is a really long string and `{:?}`", i),
    _ => {},
    // ^ Required because `match` is exhaustive. Doesn't it seem
    // like wasted space?
};

}
```

`if let` is cleaner for this use case and in addition allows various
failure options to be specified:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

In the same way, `if let` can be used to match any enum value:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Another benefit is that `if let` allows us to match non-parameterized enum variants. This is true even in cases where the enum doesn’t implement or derive `PartialEq`. In such cases `if Foo::Bar == a` would fail to compile, because instances of the enum cannot be equated, however `if let` will continue to work.

Would you like a challenge? Fix the following example to use `if let`:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[`enum`](https://doc.rust-lang.org/rust-by-example/print.html#enums), [`Option`](https://doc.rust-lang.org/rust-by-example/print.html#option), and the [RFC](https://github.com/rust-lang/rfcs/pull/160)

# let-else

> 🛈 stable since: rust 1.65
>
> 🛈 you can target specific edition by compiling like this
> `rustc --edition=2021 main.rs`

With `let`-`else`, a refutable pattern can match and bind variables
in the surrounding scope like a normal `let`, or else diverge (e.g. `break`,
`return`, `panic!`) when the pattern doesn’t match.

```rust

use std::str::FromStr;

fn get_count_item(s: &str) -> (u64, &str) {
    let mut it = s.split(' ');
    let (Some(count_str), Some(item)) = (it.next(), it.next()) else {
        panic!("Can't segment count item pair: '{s}'");
    };
    let Ok(count) = u64::from_str(count_str) else {
        panic!("Can't parse integer: '{count_str}'");
    };
    (count, item)
}

fn main() {
    assert_eq!(get_count_item("3 chairs"), (3, "chairs"));
}
```

The scope of name bindings is the main thing that makes this different from
`match` or `if let`-`else` expressions. You could previously approximate these
patterns with an unfortunate bit of repetition and an outer `let`:

```rust

#![allow(unused)]
fn main() {
use std::str::FromStr;

fn get_count_item(s: &str) -> (u64, &str) {
    let mut it = s.split(' ');
    let (count_str, item) = match (it.next(), it.next()) {
        (Some(count_str), Some(item)) => (count_str, item),
        _ => panic!("Can't segment count item pair: '{s}'"),
    };
    let count = if let Ok(count) = u64::from_str(count_str) {
        count
    } else {
        panic!("Can't parse integer: '{count_str}'");
    };
    (count, item)
}

assert_eq!(get_count_item("3 chairs"), (3, "chairs"));
}
```

### See also:

[option](https://doc.rust-lang.org/rust-by-example/print.html#option), [match](https://doc.rust-lang.org/rust-by-example/print.html#match), [if let](https://doc.rust-lang.org/rust-by-example/print.html#if-let) and the [let-else RFC](https://rust-lang.github.io/rfcs/3137-let-else.html).

# while let

Similar to `if let`, `while let` can make awkward `match` sequences
more tolerable. Consider the following sequence that increments `i`:

```rust

#![allow(unused)]
fn main() {
// Make `optional` of type `Option<i32>`
let mut optional = Some(0);

// Repeatedly try this test.
loop {
    match optional {
        // If `optional` destructures, evaluate the block.
        Some(i) => {
            if i > 9 {
                println!("Greater than 9, quit!");
                optional = None;
            } else {
                println!("`i` is `{:?}`. Try again.", i);
                optional = Some(i + 1);
            }
            // ^ Requires 3 indentations!
        },
        // Quit the loop when the destructure fails:
        _ => { break; }
        // ^ Why should this be required? There must be a better way!
    }
}
}
```

Using `while let` makes this sequence much nicer:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[`enum`](https://doc.rust-lang.org/rust-by-example/print.html#enums), [`Option`](https://doc.rust-lang.org/rust-by-example/print.html#option), and the [RFC](https://github.com/rust-lang/rfcs/pull/214)

# Functions

Functions are declared using the `fn` keyword. Its arguments are type
annotated, just like variables, and, if the function returns a value, the
return type must be specified after an arrow `->`.

The final expression in the function will be used as return value.
Alternatively, the `return` statement can be used to return a value earlier
from within the function, even from inside loops or `if` statements.

Let’s rewrite FizzBuzz using functions!

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Associated functions & Methods

Some functions are connected to a particular type. These come in two forms:
associated functions, and methods. Associated functions are functions that
are defined on a type generally, while methods are associated functions that are
called on a particular instance of a type.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Closures

Closures are functions that can capture the enclosing environment. For
example, a closure that captures the `x` variable:

```rust

|val| val + x
```

The syntax and capabilities of closures make them very convenient for
on the fly usage. Calling a closure is exactly like calling a function.
However, both input and return types _can_ be inferred and input
variable names _must_ be specified.

Other characteristics of closures include:

- using `||` instead of `()` around input variables.
- optional body delimitation (`{}`) for a single line expression (mandatory otherwise).
- the ability to capture the outer environment variables.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Capturing

Closures are inherently flexible and will do what the functionality requires
to make the closure work without annotation. This allows capturing to
flexibly adapt to the use case, sometimes moving and sometimes borrowing.
Closures can capture variables:

- by reference: `&T`
- by mutable reference: `&mut T`
- by value: `T`

They preferentially capture variables by reference and only go lower when
required.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Using `move` before vertical pipes forces closure
to take ownership of captured variables:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[`Box`](https://doc.rust-lang.org/rust-by-example/print.html#box-stack-and-heap) and [`std::mem::drop`](https://doc.rust-lang.org/std/mem/fn.drop.html)

# As input parameters

While Rust chooses how to capture variables on the fly mostly without type
annotation, this ambiguity is not allowed when writing functions. When
taking a closure as an input parameter, the closure’s complete type must be
annotated using one of a few `traits`, and they’re determined by what the
closure does with captured value. In order of decreasing restriction,
they are:

- `Fn`: the closure uses the captured value by reference (`&T`)
- `FnMut`: the closure uses the captured value by mutable reference (`&mut T`)
- `FnOnce`: the closure uses the captured value by value (`T`)

On a variable-by-variable basis, the compiler will capture variables in the
least restrictive manner possible.

For instance, consider a parameter annotated as `FnOnce`. This specifies
that the closure _may_ capture by `&T`, `&mut T`, or `T`, but the compiler
will ultimately choose based on how the captured variables are used in the
closure.

This is because if a move is possible, then any type of borrow should also
be possible. Note that the reverse is not true. If the parameter is
annotated as `Fn`, then capturing variables by `&mut T` or `T` are not
allowed. However, `&T` is allowed.

In the following example, try swapping the usage of `Fn`, `FnMut`, and
`FnOnce` to see what happens:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[`std::mem::drop`](https://doc.rust-lang.org/std/mem/fn.drop.html), [`Fn`](https://doc.rust-lang.org/std/ops/trait.Fn.html), [`FnMut`](https://doc.rust-lang.org/std/ops/trait.FnMut.html), [Generics](https://doc.rust-lang.org/rust-by-example/print.html#generics), [where](https://doc.rust-lang.org/rust-by-example/print.html#where-clauses) and [`FnOnce`](https://doc.rust-lang.org/std/ops/trait.FnOnce.html)

# Type anonymity

Closures succinctly capture variables from enclosing scopes. Does this have
any consequences? It surely does. Observe how using a closure as a function
parameter requires [generics](https://doc.rust-lang.org/rust-by-example/print.html#generics), which is necessary because of how they are
defined:

```rust

#![allow(unused)]
fn main() {
// `F` must be generic.
fn apply<F>(f: F) where
    F: FnOnce() {
    f();
}
}
```

When a closure is defined, the compiler implicitly creates a new
anonymous structure to store the captured variables inside, meanwhile
implementing the functionality via one of the `traits`: `Fn`, `FnMut`, or
`FnOnce` for this unknown type. This type is assigned to the variable which
is stored until calling.

Since this new type is of unknown type, any usage in a function will require
generics. However, an unbounded type parameter `<T>` would still be ambiguous
and not be allowed. Thus, bounding by one of the `traits`: `Fn`, `FnMut`, or
`FnOnce` (which it implements) is sufficient to specify its type.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[A thorough analysis](https://huonw.github.io/blog/2015/05/finding-closure-in-rust/), [`Fn`](https://doc.rust-lang.org/std/ops/trait.Fn.html), [`FnMut`](https://doc.rust-lang.org/std/ops/trait.FnMut.html),
and [`FnOnce`](https://doc.rust-lang.org/std/ops/trait.FnOnce.html)

# Input functions

Since closures may be used as arguments, you might wonder if the same can be said
about functions. And indeed they can! If you declare a function that takes a
closure as parameter, then any function that satisfies the trait bound of that
closure can be passed as a parameter.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

As an additional note, the `Fn`, `FnMut`, and `FnOnce``traits` dictate how
a closure captures variables from the enclosing scope.

### See also:

[`Fn`](https://doc.rust-lang.org/std/ops/trait.Fn.html), [`FnMut`](https://doc.rust-lang.org/std/ops/trait.FnMut.html), and [`FnOnce`](https://doc.rust-lang.org/std/ops/trait.FnOnce.html)

# As output parameters

Closures as input parameters are possible, so returning closures as
output parameters should also be possible. However, anonymous
closure types are, by definition, unknown, so we have to use
`impl Trait` to return them.

The valid traits for returning a closure are:

- `Fn`
- `FnMut`
- `FnOnce`

Beyond this, the `move` keyword must be used, which signals that all captures
occur by value. This is required because any captures by reference would be
dropped as soon as the function exited, leaving invalid references in the
closure.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[`Fn`](https://doc.rust-lang.org/std/ops/trait.Fn.html), [`FnMut`](https://doc.rust-lang.org/std/ops/trait.FnMut.html), [Generics](https://doc.rust-lang.org/rust-by-example/print.html#generics) and [impl Trait](https://doc.rust-lang.org/rust-by-example/print.html#impl-trait).

# Examples in `std`

This section contains a few examples of using closures from the `std` library.

# Iterator::any

`Iterator::any` is a function which when passed an iterator, will return
`true` if any element satisfies the predicate. Otherwise `false`. Its
signature:

```rust

pub trait Iterator {
    // The type being iterated over.
    type Item;

    // `any` takes `&mut self` meaning the caller may be borrowed
    // and modified, but not consumed.
    fn any<F>(&mut self, f: F) -> bool where
        // `FnMut` meaning any captured variable may at most be
        // modified, not consumed. `Self::Item` is the closure parameter type,
        // which is determined by the iterator (e.g., `&T` for `.iter()`,
        // `T` for `.into_iter()`).
        F: FnMut(Self::Item) -> bool;
}
```

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[`std::iter::Iterator::any`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.any)

# Searching through iterators

`Iterator::find` is a function which iterates over an iterator and searches for the
first value which satisfies some condition. If none of the values satisfy the
condition, it returns `None`. Its signature:

```rust

pub trait Iterator {
    // The type being iterated over.
    type Item;

    // `find` takes `&mut self` meaning the caller may be borrowed
    // and modified, but not consumed.
    fn find<P>(&mut self, predicate: P) -> Option<Self::Item> where
        // `FnMut` meaning any captured variable may at most be
        // modified, not consumed. `&Self::Item` states it takes
        // arguments to the closure by reference.
        P: FnMut(&Self::Item) -> bool;
}
```

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

`Iterator::find` gives you a reference to the item. But if you want the _index_ of the
item, use `Iterator::position`.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[`std::iter::Iterator::find`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.find)

[`std::iter::Iterator::find_map`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.find_map)

[`std::iter::Iterator::position`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.position)

[`std::iter::Iterator::rposition`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#method.rposition)

# Higher Order Functions

Rust provides Higher Order Functions (HOF). These are functions that
take one or more functions and/or produce a more useful function. HOFs
and lazy iterators give Rust its functional flavor.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

[Option](https://doc.rust-lang.org/core/option/enum.Option.html)
and
[Iterator](https://doc.rust-lang.org/core/iter/trait.Iterator.html)
implement their fair share of HOFs.

# Diverging functions

Diverging functions never return. They are marked using `!`, which is an empty type.

```rust

#![allow(unused)]
fn main() {
fn foo() -> ! {
    panic!("This call never returns.");
}
}
```

As opposed to all the other types, this one cannot be instantiated, because the
set of all possible values this type can have is empty. Note that, it is
different from the `()` type, which has exactly one possible value.

For example, this function returns as usual, although there is no information
in the return value.

```rust

fn some_fn() {
    ()
}

fn main() {
    let _a: () = some_fn();
    println!("This function returns and you can see this line.");
}
```

As opposed to this function, which will never return the control back to the caller.

```rust

#![feature(never_type)]

fn main() {
    let x: ! = panic!("This call never returns.");
    println!("You will never see this line!");
}
```

Although this might seem like an abstract concept, it is actually very useful and
often handy. The main advantage of this type is that it can be cast to any other
type, making it versatile in situations where an exact type is required, such as
in match branches. This flexibility allows us to write code like this:

```rust

fn main() {
    fn sum_odd_numbers(up_to: u32) -> u32 {
        let mut acc = 0;
        for i in 0..up_to {
            // Notice that the return type of this match expression must be u32
            // because of the type of the "addition" variable.
            let addition: u32 = match i%2 == 1 {
                // The "i" variable is of type u32, which is perfectly fine.
                true => i,
                // On the other hand, the "continue" expression does not return
                // u32, but it is still fine, because it never returns and therefore
                // does not violate the type requirements of the match expression.
                false => continue,
            };
            acc += addition;
        }
        acc
    }
    println!("Sum of odd numbers up to 9 (excluding): {}", sum_odd_numbers(9));
}
```

It is also the return type of functions that loop forever (e.g. `loop {}`) like
network servers or functions that terminate the process (e.g. `exit()`).

# Modules

Rust provides a powerful module system that can be used to hierarchically split
code in logical units (modules), and manage visibility (public/private) between
them.

A module is a collection of items: functions, structs, traits, `impl` blocks,
and even other modules.

# Visibility

By default, the items in a module have private visibility, but this can be
overridden with the `pub` modifier. Only the public items of a module can be
accessed from outside the module scope.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Struct visibility

Structs have an extra level of visibility with their fields. The visibility
defaults to private, and can be overridden with the `pub` modifier. This
visibility only matters when a struct is accessed from outside the module
where it is defined, and has the goal of hiding information (encapsulation).

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[generics](https://doc.rust-lang.org/rust-by-example/print.html#generics) and [methods](https://doc.rust-lang.org/rust-by-example/print.html#associated-functions--methods)

# The `use` declaration

The `use` declaration can be used to bind a full path to a new name, for easier
access. It is often used like this:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

You can use the `as` keyword to bind imports to a different name:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

You can also use `pub use` to re-export an item from a module, so it can be
accessed through the module’s public interface:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# `super` and `self`

The `super` and `self` keywords can be used in the path to remove ambiguity
when accessing items and to prevent unnecessary hardcoding of paths.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# File hierarchy

Modules can be mapped to a file/directory hierarchy. Let’s break down the
[visibility example](https://doc.rust-lang.org/rust-by-example/print.html#visibility) in files:

```shell

$ tree .
.
├── my
│   ├── inaccessible.rs
│   └── nested.rs
├── my.rs
└── split.rs
```

In `split.rs`:

```rust

// This declaration will look for a file named `my.rs` and will
// insert its contents inside a module named `my` under this scope
mod my;

fn function() {
    println!("called `function()`");
}

fn main() {
    my::function();

    function();

    my::indirect_access();

    my::nested::function();
}
```

In `my.rs`:

```rust

// Similarly `mod inaccessible` and `mod nested` will locate the `nested.rs`
// and `inaccessible.rs` files and insert them here under their respective
// modules
mod inaccessible;
pub mod nested;

pub fn function() {
    println!("called `my::function()`");
}

fn private_function() {
    println!("called `my::private_function()`");
}

pub fn indirect_access() {
    print!("called `my::indirect_access()`, that\n> ");

    private_function();
}
```

In `my/nested.rs`:

```rust

pub fn function() {
    println!("called `my::nested::function()`");
}

#[allow(dead_code)]
fn private_function() {
    println!("called `my::nested::private_function()`");
}
```

In `my/inaccessible.rs`:

```rust

#[allow(dead_code)]
pub fn public_function() {
    println!("called `my::inaccessible::public_function()`");
}
```

Let’s check that things still work as before:

```shell

$ rustc split.rs && ./split
called `my::function()`
called `function()`
called `my::indirect_access()`, that
> called `my::private_function()`
called `my::nested::function()`
```

# Crates

A crate is a compilation unit in Rust. Whenever `rustc some_file.rs` is called,
`some_file.rs` is treated as the _crate file_. If `some_file.rs` has `mod`
declarations in it, then the contents of the module files would be inserted in
places where `mod` declarations in the crate file are found, _before_ running
the compiler over it. In other words, modules do _not_ get compiled
individually, only crates get compiled.

A crate can be compiled into a binary or into a library. By default, `rustc`
will produce a binary from a crate. This behavior can be overridden by passing
the `--crate-type` flag to `lib`.

# Creating a Library

Let’s create a library, and then see how to link it to another crate.

In `rary.rs`:

```rust

pub fn public_function() {
    println!("called rary's `public_function()`");
}

fn private_function() {
    println!("called rary's `private_function()`");
}

pub fn indirect_access() {
    print!("called rary's `indirect_access()`, that\n> ");

    private_function();
}
```

```shell

$ rustc --crate-type=lib rary.rs
$ ls lib*
library.rlib
```

Libraries get prefixed with “lib”, and by default they get named after their
crate file, but this default name can be overridden by passing
the `--crate-name` option to `rustc` or by using the [`crate_name`\\
attribute](https://doc.rust-lang.org/rust-by-example/print.html#crates-1).

# Using a Library

To link a crate to this new library you may use `rustc`’s `--extern` flag. All
of its items will then be imported under a module named the same as the library.
This module generally behaves the same way as any other module.

```rust

// extern crate rary; // May be required for Rust 2015 edition or earlier

fn main() {
    rary::public_function();

    // Error! `private_function` is private
    //rary::private_function();

    rary::indirect_access();
}
```

```txt

# Where library.rlib is the path to the compiled library, assumed that it's
# in the same directory here:
$ rustc executable.rs --extern rary=library.rlib && ./executable
called rary's `public_function()`
called rary's `indirect_access()`, that
> called rary's `private_function()`
```

# Cargo

`cargo` is the official Rust package management tool. It has lots of really
useful features to improve code quality and developer velocity! These include

- Dependency management and integration with [crates.io](https://crates.io/) (the
official Rust package registry)
- Awareness of unit tests
- Awareness of benchmarks

This chapter will go through some quick basics, but you can find the
comprehensive docs in [The Cargo Book](https://doc.rust-lang.org/cargo/).

# Dependencies

Most programs have dependencies on some libraries. If you have ever managed
dependencies by hand, you know how much of a pain this can be. Luckily, the Rust
ecosystem comes standard with `cargo`! `cargo` can manage dependencies for a
project.

To create a new Rust project,

```sh

# A binary
cargo new foo

# A library
cargo new --lib bar
```

For the rest of this chapter, let’s assume we are making a binary, rather than
a library, but all of the concepts are the same.

After the above commands, you should see a file hierarchy like this:

```txt

.
├── bar
│   ├── Cargo.toml
│   └── src
│       └── lib.rs
└── foo
    ├── Cargo.toml
    └── src
        └── main.rs
```

The `main.rs` is the root source file for your new `foo` project – nothing new there.
The `Cargo.toml` is the config file for `cargo` for this project. If you
look inside it, you should see something like this:

```toml

[package]
name = "foo"
version = "0.1.0"
authors = ["mark"]

[dependencies]
```

The `name` field under `[package]` determines the name of the project. This is
used by `crates.io` if you publish the crate (more later). It is also the name
of the output binary when you compile.

The `version` field is a crate version number using [Semantic\\
Versioning](http://semver.org/).

The `authors` field is a list of authors used when publishing the crate.

The `[dependencies]` section lets you add dependencies for your project.

For example, suppose that we want our program to have a great CLI. You can find
lots of great packages on [crates.io](https://crates.io/) (the official Rust
package registry). One popular choice is [clap](https://crates.io/crates/clap).
As of this writing, the most recent published version of `clap` is `2.27.1`. To
add a dependency to our program, we can simply add the following to our
`Cargo.toml` under `[dependencies]`: `clap = "2.27.1"`. And that’s it! You can start using
`clap` in your program.

`cargo` also supports [other types of dependencies](https://doc.rust-lang.org/cargo/reference/specifying-dependencies.html). Here is just
a small sampling:

```toml

[package]
name = "foo"
version = "0.1.0"
authors = ["mark"]

[dependencies]
clap = "2.27.1" # from crates.io
rand = { git = "https://github.com/rust-lang-nursery/rand" } # from online repo
bar = { path = "../bar" } # from a path in the local filesystem
```

`cargo` is more than a dependency manager. All of the available
configuration options are listed in the [format specification](https://doc.rust-lang.org/cargo/reference/manifest.html) of
`Cargo.toml`.

To build our project we can execute `cargo build` anywhere in the project
directory (including subdirectories!). We can also do `cargo run` to build and
run. Notice that these commands will resolve all dependencies, download crates
if needed, and build everything, including your crate. (Note that it only
rebuilds what it has not already built, similar to `make`).

Voila! That’s all there is to it!

# Conventions

In the previous chapter, we saw the following directory hierarchy:

```txt

foo
├── Cargo.toml
└── src
    └── main.rs
```

Suppose that we wanted to have two binaries in the same project, though. What
then?

It turns out that `cargo` supports this. The default binary name is `main`, as
we saw before, but you can add additional binaries by placing them in a `bin/`
directory:

```txt

foo
├── Cargo.toml
└── src
    ├── main.rs
    └── bin
        └── my_other_bin.rs
```

To tell `cargo` to only compile or run this binary, we just pass `cargo` the
`--bin my_other_bin` flag, where `my_other_bin` is the name of the binary we
want to work with.

In addition to extra binaries, `cargo` supports [more features](https://doc.rust-lang.org/cargo/guide/project-layout.html) such as
benchmarks, tests, and examples.

In the next chapter, we will look more closely at tests.

# Testing

As we know testing is integral to any piece of software! Rust has first-class
support for unit and integration testing ( [see this\\
chapter](https://doc.rust-lang.org/book/ch11-00-testing.html) in TRPL).

From the testing chapters linked above, we see how to write unit tests and
integration tests. Organizationally, we can place unit tests in the modules they
test and integration tests in their own `tests/` directory:

```txt

foo
├── Cargo.toml
├── src
│   └── main.rs
│   └── lib.rs
└── tests
    ├── my_test.rs
    └── my_other_test.rs
```

Each file in `tests` is a separate
[integration test](https://doc.rust-lang.org/book/ch11-03-test-organization.html#integration-tests),
i.e. a test that is meant to test your library as if it were being called from a dependent
crate.

The [Testing](https://doc.rust-lang.org/rust-by-example/print.html#testing-1) chapter elaborates on the three different testing styles:
[Unit](https://doc.rust-lang.org/rust-by-example/print.html#unit-testing), [Doc](https://doc.rust-lang.org/rust-by-example/print.html#documentation-testing), and [Integration](https://doc.rust-lang.org/rust-by-example/print.html#integration-testing).

`cargo` naturally provides an easy way to run all of your tests!

```shell

$ cargo test
```

You should see output like this:

```shell

$ cargo test
   Compiling blah v0.1.0 (file:///nobackup/blah)
    Finished dev [unoptimized + debuginfo] target(s) in 0.89 secs
     Running target/debug/deps/blah-d3b32b97275ec472

running 4 tests
test test_bar ... ok
test test_baz ... ok
test test_foo_bar ... ok
test test_foo ... ok

test result: ok. 4 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```

You can also run tests whose name matches a pattern:

```shell

$ cargo test test_foo
```

```shell

$ cargo test test_foo
   Compiling blah v0.1.0 (file:///nobackup/blah)
    Finished dev [unoptimized + debuginfo] target(s) in 0.35 secs
     Running target/debug/deps/blah-d3b32b97275ec472

running 2 tests
test test_foo ... ok
test test_foo_bar ... ok

test result: ok. 2 passed; 0 failed; 0 ignored; 0 measured; 2 filtered out
```

One word of caution: Cargo may run multiple tests concurrently, so make sure
that they don’t race with each other.

One example of this concurrency causing issues is if two tests output to a
file, such as below:

```rust

#![allow(unused)]
fn main() {
#[cfg(test)]
mod tests {
    // Import the necessary modules
    use std::fs::OpenOptions;
    use std::io::Write;

    // This test writes to a file
    #[test]
    fn test_file() {
        // Opens the file ferris.txt or creates one if it doesn't exist.
        let mut file = OpenOptions::new()
            .append(true)
            .create(true)
            .open("ferris.txt")
            .expect("Failed to open ferris.txt");

        // Print "Ferris" 5 times.
        for _ in 0..5 {
            file.write_all("Ferris\n".as_bytes())
                .expect("Could not write to ferris.txt");
        }
    }

    // This test tries to write to the same file
    #[test]
    fn test_file_also() {
        // Opens the file ferris.txt or creates one if it doesn't exist.
        let mut file = OpenOptions::new()
            .append(true)
            .create(true)
            .open("ferris.txt")
            .expect("Failed to open ferris.txt");

        // Print "Corro" 5 times.
        for _ in 0..5 {
            file.write_all("Corro\n".as_bytes())
                .expect("Could not write to ferris.txt");
        }
    }
}
}
```

Although the intent is to get the following:

```shell

$ cat ferris.txt
Ferris
Ferris
Ferris
Ferris
Ferris
Corro
Corro
Corro
Corro
Corro
```

What actually gets put into `ferris.txt` is this:

```shell

$ cargo test test_file && cat ferris.txt
Corro
Ferris
Corro
Ferris
Corro
Ferris
Corro
Ferris
Corro
Ferris
```

# Build Scripts

Sometimes a normal build from `cargo` is not enough. Perhaps your crate needs
some pre-requisites before `cargo` will successfully compile, things like code
generation, or some native code that needs to be compiled. To solve this problem
we have build scripts that Cargo can run.

To add a build script to your package it can either be specified in the
`Cargo.toml` as follows:

```toml

[package]
...
build = "build.rs"
```

Otherwise Cargo will look for a `build.rs` file in the project directory by
default.

## How to use a build script

The build script is simply another Rust file that will be compiled and invoked
prior to compiling anything else in the package. Hence it can be used to fulfill
pre-requisites of your crate.

Cargo provides the script with inputs via environment variables [specified\\
here](https://doc.rust-lang.org/cargo/reference/environment-variables.html#environment-variables-cargo-sets-for-build-scripts) that can be used.

The script provides output via stdout. All lines printed are written to
`target/debug/build/<pkg>/output`. Further, lines prefixed with `cargo:` will be
interpreted by Cargo directly and hence can be used to define parameters for the
package’s compilation.

For further specification and examples have a read of the
[Cargo specification](https://doc.rust-lang.org/cargo/reference/build-scripts.html).

# Attributes

An attribute is metadata applied to some module, crate or item. This metadata
can be used to/for:

- [conditional compilation of code](https://doc.rust-lang.org/rust-by-example/print.html#cfg)
- [set crate name, version and type (binary or library)](https://doc.rust-lang.org/rust-by-example/print.html#crates-1)
- disable [lints](https://en.wikipedia.org/wiki/Lint_%28software%29) (warnings)
- enable compiler features (macros, glob imports, etc.)
- link to a foreign library
- mark functions as unit tests
- mark functions that will be part of a benchmark
- [attribute like macros](https://doc.rust-lang.org/book/ch19-06-macros.html#attribute-like-macros)

Attributes look like `#[outer_attribute]` or `#![inner_attribute]`,
with the difference between them being where they apply.

- `#[outer_attribute]` applies to the [item](https://doc.rust-lang.org/stable/reference/items.html) immediately
following it. Some examples of items are: a function, a module
declaration, a constant, a structure, an enum. Here is an example
where attribute `#[derive(Debug)]` applies to the struct
`Rectangle`:


```rust

#![allow(unused)]
fn main() {
#[derive(Debug)]
struct Rectangle {
      width: u32,
      height: u32,
}
}
```

- `#![inner_attribute]` applies to the enclosing [item](https://doc.rust-lang.org/stable/reference/items.html) (typically a
module or a crate). In other words, this attribute is interpreted as
applying to the entire scope in which it’s placed. Here is an example
where `#![allow(unused_variables)]` applies to the whole crate (if
placed in `main.rs`):


```rust

#![allow(unused_variables)]

fn main() {
      let x = 3; // This would normally warn about an unused variable.
}
```


Attributes can take arguments with different syntaxes:

- `#[attribute = "value"]`
- `#[attribute(key = "value")]`
- `#[attribute(value)]`

Attributes can have multiple values and can be separated over multiple lines, too:

```rust

#[attribute(value, value2)]

#[attribute(value, value2, value3,\
            value4, value5)]
```

# `dead_code`

The compiler provides a `dead_code` [_lint_](https://en.wikipedia.org/wiki/Lint_%28software%29) that will warn
about unused functions. An _attribute_ can be used to disable the lint.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Note that in real programs, you should eliminate dead code. In these examples
we’ll allow dead code in some places because of the interactive nature of the
examples.

# Crates

The `crate_type` attribute can be used to tell the compiler whether a crate is
a binary or a library (and even which type of library), and the `crate_name`
attribute can be used to set the name of the crate.

However, it is important to note that both the `crate_type` and `crate_name`
attributes have **no** effect whatsoever when using Cargo, the Rust package
manager. Since Cargo is used for the majority of Rust projects, this means
real-world uses of `crate_type` and `crate_name` are relatively limited.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

When the `crate_type` attribute is used, we no longer need to pass the
`--crate-type` flag to `rustc`.

```shell

$ rustc lib.rs
$ ls lib*
library.rlib
```

# `cfg`

Configuration conditional checks are possible through two different operators:

- the `cfg` attribute: `#[cfg(...)]` in attribute position
- the `cfg!` macro: `cfg!(...)` in boolean expressions

While the former enables conditional compilation, the latter conditionally
evaluates to `true` or `false` literals allowing for checks at run-time. Both
utilize identical argument syntax.

`cfg!`, unlike `#[cfg]`, does not remove any code and only evaluates to true or false. For example, all blocks in an if/else expression need to be valid when `cfg!` is used for the condition, regardless of what `cfg!` is evaluating.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[the reference](https://doc.rust-lang.org/reference/attributes.html#conditional-compilation), [`cfg!`](https://doc.rust-lang.org/std/macro.cfg!.html), and [macros](https://doc.rust-lang.org/rust-by-example/print.html#macro_rules).

# Custom

Some conditionals like `target_os` are implicitly provided by `rustc`, but
custom conditionals must be passed to `rustc` using the `--cfg` flag.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Try to run this to see what happens without the custom `cfg` flag.

With the custom `cfg` flag:

```shell

$ rustc --cfg some_condition custom.rs && ./custom
condition met!
```

# Generics

_Generics_ is the topic of generalizing types and functionalities to broader
cases. This is extremely useful for reducing code duplication in many ways,
but can call for rather involved syntax. Namely, being generic requires
taking great care to specify over which types a generic type
is actually considered valid. The simplest and most common use of generics
is for type parameters.

A type parameter is specified as generic by the use of angle brackets and upper
[camel case](https://en.wikipedia.org/wiki/CamelCase): `<Aaa, Bbb, ...>`. “Generic type parameters” are
typically represented as `<T>`. In Rust, “generic” also describes anything that
accepts one or more generic type parameters `<T>`. Any type specified as a
generic type parameter is generic, and everything else is concrete (non-generic).

For example, defining a _generic function_ named `foo` that takes an argument
`T` of any type:

```rust

fn foo<T>(arg: T) { ... }
```

Because `T` has been specified as a generic type parameter using `<T>`, it
is considered generic when used here as `(arg: T)`. This is the case even if `T`
has previously been defined as a `struct`.

This example shows some of the syntax in action:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[`structs`](https://doc.rust-lang.org/rust-by-example/print.html#structures)

# Functions

The same set of rules can be applied to functions: a type `T` becomes
generic when preceded by `<T>`.

Using generic functions sometimes requires explicitly specifying type
parameters. This may be the case if the function is called where the return type
is generic, or if the compiler doesn’t have enough information to infer
the necessary type parameters.

A function call with explicitly specified type parameters looks like:
`fun::<A, B, ...>()`.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[functions](https://doc.rust-lang.org/rust-by-example/print.html#functions) and [`struct`s](https://doc.rust-lang.org/rust-by-example/print.html#structures)

# Implementation

Similar to functions, implementations require care to remain generic.

```rust

#![allow(unused)]
fn main() {
struct S; // Concrete type `S`
struct GenericVal<T>(T); // Generic type `GenericVal`

// impl of GenericVal where we explicitly specify type parameters:
impl GenericVal<f32> {} // Specify `f32`
impl GenericVal<S> {} // Specify `S` as defined above

// `<T>` Must precede the type to remain generic
impl<T> GenericVal<T> {}
}
```

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[functions returning references](https://doc.rust-lang.org/rust-by-example/print.html#functions-2), [`impl`](https://doc.rust-lang.org/rust-by-example/print.html#associated-functions--methods), and [`struct`](https://doc.rust-lang.org/rust-by-example/print.html#structures)

# Traits

Of course `trait`s can also be generic. Here we define one which reimplements
the `Drop``trait` as a generic method to `drop` itself and an input.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[`Drop`](https://doc.rust-lang.org/std/ops/trait.Drop.html), [`struct`](https://doc.rust-lang.org/rust-by-example/print.html#structures), and [`trait`](https://doc.rust-lang.org/rust-by-example/print.html#traits-2)

# Bounds

When working with generics, the type parameters often must use traits as _bounds_ to
stipulate what functionality a type implements. For example, the following
example uses the trait `Display` to print and so it requires `T` to be bound
by `Display`; that is, `T` _must_ implement `Display`.

```rust

// Define a function `printer` that takes a generic type `T` which
// must implement trait `Display`.
fn printer<T: Display>(t: T) {
    println!("{}", t);
}
```

Bounding restricts the generic to types that conform to the bounds. That is:

```rust

struct S<T: Display>(T);

// Error! `Vec<T>` does not implement `Display`. This
// specialization will fail.
let s = S(vec![1]);
```

Another effect of bounding is that generic instances are allowed to access the
[methods](https://doc.rust-lang.org/rust-by-example/print.html#associated-functions--methods) of traits specified in the bounds. For example:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

As an additional note, [`where`](https://doc.rust-lang.org/rust-by-example/print.html#where-clauses) clauses can also be used to apply bounds in
some cases to be more expressive.

### See also:

[`std::fmt`](https://doc.rust-lang.org/rust-by-example/print.html#formatted-print), [`struct`s](https://doc.rust-lang.org/rust-by-example/print.html#structures), and [`trait`s](https://doc.rust-lang.org/rust-by-example/print.html#traits-2)

# Testcase: empty bounds

A consequence of how bounds work is that even if a `trait` doesn’t
include any functionality, you can still use it as a bound. `Eq` and
`Copy` are examples of such `trait`s from the `std` library.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[`std::cmp::Eq`](https://doc.rust-lang.org/std/cmp/trait.Eq.html), [`std::marker::Copy`](https://doc.rust-lang.org/std/marker/trait.Copy.html), and [`trait`s](https://doc.rust-lang.org/rust-by-example/print.html#traits-2)

# Multiple bounds

Multiple bounds for a single type can be applied with a `+`. Like normal, different types are
separated with `,`.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[`std::fmt`](https://doc.rust-lang.org/rust-by-example/print.html#formatted-print) and [`trait`s](https://doc.rust-lang.org/rust-by-example/print.html#traits-2)

# Where clauses

A bound can also be expressed using a `where` clause immediately
before the opening `{`, rather than at the type’s first mention.
Additionally, `where` clauses can apply bounds to arbitrary types,
rather than just to type parameters.

Some cases that a `where` clause is useful:

- When specifying generic types and bounds separately is clearer:

```rust

impl <A: TraitB + TraitC, D: TraitE + TraitF> MyTrait<A, D> for YourType {}

// Expressing bounds with a `where` clause
impl <A, D> MyTrait<A, D> for YourType where
    A: TraitB + TraitC,
    D: TraitE + TraitF {}
```

- When using a `where` clause is more expressive than using normal syntax.
The `impl` in this example cannot be directly expressed without a `where` clause:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[RFC](https://github.com/rust-lang/rfcs/blob/master/text/0135-where.md), [`struct`](https://doc.rust-lang.org/rust-by-example/print.html#structures), and [`trait`](https://doc.rust-lang.org/rust-by-example/print.html#traits-2)

# New Type Idiom

The `newtype` idiom gives compile time guarantees that the right type of value is supplied
to a program.

For example, a function that measures distance in miles, _must_ be given
a value of type `Miles`.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Uncomment the last print statement to observe that the type supplied must be `Miles`.

To obtain the `newtype`’s value as the base type, you may use the tuple or destructuring syntax like so:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[`structs`](https://doc.rust-lang.org/rust-by-example/print.html#structures)

# Associated items

“Associated Items” refers to a set of rules pertaining to [`item`](https://doc.rust-lang.org/reference/items.html) s
of various types. It is an extension to `trait` generics, and allows
`trait`s to internally define new items.

One such item is called an _associated type_, providing simpler usage
patterns when the `trait` is generic over its container type.

### See also:

[RFC](https://github.com/rust-lang/rfcs/blob/master/text/0195-associated-items.md)

# The Problem

A `trait` that is generic over its container type has type specification
requirements - users of the `trait` _must_ specify all of its generic types.

In the example below, the `Contains``trait` allows the use of the generic
types `A` and `B`. The trait is then implemented for the `Container` type,
specifying `i32` for `A` and `B` so that it can be used with `fn difference()`.

Because `Contains` is generic, we are forced to explicitly state _all_ of the
generic types for `fn difference()`. In practice, we want a way to express that
`A` and `B` are determined by the _input_`C`. As you will see in the next
section, associated types provide exactly that capability.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[`struct`s](https://doc.rust-lang.org/rust-by-example/print.html#structures), and [`trait`s](https://doc.rust-lang.org/rust-by-example/print.html#traits-2)

# Associated types

The use of “Associated types” improves the overall readability of code
by moving inner types locally into a trait as _output_ types. Syntax
for the `trait` definition is as follows:

```rust

#![allow(unused)]
fn main() {
// `A` and `B` are defined in the trait via the `type` keyword.
// (Note: `type` in this context is different from `type` when used for
// aliases).
trait Contains {
    type A;
    type B;

    // Updated syntax to refer to these new types generically.
    fn contains(&self, _: &Self::A, _: &Self::B) -> bool;
}
}
```

Note that functions that use the `trait``Contains` are no longer required
to express `A` or `B` at all:

```rust

// Without using associated types
fn difference<A, B, C>(container: &C) -> i32 where
    C: Contains<A, B> { ... }

// Using associated types
fn difference<C: Contains>(container: &C) -> i32 { ... }
```

Let’s rewrite the example from the previous section using associated types:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Phantom type parameters

A phantom type parameter is one that doesn’t show up at runtime,
but is checked statically (and only) at compile time.

Data types can use extra generic type parameters to act as markers
or to perform type checking at compile time. These extra parameters
hold no storage values, and have no runtime behavior.

In the following example, we combine [std::marker::PhantomData](https://doc.rust-lang.org/std/marker/struct.PhantomData.html)
with the phantom type parameter concept to create tuples containing
different data types.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[Derive](https://doc.rust-lang.org/rust-by-example/print.html#derive), [struct](https://doc.rust-lang.org/rust-by-example/print.html#structures), and [tuple](https://doc.rust-lang.org/rust-by-example/print.html#tuples).

# Testcase: unit clarification

A useful method of unit conversions can be examined by implementing `Add`
with a phantom type parameter. The `Add``trait` is examined below:

```rust

// This construction would impose: `Self + RHS = Output`
// where RHS defaults to Self if not specified in the implementation.
pub trait Add<RHS = Self> {
    type Output;

    fn add(self, rhs: RHS) -> Self::Output;
}

// `Output` must be `T<U>` so that `T<U> + T<U> = T<U>`.
impl<U> Add for T<U> {
    type Output = T<U>;
    ...
}
```

The whole implementation:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[Borrowing (`&`)](https://doc.rust-lang.org/rust-by-example/print.html#borrowing), [Bounds (`X: Y`)](https://doc.rust-lang.org/rust-by-example/print.html#bounds), [enum](https://doc.rust-lang.org/rust-by-example/print.html#enums), [impl & self](https://doc.rust-lang.org/rust-by-example/print.html#associated-functions--methods),
[Overloading](https://doc.rust-lang.org/rust-by-example/print.html#operator-overloading), [ref](https://doc.rust-lang.org/rust-by-example/print.html#the-ref-pattern), [Traits (`X for Y`)](https://doc.rust-lang.org/rust-by-example/print.html#traits-2), and [TupleStructs](https://doc.rust-lang.org/rust-by-example/print.html#structures).

# Scoping rules

Scopes play an important part in ownership, borrowing, and lifetimes.
That is, they indicate to the compiler when borrows are valid, when
resources can be freed, and when variables are created or destroyed.

# RAII

Variables in Rust do more than just hold data in the stack: they also _own_
resources, e.g. `Box<T>` owns memory in the heap. Rust enforces [RAII](https://en.wikipedia.org/wiki/Resource_Acquisition_Is_Initialization)
(Resource Acquisition Is Initialization), so whenever an object goes out of
scope, its destructor is called and its owned resources are freed.

This behavior shields against _resource leak_ bugs, so you’ll never have to
manually free memory or worry about memory leaks again! Here’s a quick showcase:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Of course, we can double check for memory errors using [`valgrind`](http://valgrind.org/info/):

```shell

$ rustc raii.rs && valgrind ./raii
==26873== Memcheck, a memory error detector
==26873== Copyright (C) 2002-2013, and GNU GPL'd, by Julian Seward et al.
==26873== Using Valgrind-3.9.0 and LibVEX; rerun with -h for copyright info
==26873== Command: ./raii
==26873==
==26873==
==26873== HEAP SUMMARY:
==26873==     in use at exit: 0 bytes in 0 blocks
==26873==   total heap usage: 1,013 allocs, 1,013 frees, 8,696 bytes allocated
==26873==
==26873== All heap blocks were freed -- no leaks are possible
==26873==
==26873== For counts of detected and suppressed errors, rerun with: -v
==26873== ERROR SUMMARY: 0 errors from 0 contexts (suppressed: 2 from 2)
```

No leaks here!

## Destructor

The notion of a destructor in Rust is provided through the [`Drop`](https://doc.rust-lang.org/std/ops/trait.Drop.html) trait. The
destructor is called when the resource goes out of scope. This trait is not
required to be implemented for every type, only implement it for your type if
you require its own destructor logic.

Run the below example to see how the [`Drop`](https://doc.rust-lang.org/std/ops/trait.Drop.html) trait works. When the variable in
the `main` function goes out of scope the custom destructor will be invoked.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[Box](https://doc.rust-lang.org/rust-by-example/print.html#box-stack-and-heap)

# Ownership and moves

Because variables are in charge of freeing their own resources,
**resources can only have one owner**. This prevents resources
from being freed more than once. Note that not all variables own
resources (e.g. [references](https://doc.rust-lang.org/rust-by-example/print.html#pointersref)).

When doing assignments (`let x = y`) or passing function arguments by value
(`foo(x)`), the _ownership_ of the resources is transferred. In Rust-speak,
this is known as a _move_.

After moving resources, the previous owner can no longer be used. This avoids
creating dangling pointers.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Mutability

Mutability of data can be changed when ownership is transferred.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Partial moves

Within the [destructuring](https://doc.rust-lang.org/rust-by-example/print.html#destructuring) of a single variable, both `by-move` and
`by-reference` pattern bindings can be used at the same time. Doing
this will result in a _partial move_ of the variable, which means
that parts of the variable will be moved while other parts stay. In
such a case, the parent variable cannot be used afterwards as a
whole, however the parts that are only referenced (and not moved)
can still be used. Note that types that implement the
[`Drop` trait](https://doc.rust-lang.org/rust-by-example/print.html#drop) cannot be partially moved from, because
its `drop` method would use it afterwards as a whole.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

(In this example, we store the `age` variable on the heap to
illustrate the partial move: deleting `ref` in the above code would
give an error as the ownership of `person.age` would be moved to the
variable `age`. If `Person.age` were stored on the stack, `ref` would
not be required as the definition of `age` would copy the data from
`person.age` without moving it.)

### See also:

[destructuring](https://doc.rust-lang.org/rust-by-example/print.html#destructuring)

# Borrowing

Most of the time, we’d like to access data without taking ownership over
it. To accomplish this, Rust uses a _borrowing_ mechanism. Instead of
passing objects by value (`T`), objects can be passed by reference (`&T`).

The compiler statically guarantees (via its borrow checker) that references
_always_ point to valid objects. That is, while references to an object
exist, the object cannot be destroyed.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Mutability

Mutable data can be mutably borrowed using `&mut T`. This is called
a _mutable reference_ and gives read/write access to the borrower.
In contrast, `&T` borrows the data via an immutable reference, and
the borrower can read the data but not modify it:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[`static`](https://doc.rust-lang.org/rust-by-example/print.html#static)

# Aliasing

Data can be immutably borrowed any number of times, but while immutably
borrowed, the original data can’t be mutably borrowed. On the other hand, only
_one_ mutable borrow is allowed at a time. The original data can be borrowed
again only _after_ the mutable reference has been used for the last time.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# The ref pattern

When doing pattern matching or destructuring via the `let` binding, the `ref`
keyword can be used to take references to the fields of a struct/tuple. The
example below shows a few instances where this can be useful:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Lifetimes

A _lifetime_ is a construct the compiler (or more specifically, its _borrow_
_checker_) uses to ensure all borrows are valid. Specifically, a variable’s
lifetime begins when it is created and ends when it is destroyed. While
lifetimes and scopes are often referred to together, they are not the same.

Take, for example, the case where we borrow a variable via `&`. The
borrow has a lifetime that is determined by where it is declared. As a result,
the borrow is valid as long as it ends before the lender is destroyed. However,
the scope of the borrow is determined by where the reference is used.

In the following example and in the rest of this section, we will see how
lifetimes relate to scopes, as well as how the two differ.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Note that no names or types are assigned to label lifetimes.
This restricts how lifetimes will be able to be used as we will see.

# Explicit annotation

The borrow checker uses explicit lifetime annotations to determine
how long references should be valid. In cases where lifetimes are not
elided[1](https://doc.rust-lang.org/rust-by-example/print.html#footnote-1), Rust requires explicit annotations to determine what the
lifetime of a reference should be. The syntax for explicitly annotating
a lifetime uses an apostrophe character as follows:

```rust

foo<'a>
// `foo` has a lifetime parameter `'a`
```

Similar to [closures](https://doc.rust-lang.org/rust-by-example/print.html#type-anonymity), using lifetimes requires generics.
Additionally, this lifetime syntax indicates that the lifetime of `foo`
may not exceed that of `'a`. Explicit annotation of a type has the form
`&'a T` where `'a` has already been introduced.

In cases with multiple lifetimes, the syntax is similar:

```rust

foo<'a, 'b>
// `foo` has lifetime parameters `'a` and `'b`
```

In this case, the lifetime of `foo` cannot exceed that of either `'a` _or_`'b`.

See the following example for explicit lifetime annotation in use:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[generics](https://doc.rust-lang.org/rust-by-example/print.html#generics) and [closures](https://doc.rust-lang.org/rust-by-example/print.html#closures)

* * *

1. [elision](https://doc.rust-lang.org/rust-by-example/print.html#elision) implicitly annotates lifetimes and so is different. [↩](https://doc.rust-lang.org/rust-by-example/print.html#fr-1-1)


# Functions

Ignoring [elision](https://doc.rust-lang.org/rust-by-example/print.html#elision), function signatures with lifetimes have a few constraints:

- any reference _must_ have an annotated lifetime.
- any reference being returned _must_ have the same lifetime as an input or
be `static`.

Additionally, note that returning references without input is banned if it
would result in returning references to invalid data. The following example shows
off some valid forms of functions with lifetimes:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[Functions](https://doc.rust-lang.org/rust-by-example/print.html#functions)

# Methods

Methods are annotated similarly to functions:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[methods](https://doc.rust-lang.org/rust-by-example/print.html#associated-functions--methods)

# Structs

Annotation of lifetimes in structures are also similar to functions:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[`struct`s](https://doc.rust-lang.org/rust-by-example/print.html#structures)

# Traits

Annotation of lifetimes in trait methods basically are similar to functions.
Note that `impl` may have annotation of lifetimes too.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[`trait`s](https://doc.rust-lang.org/rust-by-example/print.html#traits-2)

# Bounds

Just like generic types can be bounded, lifetimes (themselves generic)
use bounds as well. The `:` character has a slightly different meaning here,
but `+` is the same. Note how the following read:

1. `T: 'a`: _All_ references in `T` must outlive lifetime `'a`.
2. `T: Trait + 'a`: Type `T` must implement trait `Trait` and _all_ references
in `T` must outlive `'a`.

The example below shows the above syntax in action used after keyword `where`:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[generics](https://doc.rust-lang.org/rust-by-example/print.html#generics), [bounds in generics](https://doc.rust-lang.org/rust-by-example/print.html#bounds), and
[multiple bounds in generics](https://doc.rust-lang.org/rust-by-example/print.html#multiple-bounds)

# Coercion

A longer lifetime can be coerced into a shorter one
so that it works inside a scope it normally wouldn’t work in.
This comes in the form of inferred coercion by the Rust compiler,
and also in the form of declaring a lifetime difference:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Static

Rust has a few reserved lifetime names. One of those is `'static`. You
might encounter it in two situations:

```rust

// A reference with 'static lifetime:
let s: &'static str = "hello world";

// 'static as part of a trait bound:
fn generic<T>(x: T) where T: 'static {}
```

Both are related but subtly different and this is a common source for
confusion when learning Rust. Here are some examples for each situation:

## Reference lifetime

As a reference lifetime `'static` indicates that the data pointed to by
the reference lives for the remaining lifetime of the running program.
It can still be coerced to a shorter lifetime.

There are two common ways to make a variable with `'static` lifetime, and both
are stored in the read-only memory of the binary:

- Make a constant with the `static` declaration.
- Make a `string` literal which has type: `&'static str`.

See the following example for a display of each method:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Since `'static` references only need to be valid for the _remainder_ of
a program’s life, they can be created while the program is executed. Just to
demonstrate, the below example uses
[`Box::leak`](https://doc.rust-lang.org/std/boxed/struct.Box.html#method.leak)
to dynamically create `'static` references. In that case it definitely doesn’t
live for the entire duration, but only from the leaking point onward.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

## Trait bound

As a trait bound, it means the type does not contain any non-static
references. Eg. the receiver can hold on to the type for as long as
they want and it will never become invalid until they drop it.

It’s important to understand this means that any owned data always passes
a `'static` lifetime bound, but a reference to that owned data generally
does not:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

The compiler will tell you:

```ignore

error[E0597]: `i` does not live long enough
  --> src/lib.rs:15:15
   |
15 |     print_it(&i);
   |     ---------^^--
   |     |         |
   |     |         borrowed value does not live long enough
   |     argument requires that `i` is borrowed for `'static`
16 | }
   | - `i` dropped here while still borrowed
```

### See also:

[`'static` constants](https://doc.rust-lang.org/rust-by-example/print.html#constants)

# Elision

Some lifetime patterns are overwhelmingly common and so the borrow checker
will allow you to omit them to save typing and to improve readability.
This is known as elision. Elision exists in Rust solely because these patterns
are common.

The following code shows a few examples of elision. For a more comprehensive
description of elision, see [lifetime elision](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html#lifetime-elision) in the book.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[elision](https://doc.rust-lang.org/book/ch10-03-lifetime-syntax.html#lifetime-elision)

# Traits

A `trait` is a collection of methods defined for an unknown type:
`Self`. They can access other methods declared in the same trait.

Traits can be implemented for any data type. In the example below,
we define `Animal`, a group of methods. The `Animal``trait` is
then implemented for the `Sheep` data type, allowing the use of
methods from `Animal` with a `Sheep`.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Derive

The compiler is capable of providing basic implementations for some traits via
the `#[derive]` [attribute](https://doc.rust-lang.org/rust-by-example/print.html#attributes). These traits can still be
manually implemented if a more complex behavior is required.

The following is a list of derivable traits:

- Comparison traits:
[`Eq`](https://doc.rust-lang.org/std/cmp/trait.Eq.html), [`PartialEq`](https://doc.rust-lang.org/std/cmp/trait.PartialEq.html), [`Ord`](https://doc.rust-lang.org/std/cmp/trait.Ord.html), [`PartialOrd`](https://doc.rust-lang.org/std/cmp/trait.PartialOrd.html).
- [`Clone`](https://doc.rust-lang.org/std/clone/trait.Clone.html), to create `T` from `&T` via a copy.
- [`Copy`](https://doc.rust-lang.org/core/marker/trait.Copy.html), to give a type ‘copy semantics’ instead of ‘move semantics’.
- [`Hash`](https://doc.rust-lang.org/std/hash/trait.Hash.html), to compute a hash from `&T`.
- [`Default`](https://doc.rust-lang.org/std/default/trait.Default.html), to create an empty instance of a data type.
- [`Debug`](https://doc.rust-lang.org/std/fmt/trait.Debug.html), to format a value using the `{:?}` formatter.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[`derive`](https://doc.rust-lang.org/reference/attributes.html#derive)

# Returning Traits with `dyn`

The Rust compiler needs to know how much space every function’s return type requires. This means all
your functions have to return a concrete type. Unlike other languages, if you have a trait like
`Animal`, you can’t write a function that returns `Animal`, because its different implementations
will need different amounts of memory.

However, there’s an easy workaround. Instead of returning a trait object directly, our functions
return a `Box` which _contains_ some `Animal`. A `box` is just a reference to some memory in the
heap. Because a reference has a statically-known size, and the compiler can guarantee it points to a
heap-allocated `Animal`, we can return a trait from our function!

Rust tries to be as explicit as possible whenever it allocates memory on the heap. So if your
function returns a pointer-to-trait-on-heap in this way, you need to write the return type with the
`dyn` keyword, e.g. `Box<dyn Animal>`.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Operator Overloading

In Rust, many of the operators can be overloaded via traits. That is, some operators can
be used to accomplish different tasks based on their input arguments. This is possible
because operators are syntactic sugar for method calls. For example, the `+` operator in
`a + b` calls the `add` method (as in `a.add(b)`). This `add` method is part of the `Add`
trait. Hence, the `+` operator can be used by any implementor of the `Add` trait.

A list of the traits, such as `Add`, that overload operators can be found in [`core::ops`](https://doc.rust-lang.org/core/ops/).

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See Also

[Add](https://doc.rust-lang.org/core/ops/trait.Add.html), [Syntax Index](https://doc.rust-lang.org/book/appendix-02-operators.html)

# Drop

The [`Drop`](https://doc.rust-lang.org/std/ops/trait.Drop.html) trait only has one method: `drop`, which is called automatically
when an object goes out of scope. The main use of the `Drop` trait is to free the
resources that the implementor instance owns.

`Box`, `Vec`, `String`, `File`, and `Process` are some examples of types that
implement the `Drop` trait to free resources. The `Drop` trait can also be
manually implemented for any custom data type.

The following example adds a print to console to the `drop` function to announce
when it is called.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

For a more practical example, here’s how the `Drop` trait can be used to automatically
clean up temporary files when they’re no longer needed:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Iterators

The [`Iterator`](https://doc.rust-lang.org/core/iter/trait.Iterator.html) trait is used to implement iterators over collections
such as arrays.

The trait requires only a method to be defined for the `next` element,
which may be manually defined in an `impl` block or automatically
defined (as in arrays and ranges).

As a point of convenience for common situations, the `for` construct
turns some collections into iterators using the [`.into_iter()`](https://doc.rust-lang.org/std/iter/trait.IntoIterator.html) method.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# `impl Trait`

`impl Trait` can be used in two locations:

1. as an argument type
2. as a return type

## As an argument type

If your function is generic over a trait but you don’t mind the specific type, you can simplify the function declaration using `impl Trait` as the type of the argument.

For example, consider the following code:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

`parse_csv_document` is generic, allowing it to take any type which implements BufRead, such as `BufReader<File>` or `[u8]`,
but it’s not important what type `R` is, and `R` is only used to declare the type of `src`, so the function can also be written as:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Note that using `impl Trait` as an argument type means that you cannot explicitly state what form of the function you use, i.e. `parse_csv_document::<std::io::Empty>(std::io::empty())` will not work with the second example.

## As a return type

If your function returns a type that implements `MyTrait`, you can write its
return type as `-> impl MyTrait`. This can help simplify your type signatures quite a lot!

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

More importantly, some Rust types can’t be written out. For example, every
closure has its own unnamed concrete type. Before `impl Trait` syntax, you had
to allocate on the heap in order to return a closure. But now you can do it all
statically, like this:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

You can also use `impl Trait` to return an iterator that uses `map` or `filter`
closures! This makes using `map` and `filter` easier. Because closure types don’t
have names, you can’t write out an explicit return type if your function returns
iterators with closures. But with `impl Trait` you can do this easily:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Clone and Copy

When dealing with resources, the default behavior is to transfer them during
assignments or function calls. However, sometimes we need to make a
copy of the resource as well.

The [`Clone`](https://doc.rust-lang.org/std/clone/trait.Clone.html) trait helps us do exactly this. Most commonly, we can
use the `.clone()` method defined by the `Clone` trait.

## Copy: Implicit Cloning

The [`Copy`](https://doc.rust-lang.org/std/marker/trait.Copy.html) trait allows a type to be duplicated simply by copying bits,
with no additional logic required. When a type implements `Copy`, assignments
and function calls will implicitly copy the value instead of moving it.

**Important:**`Copy` requires `Clone` \- any type that implements `Copy` must
also implement `Clone`. This is because `Copy` is defined as a subtrait:
`trait Copy: Clone {}`. The `Clone` implementation for `Copy` types simply
copies the bits.

Not all types can implement `Copy`. A type can only be `Copy` if:

- All of its components are `Copy`
- It doesn’t manage external resources (like heap memory, file handles, etc.)

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Supertraits

Rust doesn’t have “inheritance”, but you can define a trait as being a superset
of another trait. For example:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[The Rust Programming Language chapter on supertraits](https://doc.rust-lang.org/book/ch19-03-advanced-traits.html#using-supertraits-to-require-one-traits-functionality-within-another-trait)

# Disambiguating overlapping traits

A type can implement many different traits. What if two traits both require
the same name for a function? For example, many traits might have a method
named `get()`. They might even have different return types!

Good news: because each trait implementation gets its own `impl` block, it’s
clear which trait’s `get` method you’re implementing.

What about when it comes time to _call_ those methods? To disambiguate between
them, we have to use Fully Qualified Syntax.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[The Rust Programming Language chapter on Fully Qualified syntax](https://doc.rust-lang.org/book/ch19-03-advanced-traits.html#fully-qualified-syntax-for-disambiguation-calling-methods-with-the-same-name)

# `macro_rules!`

Rust provides a powerful macro system that allows metaprogramming. As you’ve
seen in previous chapters, macros look like functions, except that their name
ends with a bang `!`, but instead of generating a function call, macros are
expanded into source code that gets compiled with the rest of the program.
However, unlike macros in C and other languages, Rust macros are expanded into
abstract syntax trees, rather than string preprocessing, so you don’t get
unexpected precedence bugs.

Macros are created using the `macro_rules!` macro.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

So why are macros useful?

1. Don’t repeat yourself. There are many cases where you may need similar
functionality in multiple places but with different types. Often, writing a
macro is a useful way to avoid repeating code. (More on this later)

2. Domain-specific languages. Macros allow you to define special syntax for a
specific purpose. (More on this later)

3. Variadic interfaces. Sometimes you want to define an interface that takes a
variable number of arguments. An example is `println!` which could take any
number of arguments, depending on the format string. (More on this later)


# Syntax

In following subsections, we will show how to define macros in Rust.
There are three basic ideas:

- [Patterns and Designators](https://doc.rust-lang.org/rust-by-example/print.html#designators)
- [Overloading](https://doc.rust-lang.org/rust-by-example/print.html#overload)
- [Repetition](https://doc.rust-lang.org/rust-by-example/print.html#repeat)

# Designators

The arguments of a macro are prefixed by a dollar sign `$` and type annotated
with a _designator_:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

These are some of the available designators:

- `block`
- `expr` is used for expressions
- `ident` is used for variable/function names
- `item`
- `literal` is used for literal constants
- `pat` ( _pattern_)
- `path`
- `stmt` ( _statement_)
- `tt` ( _token tree_)
- `ty` ( _type_)
- `vis` ( _visibility qualifier_)

For a complete list, see the [Rust Reference](https://doc.rust-lang.org/reference/macros-by-example.html).

# Overload

Macros can be overloaded to accept different combinations of arguments.
In that regard, `macro_rules!` can work similarly to a match block:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Repeat

Macros can use `+` in the argument list to indicate that an argument may
repeat at least once, or `*`, to indicate that the argument may repeat zero or
more times.

In the following example, surrounding the matcher with `$(...),+` will
match one or more expression, separated by commas.
Also note that the semicolon is optional on the last case.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# DRY (Don’t Repeat Yourself)

Macros allow writing DRY code by factoring out the common parts of functions
and/or test suites. Here is an example that implements and tests the `+=`, `*=`
and `-=` operators on `Vec<T>`:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

```shell

$ rustc --test dry.rs && ./dry
running 3 tests
test test::mul_assign ... ok
test test::add_assign ... ok
test test::sub_assign ... ok

test result: ok. 3 passed; 0 failed; 0 ignored; 0 measured
```

# Domain Specific Languages (DSLs)

A DSL is a mini “language” embedded in a Rust macro. It is completely valid
Rust because the macro system expands into normal Rust constructs, but it looks
like a small language. This allows you to define concise or intuitive syntax for
some special functionality (within bounds).

Suppose that I want to define a little calculator API. I would like to supply
an expression and have the output printed to console.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Output:

```txt

1 + 2 = 3
(1 + 2) * (3 / 4) = 0
```

This was a very simple example, but much more complex interfaces have been
developed, such as [`lazy_static`](https://crates.io/crates/lazy_static) or
[`clap`](https://crates.io/crates/clap).

Also, note the two pairs of braces in the macro. The outer ones are
part of the syntax of `macro_rules!`, in addition to `()` or `[]`.

# Variadic Interfaces

A _variadic_ interface takes an arbitrary number of arguments. For example,
`println!` can take an arbitrary number of arguments, as determined by the
format string.

We can extend our `calculate!` macro from the previous section to be variadic:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Output:

```txt

1 + 2 = 3
3 + 4 = 7
(2 * 3) + 1 = 7
```

# Error handling

Error handling is the process of handling the possibility of failure. For
example, failing to read a file and then continuing to use that _bad_ input
would clearly be problematic. Noticing and explicitly managing those errors
saves the rest of the program from various pitfalls.

There are various ways to deal with errors in Rust, which are described in the
following subchapters. They all have more or less subtle differences and different
use cases. As a rule of thumb:

An explicit `panic` is mainly useful for tests and dealing with unrecoverable errors.
For prototyping it can be useful, for example when dealing with functions that
haven’t been implemented yet, but in those cases the more descriptive `unimplemented`
is better. In tests `panic` is a reasonable way to explicitly fail.

The `Option` type is for when a value is optional or when the lack of a value is
not an error condition. For example the parent of a directory - `/` and `C:` don’t
have one. When dealing with `Option`s, `unwrap` is fine for prototyping and cases
where it’s absolutely certain that there is guaranteed to be a value. However `expect`
is more useful since it lets you specify an error message in case something goes
wrong anyway.

When there is a chance that things do go wrong and the caller has to deal with the
problem, use `Result`. You can `unwrap` and `expect` them as well (please don’t
do that unless it’s a test or quick prototype).

For a more rigorous discussion of error handling, refer to the error
handling section in the [official book](https://doc.rust-lang.org/book/ch09-00-error-handling.html).

# `panic`

The simplest error handling mechanism we will see is `panic`. It prints an
error message, starts unwinding the stack, and usually exits the program.
Here, we explicitly call `panic` on our error condition:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

The first call to `drink` works. The second panics and thus the third is never called.

# `abort` and `unwind`

The previous section illustrates the error handling mechanism `panic`. Different code paths can be conditionally compiled based on the panic setting. The current values available are `unwind` and `abort`.

Building on the prior lemonade example, we explicitly use the panic strategy to exercise different lines of code.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Here is another example focusing on rewriting `drink()` and explicitly use the `unwind` keyword.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

The panic strategy can be set from the command line by using `abort` or `unwind`.

```console

rustc  lemonade.rs -C panic=abort
```

# `Option` & `unwrap`

In the last example, we showed that we can induce program failure at will.
We told our program to `panic` if we drink a sugary lemonade.
But what if we expect _some_ drink but don’t receive one?
That case would be just as bad, so it needs to be handled!

We _could_ test this against the null string (`""`) as we do with a lemonade.
Since we’re using Rust, let’s instead have the compiler point out cases
where there’s no drink.

An `enum` called `Option<T>` in the `std` library is used when absence is a
possibility. It manifests itself as one of two “options”:

- `Some(T)`: An element of type `T` was found
- `None`: No element was found

These cases can either be explicitly handled via `match` or implicitly with
`unwrap`. Implicit handling will either return the inner element or `panic`.

Note that it’s possible to manually customize `panic` with [expect](https://doc.rust-lang.org/std/option/enum.Option.html#method.expect),
but `unwrap` otherwise leaves us with a less meaningful output than explicit
handling. In the following example, explicit handling yields a more
controlled result while retaining the option to `panic` if desired.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Unpacking options with `?`

You can unpack `Option`s by using `match` statements, but it’s often easier to
use the `?` operator. If `x` is an `Option`, then evaluating `x?` will return
the underlying value if `x` is `Some`, otherwise it will terminate whatever
function is being executed and return `None`.

```rust

fn next_birthday(current_age: Option<u8>) -> Option<String> {
    // If `current_age` is `None`, this returns `None`.
    // If `current_age` is `Some`, the inner `u8` value + 1
    // gets assigned to `next_age`
    let next_age: u8 = current_age? + 1;
    Some(format!("Next year I will be {}", next_age))
}
```

You can chain many `?`s together to make your code much more readable.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Combinators: `map`

`match` is a valid method for handling `Option`s. However, you may
eventually find heavy usage tedious, especially with operations only valid
with an input. In these cases, [combinators](https://doc.rust-lang.org/reference/glossary.html#combinator) can be used to
manage control flow in a modular fashion.

`Option` has a built in method called `map()`, a combinator for the simple
mapping of `Some -> Some` and `None -> None`. Multiple `map()` calls can be
chained together for even more flexibility.

In the following example, `process()` replaces all functions previous
to it while staying compact.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[closures](https://doc.rust-lang.org/rust-by-example/print.html#closures), [`Option`](https://doc.rust-lang.org/std/option/enum.Option.html), [`Option::map()`](https://doc.rust-lang.org/std/option/enum.Option.html#method.map)

# Combinators: `and_then`

`map()` was described as a chainable way to simplify `match` statements.
However, using `map()` on a function that returns an `Option<T>` results
in the nested `Option<Option<T>>`. Chaining multiple calls together can
then become confusing. That’s where another combinator called `and_then()`,
known in some languages as flatmap, comes in.

`and_then()` calls its function input with the wrapped value and returns the result. If the `Option` is `None`, then it returns `None` instead.

In the following example, `cookable_v3()` results in an `Option<Food>`.
Using `map()` instead of `and_then()` would have given an
`Option<Option<Food>>`, which is an invalid type for `eat()`.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[closures](https://doc.rust-lang.org/rust-by-example/print.html#closures), [`Option`](https://doc.rust-lang.org/std/option/enum.Option.html), [`Option::and_then()`](https://doc.rust-lang.org/std/option/enum.Option.html#method.and_then), and [`Option::flatten()`](https://doc.rust-lang.org/std/option/enum.Option.html#method.flatten)

# Unpacking options and defaults

There is more than one way to unpack an `Option` and fall back on a default if it is `None`. To choose the one that meets our needs, we need to consider the following:

- do we need eager or lazy evaluation?
- do we need to keep the original empty value intact, or modify it in place?

## `or()` is chainable, evaluates eagerly, keeps empty value intact

`or()`is chainable and eagerly evaluates its argument, as is shown in the following example. Note that because `or`’s arguments are evaluated eagerly, the variable passed to `or` is moved.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

## `or_else()` is chainable, evaluates lazily, keeps empty value intact

Another alternative is to use `or_else`, which is also chainable, and evaluates lazily, as is shown in the following example:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

## `get_or_insert()` evaluates eagerly, modifies empty value in place

To make sure that an `Option` contains a value, we can use `get_or_insert` to modify it in place with a fallback value, as is shown in the following example. Note that `get_or_insert` eagerly evaluates its parameter, so variable `apple` is moved:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

## `get_or_insert_with()` evaluates lazily, modifies empty value in place

Instead of explicitly providing a value to fall back on, we can pass a closure to `get_or_insert_with`, as follows:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[`closures`](https://doc.rust-lang.org/book/ch13-01-closures.html), [`get_or_insert`](https://doc.rust-lang.org/core/option/enum.Option.html#method.get_or_insert), [`get_or_insert_with`](https://doc.rust-lang.org/core/option/enum.Option.html#method.get_or_insert_with), [`moved variables`](https://doc.rust-lang.org/book/ch04-02-references-and-borrowing.html), [`or`](https://doc.rust-lang.org/core/option/enum.Option.html#method.or), [`or_else`](https://doc.rust-lang.org/core/option/enum.Option.html#method.or_else)

# `Result`

[`Result`](https://doc.rust-lang.org/std/result/enum.Result.html) is a richer version of the [`Option`](https://doc.rust-lang.org/std/option/enum.Option.html) type that
describes possible _error_ instead of possible _absence_.

That is, `Result<T, E>` could have one of two outcomes:

- `Ok(T)`: An element `T` was found
- `Err(E)`: An error was found with element `E`

By convention, the expected outcome is `Ok` while the unexpected outcome is `Err`.

Like `Option`, `Result` has many methods associated with it. `unwrap()`, for
example, either yields the element `T` or `panic`s. For case handling,
there are many combinators between `Result` and `Option` that overlap.

In working with Rust, you will likely encounter methods that return the
`Result` type, such as the [`parse()`](https://doc.rust-lang.org/std/primitive.str.html#method.parse) method. It might not always
be possible to parse a string into the other type, so `parse()` returns a
`Result` indicating possible failure.

Let’s see what happens when we successfully and unsuccessfully `parse()` a string:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

In the unsuccessful case, `parse()` leaves us with an error for `unwrap()`
to `panic` on. Additionally, the `panic` exits our program and provides an
unpleasant error message.

To improve the quality of our error message, we should be more specific
about the return type and consider explicitly handling the error.

## Using `Result` in `main`

The `Result` type can also be the return type of the `main` function if
specified explicitly. Typically the `main` function will be of the form:

```rust

fn main() {
    println!("Hello World!");
}
```

However `main` is also able to have a return type of `Result`. If an error
occurs within the `main` function it will return an error code and print a debug
representation of the error (using the [`Debug`](https://doc.rust-lang.org/std/fmt/trait.Debug.html) trait). The following example
shows such a scenario and touches on aspects covered in [the following section](https://doc.rust-lang.org/rust-by-example/print.html#early-returns).

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# `map` for `Result`

Panicking in the previous example’s `multiply` does not make for robust code.
Generally, we want to return the error to the caller so it can decide what is
the right way to respond to errors.

We first need to know what kind of error type we are dealing with. To determine
the `Err` type, we look to [`parse()`](https://doc.rust-lang.org/std/primitive.str.html#method.parse), which is implemented with the
[`FromStr`](https://doc.rust-lang.org/std/str/trait.FromStr.html) trait for [`i32`](https://doc.rust-lang.org/std/primitive.i32.html). As a result, the `Err` type is
specified as [`ParseIntError`](https://doc.rust-lang.org/std/num/struct.ParseIntError.html).

In the example below, the straightforward `match` statement leads to code
that is overall more cumbersome.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Luckily, `Option`’s `map`, `and_then`, and many other combinators are also
implemented for `Result`. [`Result`](https://doc.rust-lang.org/std/result/enum.Result.html) contains a complete listing.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# aliases for `Result`

How about when we want to reuse a specific `Result` type many times?
Recall that Rust allows us to create [aliases](https://doc.rust-lang.org/rust-by-example/print.html#aliasing). Conveniently,
we can define one for the specific `Result` in question.

At a module level, creating aliases can be particularly helpful. Errors
found in a specific module often have the same `Err` type, so a single alias
can succinctly define _all_ associated `Results`. This is so useful that the
`std` library even supplies one: [`io::Result`](https://doc.rust-lang.org/std/io/type.Result.html)!

Here’s a quick example to show off the syntax:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[`io::Result`](https://doc.rust-lang.org/std/io/type.Result.html)

# Early returns

In the previous example, we explicitly handled the errors using combinators.
Another way to deal with this case analysis is to use a combination of
`match` statements and _early returns_.

That is, we can simply stop executing the function and return the error if
one occurs. For some, this form of code can be easier to both read and
write. Consider this version of the previous example, rewritten using early returns:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

At this point, we’ve learned to explicitly handle errors using combinators
and early returns. While we generally want to avoid panicking, explicitly
handling all of our errors is cumbersome.

In the next section, we’ll introduce `?` for the cases where we simply
need to `unwrap` without possibly inducing `panic`.

# Introducing `?`

Sometimes we just want the simplicity of `unwrap` without the possibility of
a `panic`. Until now, `unwrap` has forced us to nest deeper and deeper when
what we really wanted was to get the variable _out_. This is exactly the purpose of `?`.

Upon finding an `Err`, there are two valid actions to take:

1. `panic!` which we already decided to try to avoid if possible
2. `return` because an `Err` means it cannot be handled

`?` is _almost_ [1](https://doc.rust-lang.org/rust-by-example/print.html#footnote-%E2%80%A0) exactly equivalent to an `unwrap` which `return`s
instead of `panic`king on `Err`s. Let’s see how we can simplify the earlier
example that used combinators:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

## The `try!` macro

Before there was `?`, the same functionality was achieved with the `try!` macro.
The `?` operator is now recommended, but you may still find `try!` when looking
at older code. The same `multiply` function from the previous example
would look like this using `try!`:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

* * *

1. See [re-enter ?](https://doc.rust-lang.org/rust-by-example/print.html#other-uses-of-) for more details. [↩](https://doc.rust-lang.org/rust-by-example/print.html#fr-%E2%80%A0-1)


# Multiple error types

The previous examples have always been very convenient; `Result`s interact
with other `Result`s and `Option`s interact with other `Option`s.

Sometimes an `Option` needs to interact with a `Result`, or a
`Result<T, Error1>` needs to interact with a `Result<T, Error2>`. In those
cases, we want to manage our different error types in a way that makes them
composable and easy to interact with.

In the following code, two instances of `unwrap` generate different error
types. `Vec::first` returns an `Option`, while `parse::<i32>` returns a
`Result<i32, ParseIntError>`:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Over the next sections, we’ll see several strategies for handling these kind of problems.

# Pulling `Result`s out of `Option`s

The most basic way of handling mixed error types is to just embed them in each
other.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

There are times when we’ll want to stop processing on errors (like with
[`?`](https://doc.rust-lang.org/rust-by-example/print.html#introducing-)) but keep going when the `Option` is `None`. The `transpose` function comes in handy to swap the `Result` and `Option`.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Defining an error type

Sometimes it simplifies the code to mask all of the different errors with a
single type of error. We’ll show this with a custom error.

Rust allows us to define our own error types. In general, a “good” error type:

- Represents different errors with the same type
- Presents nice error messages to the user
- Is easy to compare with other types
  - Good: `Err(EmptyVec)`
  - Bad: `Err("Please use a vector with at least one element".to_owned())`
- Can hold information about the error
  - Good: `Err(BadChar(c, position))`
  - Bad: `Err("+ cannot be used here".to_owned())`
- Composes well with other errors

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# `Box`ing errors

A way to write simple code while preserving the original errors is to [`Box`](https://doc.rust-lang.org/std/boxed/struct.Box.html)
them. The drawback is that the underlying error type is only known at runtime and not
[statically determined](https://doc.rust-lang.org/book/ch17-02-trait-objects.html#trait-objects-perform-dynamic-dispatch).

The stdlib helps in boxing our errors by having `Box` implement conversion from
any type that implements the `Error` trait into the trait object `Box<Error>`,
via [`From`](https://doc.rust-lang.org/std/convert/trait.From.html).

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[Dynamic dispatch](https://doc.rust-lang.org/book/ch17-02-trait-objects.html#trait-objects-perform-dynamic-dispatch) and [`Error` trait](https://doc.rust-lang.org/std/error/trait.Error.html)

# Other uses of `?`

Notice in the previous example that our immediate reaction to calling
`parse` is to `map` the error from a library error into a boxed
error:

```rust

.and_then(|s| s.parse::<i32>())
    .map_err(|e| e.into())
```

Since this is a simple and common operation, it would be convenient if it
could be elided. Alas, because `and_then` is not sufficiently flexible, it
cannot. However, we can instead use `?`.

`?` was previously explained as either `unwrap` or `return Err(err)`.
This is only mostly true. It actually means `unwrap` or
`return Err(From::from(err))`. Since `From::from` is a conversion utility
between different types, this means that if you `?` where the error is
convertible to the return type, it will convert automatically.

Here, we rewrite the previous example using `?`. As a result, the
`map_err` will go away when `From::from` is implemented for our error type:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

This is actually fairly clean now. Compared with the original `panic`, it
is very similar to replacing the `unwrap` calls with `?` except that the
return types are `Result`. As a result, they must be destructured at the
top level.

### See also:

[`From::from`](https://doc.rust-lang.org/std/convert/trait.From.html) and [`?`](https://doc.rust-lang.org/reference/expressions/operator-expr.html#the-question-mark-operator)

# Wrapping errors

An alternative to boxing errors is to wrap them in your own error type.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

This adds a bit more boilerplate for handling errors and might not be needed in
all applications. There are some libraries that can take care of the boilerplate
for you.

### See also:

[`From::from`](https://doc.rust-lang.org/std/convert/trait.From.html) and [`Enums`](https://doc.rust-lang.org/rust-by-example/print.html#enums)

[`Crates for handling errors`](https://crates.io/keywords/error-handling)

# Iterating over `Result`s

An `Iter::map` operation might fail, for example:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Let’s step through strategies for handling this.

## Ignore the failed items with `filter_map()`

`filter_map` calls a function and filters out the results that are `None`.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

## Collect the failed items with `map_err()` and `filter_map()`

`map_err` calls a function with the error, so by adding that to the previous
`filter_map` solution we can save them off to the side while iterating.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

## Fail the entire operation with `collect()`

`Result` implements `FromIterator` so that a vector of results (`Vec<Result<T, E>>`)
can be turned into a result with a vector (`Result<Vec<T>, E>`). Once an
`Result::Err` is found, the iteration will terminate.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

This same technique can be used with `Option`.

## Collect all valid values and failures with `partition()`

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

When you look at the results, you’ll note that everything is still wrapped in
`Result`. A little more boilerplate is needed for this.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Std library types

The `std` library provides many custom types which expands drastically on
the `primitives`. Some of these include:

- growable `String`s like: `"hello world"`
- growable vectors: `[1, 2, 3]`
- optional types: `Option<i32>`
- error handling types: `Result<i32, i32>`
- heap allocated pointers: `Box<i32>`

### See also:

[primitives](https://doc.rust-lang.org/rust-by-example/print.html#primitives) and [the std library](https://doc.rust-lang.org/std/)

# Box, stack and heap

All values in Rust are stack allocated by default. Values can be _boxed_
(allocated on the heap) by creating a `Box<T>`. A box is a smart pointer to a
heap allocated value of type `T`. When a box goes out of scope, its destructor
is called, the inner object is destroyed, and the memory on the heap is freed.

Boxed values can be dereferenced using the `*` operator; this removes one layer
of indirection.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Vectors

Vectors are re-sizable arrays. Like slices, their size is not known at compile
time, but they can grow or shrink at any time. A vector is represented using
3 parameters:

- pointer to the data
- length
- capacity

The capacity indicates how much memory is reserved for the vector. The vector
can grow as long as the length is smaller than the capacity. When this threshold
needs to be surpassed, the vector is reallocated with a larger capacity.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

More `Vec` methods can be found under the
[std::vec](https://doc.rust-lang.org/std/vec/) module

# Strings

The two most used string types in Rust are `String` and `&str`.

A `String` is stored as a vector of bytes (`Vec<u8>`), but guaranteed to
always be a valid UTF-8 sequence. `String` is heap allocated, growable and not
null terminated.

`&str` is a slice (`&[u8]`) that always points to a valid UTF-8 sequence, and
can be used to view into a `String`, just like `&[T]` is a view into `Vec<T>`.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

More `str`/`String` methods can be found under the
[std::str](https://doc.rust-lang.org/std/str/) and
[std::string](https://doc.rust-lang.org/std/string/)
modules

## Literals and escapes

There are multiple ways to write string literals with special characters in them.
All result in a similar `&str` so it’s best to use the form that is the most
convenient to write. Similarly there are multiple ways to write byte string literals,
which all result in `&[u8; N]`.

Generally special characters are escaped with a backslash character: `\`.
This way you can add any character to your string, even unprintable ones
and ones that you don’t know how to type. If you want a literal backslash,
escape it with another one: `\\`

String or character literal delimiters occurring within a literal must be escaped: `"\""`, `'\''`.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Sometimes there are just too many characters that need to be escaped or it’s just
much more convenient to write a string out as-is. This is where raw string literals come into play.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Want a string that’s not UTF-8? (Remember, `str` and `String` must be valid UTF-8).
Or maybe you want an array of bytes that’s mostly text? Byte strings to the rescue!

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

For conversions between character encodings check out the [encoding](https://crates.io/crates/encoding) crate.

A more detailed listing of the ways to write string literals and escape characters
is given in the [‘Tokens’ chapter](https://doc.rust-lang.org/reference/tokens.html) of the Rust Reference.

# `Option`

Sometimes it’s desirable to catch the failure of some parts of a program
instead of calling `panic!`; this can be accomplished using the `Option` enum.

The `Option<T>` enum has two variants:

- `None`, to indicate failure or lack of value, and
- `Some(value)`, a tuple struct that wraps a `value` with type `T`.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# `Result`

We’ve seen that the `Option` enum can be used as a return value from functions
that may fail, where `None` can be returned to indicate failure. However,
sometimes it is important to express _why_ an operation failed. To do this we
have the `Result` enum.

The `Result<T, E>` enum has two variants:

- `Ok(value)` which indicates that the operation succeeded, and wraps the
`value` returned by the operation. (`value` has type `T`)
- `Err(why)`, which indicates that the operation failed, and wraps `why`,
which (hopefully) explains the cause of the failure. (`why` has type `E`)

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# `?`

Chaining results using match can get pretty untidy; luckily, the `?` operator
can be used to make things pretty again. `?` is used at the end of an expression
returning a `Result`, and is equivalent to a match expression, where the
`Err(err)` branch expands to an early `return Err(From::from(err))`, and the `Ok(ok)`
branch expands to an `ok` expression.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Be sure to check the [documentation](https://doc.rust-lang.org/std/result/index.html),
as there are many methods to map/compose `Result`.

# `panic!`

The `panic!` macro can be used to generate a panic and start unwinding
its stack. While unwinding, the runtime will take care of freeing all the
resources _owned_ by the thread by calling the destructor of all its objects.

Since we are dealing with programs with only one thread, `panic!` will cause the
program to report the panic message and exit.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Let’s check that `panic!` doesn’t leak memory.

```shell

$ rustc panic.rs && valgrind ./panic
==4401== Memcheck, a memory error detector
==4401== Copyright (C) 2002-2013, and GNU GPL'd, by Julian Seward et al.
==4401== Using Valgrind-3.10.0.SVN and LibVEX; rerun with -h for copyright info
==4401== Command: ./panic
==4401==
thread '<main>' panicked at 'division by zero', panic.rs:5
==4401==
==4401== HEAP SUMMARY:
==4401==     in use at exit: 0 bytes in 0 blocks
==4401==   total heap usage: 18 allocs, 18 frees, 1,648 bytes allocated
==4401==
==4401== All heap blocks were freed -- no leaks are possible
==4401==
==4401== For counts of detected and suppressed errors, rerun with: -v
==4401== ERROR SUMMARY: 0 errors from 0 contexts (suppressed: 0 from 0)
```

# HashMap

Where vectors store values by an integer index, `HashMap`s store values by key.
`HashMap` keys can be booleans, integers, strings,
or any other type that implements the `Eq` and `Hash` traits.
More on this in the next section.

Like vectors, `HashMap`s are growable, but HashMaps can also shrink themselves
when they have excess space.
You can create a HashMap with a certain starting capacity using
`HashMap::with_capacity(uint)`, or use `HashMap::new()` to get a HashMap
with a default initial capacity (recommended).

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

For more information on how hashing and hash maps
(sometimes called hash tables) work, have a look at
[Hash Table Wikipedia](https://en.wikipedia.org/wiki/Hash_table)

# Alternate/custom key types

Any type that implements the `Eq` and `Hash` traits can be a key in `HashMap`.
This includes:

- `bool` (though not very useful since there are only two possible keys)
- `int`, `uint`, and all variations thereof
- `String` and `&str` (protip: you can have a `HashMap` keyed by `String`
and call `.get()` with an `&str`)

Note that `f32` and `f64` do _not_ implement `Hash`,
likely because [floating-point precision errors](https://en.wikipedia.org/wiki/Floating_point#Accuracy_problems)
would make using them as hashmap keys horribly error-prone.

All collection classes implement `Eq` and `Hash`
if their contained type also respectively implements `Eq` and `Hash`.
For example, `Vec<T>` will implement `Hash` if `T` implements `Hash`.

You can easily implement `Eq` and `Hash` for a custom type with just one line:
`#[derive(PartialEq, Eq, Hash)]`

The compiler will do the rest. If you want more control over the details,
you can implement `Eq` and/or `Hash` yourself.
This guide will not cover the specifics of implementing `Hash`.

To play around with using a `struct` in `HashMap`,
let’s try making a very simple user logon system:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# HashSet

Consider a `HashSet` as a `HashMap` where we just care about the keys (
`HashSet<T>` is, in actuality, just a wrapper around `HashMap<T, ()>`).

“What’s the point of that?” you ask. “I could just store the keys in a `Vec`.”

A `HashSet`’s unique feature is that
it is guaranteed to not have duplicate elements.
That’s the contract that any set collection fulfills.
`HashSet` is just one implementation. (see also: [`BTreeSet`](https://doc.rust-lang.org/std/collections/struct.BTreeSet.html))

If you insert a value that is already present in the `HashSet`,
(i.e. the new value is equal to the existing and they both have the same hash),
then the new value will replace the old.

This is great for when you never want more than one of something,
or when you want to know if you’ve already got something.

But sets can do more than that.

Sets have 4 primary operations (all of the following calls return an iterator):

- `union`: get all the unique elements in both sets.

- `difference`: get all the elements that are in the first set but not the second.

- `intersection`: get all the elements that are only in _both_ sets.

- `symmetric_difference`:
get all the elements that are in one set or the other, but _not_ both.


Try all of these in the following example:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

(Examples are adapted from the [documentation.](https://doc.rust-lang.org/std/collections/struct.HashSet.html#method.difference))

# `Rc`

When multiple ownership is needed, `Rc`(Reference Counting) can be used. `Rc`
keeps track of the number of the references which means the number of owners of
the value wrapped inside an `Rc`.

Reference count of an `Rc` increases by 1 whenever an `Rc` is cloned, and
decreases by 1 whenever one cloned `Rc` is dropped out of the scope. When an
`Rc`’s reference count becomes zero (which means there are no remaining owners),
both the `Rc` and the value are all dropped.

Cloning an `Rc` never performs a deep copy. Cloning creates just another pointer
to the wrapped value, and increments the count.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### See also:

[std::rc](https://doc.rust-lang.org/std/rc/index.html) and [std::sync::arc](https://doc.rust-lang.org/std/sync/struct.Arc.html).

# Arc

When shared ownership between threads is needed, `Arc`(Atomically Reference
Counted) can be used. This struct, via the `Clone` implementation can create
a reference pointer for the location of a value in the memory heap while
increasing the reference counter. As it shares ownership between threads, when
the last reference pointer to a value is out of scope, the variable is dropped.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Std misc

Many other types are provided by the std library to support
things such as:

- Threads
- Channels
- File I/O

These expand beyond what the [primitives](https://doc.rust-lang.org/rust-by-example/print.html#primitives) provide.

### See also:

[primitives](https://doc.rust-lang.org/rust-by-example/print.html#primitives) and [the std library](https://doc.rust-lang.org/std/)

# Threads

Rust provides a mechanism for spawning native OS threads via the `spawn`
function, the argument of this function is a moving closure.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

These threads will be scheduled by the OS.

# Testcase: map-reduce

Rust makes it very easy to parallelize data processing, without many of the headaches traditionally associated with such an attempt.

The standard library provides great threading primitives out of the box.
These, combined with Rust’s concept of Ownership and aliasing rules, automatically prevent
data races.

The aliasing rules (one writable reference XOR many readable references) automatically prevent
you from manipulating state that is visible to other threads. (Where synchronization is needed,
there are synchronization
primitives like `Mutex`es or `Channel`s.)

In this example, we will calculate the sum of all digits in a block of numbers.
We will do this by parcelling out chunks of the block into different threads. Each thread will sum
its tiny block of digits, and subsequently we will sum the intermediate sums produced by each
thread.

Note that, although we’re passing references across thread boundaries, Rust understands that we’re
only passing read-only references, and that thus no unsafety or data races can occur. Also because
the references we’re passing have `'static` lifetimes, Rust understands that our data won’t be
destroyed while these threads are still running. (When you need to share non-`static` data between
threads, you can use a smart pointer like `Arc` to keep the data alive and avoid non-`static`
lifetimes.)

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### Assignments

It is not wise to let our number of threads depend on user inputted data.
What if the user decides to insert a lot of spaces? Do we _really_ want to spawn 2,000 threads?
Modify the program so that the data is always chunked into a limited number of chunks,
defined by a static constant at the beginning of the program.

### See also:

- [Threads](https://doc.rust-lang.org/rust-by-example/print.html#threads)
- [vectors](https://doc.rust-lang.org/rust-by-example/print.html#vectors) and [iterators](https://doc.rust-lang.org/rust-by-example/print.html#iterators)
- [closures](https://doc.rust-lang.org/rust-by-example/print.html#closures), [move](https://doc.rust-lang.org/rust-by-example/print.html#ownership-and-moves) semantics and [`move` closures](https://doc.rust-lang.org/book/ch13-01-closures.html#closures-can-capture-their-environment)
- [destructuring](https://doc.rust-lang.org/book/ch18-03-pattern-syntax.html#destructuring-to-break-apart-values) assignments
- [turbofish notation](https://doc.rust-lang.org/book/appendix-02-operators.html?highlight=turbofish) to help type inference
- [unwrap vs. expect](https://doc.rust-lang.org/rust-by-example/print.html#option--unwrap)
- [enumerate](https://doc.rust-lang.org/book/loops.html#enumerate)

# Channels

Rust provides asynchronous `channels` for communication between threads. Channels
allow a unidirectional flow of information between two end-points: the
`Sender` and the `Receiver`.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

# Path

The `Path` type represents file paths in the underlying filesystem. Across all
platforms there is a single `std::path::Path` that abstracts over
platform-specific path semantics and separators. Bring it into scope with
`use std::path::Path;` when needed.

A `Path` can be created from an `OsStr`, and provides several methods to get
information from the file/directory the path points to.

A `Path` is immutable. The owned version of `Path` is `PathBuf`. The relation
between `Path` and `PathBuf` is similar to that of `str` and `String`:
a `PathBuf` can be mutated in-place, and can be dereferenced to a `Path`.

Note that a `Path` is _not_ internally represented as an UTF-8 string, but
instead is stored as an `OsString`. Therefore, converting a `Path` to a `&str`
is _not_ free and may fail (an `Option` is returned). However, a `Path` can be
freely converted to an `OsString` or `&OsStr` using `into_os_string` and
`as_os_str`, respectively.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Be sure to check other `Path` methods and the `Metadata` struct.

### See also:

[OsStr](https://doc.rust-lang.org/std/ffi/struct.OsStr.html) and [Metadata](https://doc.rust-lang.org/std/fs/struct.Metadata.html).

# File I/O

The `File` struct represents a file that has been opened (it wraps a file
descriptor), and gives read and/or write access to the underlying file.

Since many things can go wrong when doing file I/O, all the `File` methods
return the `io::Result<T>` type, which is an alias for `Result<T, io::Error>`.

This makes the failure of all I/O operations _explicit_. Thanks to this, the
programmer can see all the failure paths, and is encouraged to handle them in
a proactive manner.

# `open`

The `open` function can be used to open a file in read-only mode.

A `File` owns a resource, the file descriptor and takes care of closing the
file when it is `drop`ed.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Here’s the expected successful output:

```shell

$ echo "Hello World!" > hello.txt
$ rustc open.rs && ./open
hello.txt contains:
Hello World!
```

(You are encouraged to test the previous example under different failure
conditions: `hello.txt` doesn’t exist, or `hello.txt` is not readable,
etc.)

# `create`

The `create` function opens a file in write-only mode. If the file
already existed, the old content is destroyed. Otherwise, a new file is
created.

```rust

static LOREM_IPSUM: &str =
    "Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
";

use std::fs::File;
use std::io::prelude::*;
use std::path::Path;

fn main() {
    let path = Path::new("lorem_ipsum.txt");
    let display = path.display();

    // Open a file in write-only mode, returns `io::Result<File>`
    let mut file = match File::create(&path) {
        Err(why) => panic!("couldn't create {}: {}", display, why),
        Ok(file) => file,
    };

    // Write the `LOREM_IPSUM` string to `file`, returns `io::Result<()>`
    match file.write_all(LOREM_IPSUM.as_bytes()) {
        Err(why) => panic!("couldn't write to {}: {}", display, why),
        Ok(_) => println!("successfully wrote to {}", display),
    }
}
```

Here’s the expected successful output:

```shell

$ rustc create.rs && ./create
successfully wrote to lorem_ipsum.txt

$ cat lorem_ipsum.txt
Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod
tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam,
quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo
consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse
cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non
proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
```

(As in the previous example, you are encouraged to test this example under
failure conditions.)

The [`OpenOptions`](https://doc.rust-lang.org/std/fs/struct.OpenOptions.html) struct can be used to configure how a file is opened.

# `read_lines`

## A naive approach

This might be a reasonable first attempt for a beginner’s first
implementation for reading lines from a file.

```rust

#![allow(unused)]
fn main() {
use std::fs::read_to_string;

fn read_lines(filename: &str) -> Vec<String> {
    let mut result = Vec::new();

    for line in read_to_string(filename).unwrap().lines() {
        result.push(line.to_string())
    }

    result
}
}
```

Since the method `lines()` returns an iterator over the lines in the file,
we can also perform a map inline and collect the results, yielding a more
concise and fluent expression.

```rust

#![allow(unused)]
fn main() {
use std::fs::read_to_string;

fn read_lines(filename: &str) -> Vec<String> {
    read_to_string(filename)
        .unwrap()  // panic on possible file-reading errors
        .lines()  // split the string into an iterator of string slices
        .map(String::from)  // make each slice into a string
        .collect()  // gather them together into a vector
}
}
```

Note that in both examples above, we must convert the `&str` reference
returned from `lines()` to the owned type `String`, using `.to_string()`
and `String::from` respectively.

## A more efficient approach

Here we pass ownership of the open `File` to a `BufReader` struct. `BufReader` uses an internal
buffer to reduce intermediate allocations.

We also update `read_lines` to return an iterator instead of allocating new
`String` objects in memory for each line.

```rust

use std::fs::File;
use std::io::{self, BufRead};
use std::path::Path;

fn main() {
    // File hosts.txt must exist in the current path
    if let Ok(lines) = read_lines("./hosts.txt") {
        // Consumes the iterator, returns an (Optional) String
        for line in lines.map_while(Result::ok) {
            println!("{}", line);
        }
    }
}

// The output is wrapped in a Result to allow matching on errors.
// Returns an Iterator to the Reader of the lines of the file.
fn read_lines<P>(filename: P) -> io::Result<io::Lines<io::BufReader<File>>>
where P: AsRef<Path>, {
    let file = File::open(filename)?;
    Ok(io::BufReader::new(file).lines())
}
```

Running this program simply prints the lines individually.

```shell

$ echo -e "127.0.0.1\n192.168.0.1\n" > hosts.txt
$ rustc read_lines.rs && ./read_lines
127.0.0.1
192.168.0.1
```

(Note that since `File::open` expects a generic `AsRef<Path>` as argument, we define our
generic `read_lines()` method with the same generic constraint, using the `where` keyword.)

This process is more efficient than creating a `String` in memory with all of the file’s
contents. This can especially cause performance issues when working with larger files.

# Child processes

The `process::Output` struct represents the output of a finished child process,
and the `process::Command` struct is a process builder.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

(You are encouraged to try the previous example with an incorrect flag passed
to `rustc`)

# Pipes

The `std::process::Child` struct represents a child process, and exposes the
`stdin`, `stdout` and `stderr` handles for interaction with the underlying
process via pipes.

```rust

use std::io::prelude::*;
use std::process::{Command, Stdio};

static PANGRAM: &'static str =
"the quick brown fox jumps over the lazy dog\n";

fn main() {
    // Spawn the `wc` command
    let mut cmd = if cfg!(target_family = "windows") {
        let mut cmd = Command::new("powershell");
        cmd.arg("-Command").arg("$input | Measure-Object -Line -Word -Character");
        cmd
    } else {
        Command::new("wc")
    };
    let process = match cmd
                                .stdin(Stdio::piped())
                                .stdout(Stdio::piped())
                                .spawn() {
        Err(why) => panic!("couldn't spawn wc: {}", why),
        Ok(process) => process,
    };

    // Write a string to the `stdin` of `wc`.
    //
    // `stdin` has type `Option<ChildStdin>`, but since we know this instance
    // must have one, we can directly `unwrap` it.
    match process.stdin.unwrap().write_all(PANGRAM.as_bytes()) {
        Err(why) => panic!("couldn't write to wc stdin: {}", why),
        Ok(_) => println!("sent pangram to wc"),
    }

    // Because `stdin` does not live after the above calls, it is `drop`ed,
    // and the pipe is closed.
    //
    // This is very important, otherwise `wc` wouldn't start processing the
    // input we just sent.

    // The `stdout` field also has type `Option<ChildStdout>` so must be unwrapped.
    let mut s = String::new();
    match process.stdout.unwrap().read_to_string(&mut s) {
        Err(why) => panic!("couldn't read wc stdout: {}", why),
        Ok(_) => print!("wc responded with:\n{}", s),
    }
}
```

# Wait

If you’d like to wait for a `process::Child` to finish, you must call
`Child::wait`, which will return a `process::ExitStatus`.

```rust

use std::process::Command;

fn main() {
    let mut child = Command::new("sleep").arg("5").spawn().unwrap();
    let _result = child.wait().unwrap();

    println!("reached end of main");
}
```

```bash

$ rustc wait.rs && ./wait
# `wait` keeps running for 5 seconds until the `sleep 5` command finishes
reached end of main
```

# Filesystem Operations

The `std::fs` module contains several functions that deal with the filesystem.

```rust

use std::fs;
use std::fs::{File, OpenOptions};
use std::io;
use std::io::prelude::*;
#[cfg(target_family = "unix")]
use std::os::unix;
#[cfg(target_family = "windows")]
use std::os::windows;
use std::path::Path;

// A simple implementation of `% cat path`
fn cat(path: &Path) -> io::Result<String> {
    let mut f = File::open(path)?;
    let mut s = String::new();
    match f.read_to_string(&mut s) {
        Ok(_) => Ok(s),
        Err(e) => Err(e),
    }
}

// A simple implementation of `% echo s > path`
fn echo(s: &str, path: &Path) -> io::Result<()> {
    let mut f = File::create(path)?;

    f.write_all(s.as_bytes())
}

// A simple implementation of `% touch path` (ignores existing files)
fn touch(path: &Path) -> io::Result<()> {
    match OpenOptions::new().create(true).write(true).open(path) {
        Ok(_) => Ok(()),
        Err(e) => Err(e),
    }
}

fn main() {
    println!("`mkdir a`");
    // Create a directory, returns `io::Result<()>`
    match fs::create_dir("a") {
        Err(why) => println!("! {:?}", why.kind()),
        Ok(_) => {},
    }

    println!("`echo hello > a/b.txt`");
    // The previous match can be simplified using the `unwrap_or_else` method
    echo("hello", &Path::new("a/b.txt")).unwrap_or_else(|why| {
        println!("! {:?}", why.kind());
    });

    println!("`mkdir -p a/c/d`");
    // Recursively create a directory, returns `io::Result<()>`
    fs::create_dir_all("a/c/d").unwrap_or_else(|why| {
        println!("! {:?}", why.kind());
    });

    println!("`touch a/c/e.txt`");
    touch(&Path::new("a/c/e.txt")).unwrap_or_else(|why| {
        println!("! {:?}", why.kind());
    });

    println!("`ln -s ../b.txt a/c/b.txt`");
    // Create a symbolic link, returns `io::Result<()>`
    #[cfg(target_family = "unix")] {
        unix::fs::symlink("../b.txt", "a/c/b.txt").unwrap_or_else(|why| {
            println!("! {:?}", why.kind());
        });
    }
    #[cfg(target_family = "windows")] {
        windows::fs::symlink_file("../b.txt", "a/c/b.txt").unwrap_or_else(|why| {
            println!("! {:?}", why.to_string());
        });
    }

    println!("`cat a/c/b.txt`");
    match cat(&Path::new("a/c/b.txt")) {
        Err(why) => println!("! {:?}", why.kind()),
        Ok(s) => println!("> {}", s),
    }

    println!("`ls a`");
    // Read the contents of a directory, returns `io::Result<Vec<Path>>`
    match fs::read_dir("a") {
        Err(why) => println!("! {:?}", why.kind()),
        Ok(paths) => for path in paths {
            println!("> {:?}", path.unwrap().path());
        },
    }

    println!("`rm a/c/e.txt`");
    // Remove a file, returns `io::Result<()>`
    fs::remove_file("a/c/e.txt").unwrap_or_else(|why| {
        println!("! {:?}", why.kind());
    });

    println!("`rmdir a/c/d`");
    // Remove an empty directory, returns `io::Result<()>`
    fs::remove_dir("a/c/d").unwrap_or_else(|why| {
        println!("! {:?}", why.kind());
    });
}
```

Here’s the expected successful output:

```shell

$ rustc fs.rs && ./fs
`mkdir a`
`echo hello > a/b.txt`
`mkdir -p a/c/d`
`touch a/c/e.txt`
`ln -s ../b.txt a/c/b.txt`
`cat a/c/b.txt`
> hello
`ls a`
> "a/b.txt"
> "a/c"
`rm a/c/e.txt`
`rmdir a/c/d`
```

And the final state of the `a` directory is:

```shell

$ tree a
a
|-- b.txt
`-- c
    `-- b.txt -> ../b.txt

1 directory, 2 files
```

An alternative way to define the function `cat` is with `?` notation:

```rust

fn cat(path: &Path) -> io::Result<String> {
    let mut f = File::open(path)?;
    let mut s = String::new();
    f.read_to_string(&mut s)?;
    Ok(s)
}
```

### See also:

[`cfg!`](https://doc.rust-lang.org/rust-by-example/print.html#cfg)

# Program arguments

## Standard Library

The command line arguments can be accessed using `std::env::args`, which
returns an iterator that yields a `String` for each argument:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

```shell

$ ./args 1 2 3
My path is ./args.
I got 3 arguments: ["1", "2", "3"].
```

## Crates

Alternatively, there are numerous crates that can provide extra functionality
when creating command-line applications. One of the more popular command line
argument crates being [`clap`](https://rust-cli.github.io/book/tutorial/cli-args.html#parsing-cli-arguments-with-clap).

# Argument parsing

Matching can be used to parse simple arguments:

```rust

use std::env;

fn increase(number: i32) {
    println!("{}", number + 1);
}

fn decrease(number: i32) {
    println!("{}", number - 1);
}

fn help() {
    println!("usage:
match_args <string>
    Check whether given string is the answer.
match_args {{increase|decrease}} <integer>
    Increase or decrease given integer by one.");
}

fn main() {
    let args: Vec<String> = env::args().collect();

    match args.len() {
        // no arguments passed
        1 => {
            println!("My name is 'match_args'. Try passing some arguments!");
        },
        // one argument passed
        2 => {
            match args[1].parse() {
                Ok(42) => println!("This is the answer!"),
                _ => println!("This is not the answer."),
            }
        },
        // one command and one argument passed
        3 => {
            let cmd = &args[1];
            let num = &args[2];
            // parse the number
            let number: i32 = match num.parse() {
                Ok(n) => {
                    n
                },
                Err(_) => {
                    eprintln!("error: second argument not an integer");
                    help();
                    return;
                },
            };
            // parse the command
            match &cmd[..] {
                "increase" => increase(number),
                "decrease" => decrease(number),
                _ => {
                    eprintln!("error: invalid command");
                    help();
                },
            }
        },
        // all the other cases
        _ => {
            // show a help message
            help();
        }
    }
}
```

If you named your program `match_args.rs` and compile it like this `rustc match_args.rs`, you can execute it as follows:

```shell

$ ./match_args Rust
This is not the answer.
$ ./match_args 42
This is the answer!
$ ./match_args do something
error: second argument not an integer
usage:
match_args <string>
    Check whether given string is the answer.
match_args {increase|decrease} <integer>
    Increase or decrease given integer by one.
$ ./match_args do 42
error: invalid command
usage:
match_args <string>
    Check whether given string is the answer.
match_args {increase|decrease} <integer>
    Increase or decrease given integer by one.
$ ./match_args increase 42
43
```

# Foreign Function Interface

Rust provides a Foreign Function Interface (FFI) to C libraries. Foreign
functions must be declared inside an `extern` block annotated with a `#[link]`
attribute containing the name of the foreign library.

```rust

use std::fmt;

// this extern block links to the libm library
#[cfg(target_family = "windows")]
#[link(name = "msvcrt")]
extern {
    // this is a foreign function
    // that computes the square root of a single precision complex number
    fn csqrtf(z: Complex) -> Complex;

    fn ccosf(z: Complex) -> Complex;
}
#[cfg(target_family = "unix")]
#[link(name = "m")]
extern {
    // this is a foreign function
    // that computes the square root of a single precision complex number
    fn csqrtf(z: Complex) -> Complex;

    fn ccosf(z: Complex) -> Complex;
}

// Since calling foreign functions is considered unsafe,
// it's common to write safe wrappers around them.
fn cos(z: Complex) -> Complex {
    unsafe { ccosf(z) }
}

fn main() {
    // z = -1 + 0i
    let z = Complex { re: -1., im: 0. };

    // calling a foreign function is an unsafe operation
    let z_sqrt = unsafe { csqrtf(z) };

    println!("the square root of {:?} is {:?}", z, z_sqrt);

    // calling safe API wrapped around unsafe operation
    println!("cos({:?}) = {:?}", z, cos(z));
}

// Minimal implementation of single precision complex numbers
#[repr(C)]
#[derive(Clone, Copy)]
struct Complex {
    re: f32,
    im: f32,
}

impl fmt::Debug for Complex {
    fn fmt(&self, f: &mut fmt::Formatter) -> fmt::Result {
        if self.im < 0. {
            write!(f, "{}-{}i", self.re, -self.im)
        } else {
            write!(f, "{}+{}i", self.re, self.im)
        }
    }
}
```

# Testing

Rust is a programming language that cares a lot about correctness and it
includes support for writing software tests within the language itself.

Testing comes in three styles:

- [Unit](https://doc.rust-lang.org/rust-by-example/print.html#unit-testing) testing.
- [Doc](https://doc.rust-lang.org/rust-by-example/print.html#documentation-testing) testing.
- [Integration](https://doc.rust-lang.org/rust-by-example/print.html#integration-testing) testing.

Also Rust has support for specifying additional dependencies for tests:

- [Dev-dependencies](https://doc.rust-lang.org/rust-by-example/print.html#development-dependencies)

## See Also

- [The Book](https://doc.rust-lang.org/book/ch11-00-testing.html) chapter on testing
- [API Guidelines](https://rust-lang-nursery.github.io/api-guidelines/documentation.html) on doc-testing

# Unit testing

Tests are Rust functions that verify that the non-test code is functioning in
the expected manner. The bodies of test functions typically perform some setup,
run the code we want to test, then assert whether the results are what we
expect.

Most unit tests go into a `tests` [mod](https://doc.rust-lang.org/rust-by-example/print.html#modules) with the `#[cfg(test)]` [attribute](https://doc.rust-lang.org/rust-by-example/print.html#attributes).
Test functions are marked with the `#[test]` attribute.

Tests fail when something in the test function [panics](https://doc.rust-lang.org/rust-by-example/print.html#panic-1). There are some
helper [macros](https://doc.rust-lang.org/rust-by-example/print.html#macro_rules):

- `assert!(expression)` \- panics if expression evaluates to `false`.
- `assert_eq!(left, right)` and `assert_ne!(left, right)` \- testing left and
right expressions for equality and inequality respectively.

```rust

pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

// This is a really bad adding function, its purpose is to fail in this
// example.
#[allow(dead_code)]
fn bad_add(a: i32, b: i32) -> i32 {
    a - b
}

#[cfg(test)]
mod tests {
    // Note this useful idiom: importing names from outer (for mod tests) scope.
    use super::*;

    #[test]
    fn test_add() {
        assert_eq!(add(1, 2), 3);
    }

    #[test]
    fn test_bad_add() {
        // This assert would fire and test will fail.
        // Please note, that private functions can be tested too!
        assert_eq!(bad_add(1, 2), 3);
    }
}
```

Tests can be run with `cargo test`.

```shell

$ cargo test

running 2 tests
test tests::test_bad_add ... FAILED
test tests::test_add ... ok

failures:

---- tests::test_bad_add stdout ----
        thread 'tests::test_bad_add' panicked at 'assertion failed: `(left == right)`
  left: `-1`,
 right: `3`', src/lib.rs:21:8
note: Run with `RUST_BACKTRACE=1` for a backtrace.

failures:
    tests::test_bad_add

test result: FAILED. 1 passed; 1 failed; 0 ignored; 0 measured; 0 filtered out
```

## Tests and `?`

None of the previous unit test examples had a return type. But in Rust 2018,
your unit tests can return `Result<()>`, which lets you use `?` in them! This
can make them much more concise.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

See [“The Edition Guide”](https://doc.rust-lang.org/edition-guide/rust-2018/error-handling-and-panics/question-mark-in-main-and-tests.html) for more details.

## Testing panics

To check functions that should panic under certain circumstances, use attribute
`#[should_panic]`. This attribute accepts optional parameter `expected =` with
the text of the panic message. If your function can panic in multiple ways, it helps
make sure your test is testing the correct panic.

**Note**: Rust also allows a shorthand form `#[should_panic = "message"]`, which works
exactly like `#[should_panic(expected = "message")]`. Both are valid; the latter is more commonly
used and is considered more explicit.

```rust

pub fn divide_non_zero_result(a: u32, b: u32) -> u32 {
    if b == 0 {
        panic!("Divide-by-zero error");
    } else if a < b {
        panic!("Divide result is zero");
    }
    a / b
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_divide() {
        assert_eq!(divide_non_zero_result(10, 2), 5);
    }

    #[test]
    #[should_panic]
    fn test_any_panic() {
        divide_non_zero_result(1, 0);
    }

    #[test]
    #[should_panic(expected = "Divide result is zero")]
    fn test_specific_panic() {
        divide_non_zero_result(1, 10);
    }

    #[test]
    #[should_panic = "Divide result is zero"] // This also works
    fn test_specific_panic_shorthand() {
        divide_non_zero_result(1, 10);
    }
}
```

Running these tests gives us:

```shell

$ cargo test

running 4 tests
test tests::test_any_panic ... ok
test tests::test_divide ... ok
test tests::test_specific_panic ... ok
test tests::test_specific_panic_shorthand ... ok

test result: ok. 4 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out

   Doc-tests tmp-test-should-panic

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```

## Running specific tests

To run specific tests one may specify the test name to `cargo test` command.

```shell

$ cargo test test_any_panic
running 1 test
test tests::test_any_panic ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 3 filtered out

   Doc-tests tmp-test-should-panic

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```

To run multiple tests one may specify part of a test name that matches all the
tests that should be run.

```shell

$ cargo test panic
running 3 tests
test tests::test_any_panic ... ok
test tests::test_specific_panic ... ok
test tests::test_specific_panic_shorthand ... ok

test result: ok. 3 passed; 0 failed; 0 ignored; 0 measured; 1 filtered out

   Doc-tests tmp-test-should-panic

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```

## Ignoring tests

Tests can be marked with the `#[ignore]` attribute to exclude some tests. Or to run
them with command `cargo test -- --ignored`

```rust

pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_add() {
        assert_eq!(add(2, 2), 4);
    }

    #[test]
    fn test_add_hundred() {
        assert_eq!(add(100, 2), 102);
        assert_eq!(add(2, 100), 102);
    }

    #[test]
    #[ignore]
    fn ignored_test() {
        assert_eq!(add(0, 0), 0);
    }
}
```

```shell

$ cargo test
running 3 tests
test tests::ignored_test ... ignored
test tests::test_add ... ok
test tests::test_add_hundred ... ok

test result: ok. 2 passed; 0 failed; 1 ignored; 0 measured; 0 filtered out

   Doc-tests tmp-ignore

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out

$ cargo test -- --ignored
running 1 test
test tests::ignored_test ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out

   Doc-tests tmp-ignore

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```

# Documentation testing

The primary way of documenting a Rust project is through annotating the source
code. Documentation comments are written in
[CommonMark Markdown specification](https://commonmark.org/) and support code blocks in them.
Rust takes care about correctness, so these code blocks are compiled and used
as documentation tests.

````rust

/// First line is a short summary describing function.
///
/// The next lines present detailed documentation. Code blocks start with
/// triple backquotes and have implicit `fn main()` inside
/// and `extern crate <cratename>`. Assume we're testing a `playground` library
/// crate or using the Playground's Test action:
///
/// ```
/// let result = playground::add(2, 3);
/// assert_eq!(result, 5);
/// ```
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

/// Usually doc comments may include sections "Examples", "Panics" and "Failures".
///
/// The next function divides two numbers.
///
/// # Examples
///
/// ```
/// let result = playground::div(10, 2);
/// assert_eq!(result, 5);
/// ```
///
/// # Panics
///
/// The function panics if the second argument is zero.
///
/// ```rust,should_panic
/// // panics on division by zero
/// playground::div(10, 0);
/// ```
pub fn div(a: i32, b: i32) -> i32 {
    if b == 0 {
        panic!("Divide-by-zero error");
    }

    a / b
}
````

Code blocks in documentation are automatically tested
when running the regular `cargo test` command:

```shell

$ cargo test
running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out

   Doc-tests playground

running 3 tests
test src/lib.rs - add (line 7) ... ok
test src/lib.rs - div (line 21) ... ok
test src/lib.rs - div (line 31) ... ok

test result: ok. 3 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```

## Motivation behind documentation tests

The main purpose of documentation tests is to serve as examples that exercise
the functionality, which is one of the most important
[guidelines](https://rust-lang-nursery.github.io/api-guidelines/documentation.html#examples-use--not-try-not-unwrap-c-question-mark). It allows using examples from docs as
complete code snippets. But using `?` makes compilation fail since `main`
returns `unit`. The ability to hide some source lines from documentation comes
to the rescue: one may write `fn try_main() -> Result<(), ErrorType>`, hide it
and `unwrap` it in hidden `main`. Sounds complicated? Here’s an example:

````rust

/// Using hidden `try_main` in doc tests.
///
/// ```
/// # // hidden lines start with `#` symbol, but they're still compilable!
/// # fn try_main() -> Result<(), String> { // line that wraps the body shown in doc
/// let res = playground::try_div(10, 2)?;
/// # Ok(()) // returning from try_main
/// # }
/// # fn main() { // starting main that'll unwrap()
/// #    try_main().unwrap(); // calling try_main and unwrapping
/// #                         // so that test will panic in case of error
/// # }
/// ```
pub fn try_div(a: i32, b: i32) -> Result<i32, String> {
    if b == 0 {
        Err(String::from("Divide-by-zero"))
    } else {
        Ok(a / b)
    }
}
````

## See Also

- [RFC505](https://github.com/rust-lang/rfcs/blob/master/text/0505-api-comment-conventions.md) on documentation style
- [API Guidelines](https://rust-lang-nursery.github.io/api-guidelines/documentation.html) on documentation guidelines

# Integration testing

[Unit tests](https://doc.rust-lang.org/rust-by-example/print.html#unit-testing) are testing one module in isolation at a time: they’re small
and can test private code. Integration tests are external to your crate and use
only its public interface in the same way any other code would. Their purpose is
to test that many parts of your library work correctly together.

Cargo looks for integration tests in `tests` directory next to `src`.

File `src/lib.rs`:

```rust

// Define this in a crate called `adder`.
pub fn add(a: i32, b: i32) -> i32 {
    a + b
}
```

File with test: `tests/integration_test.rs`:

```rust

#[test]
fn test_add() {
    assert_eq!(adder::add(3, 2), 5);
}
```

Running tests with `cargo test` command:

```shell

$ cargo test
running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out

     Running target/debug/deps/integration_test-bcd60824f5fbfe19

running 1 test
test test_add ... ok

test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out

   Doc-tests adder

running 0 tests

test result: ok. 0 passed; 0 failed; 0 ignored; 0 measured; 0 filtered out
```

Each Rust source file in the `tests` directory is compiled as a separate crate. In
order to share some code between integration tests we can make a module with public
functions, importing and using it within tests.

File `tests/common/mod.rs`:

```rust

pub fn setup() {
    // some setup code, like creating required files/directories, starting
    // servers, etc.
}
```

File with test: `tests/integration_test.rs`

```rust

// importing common module.
mod common;

#[test]
fn test_add() {
    // using common code.
    common::setup();
    assert_eq!(adder::add(3, 2), 5);
}
```

Creating the module as `tests/common.rs` also works, but is not recommended
because the test runner will treat the file as a test crate and try to run tests
inside it.

# Development dependencies

Sometimes there is a need to have dependencies for tests (or examples,
or benchmarks) only. Such dependencies are added to `Cargo.toml` in the
`[dev-dependencies]` section. These dependencies are not propagated to other
packages which depend on this package.

One such example is [`pretty_assertions`](https://docs.rs/pretty_assertions/1.0.0/pretty_assertions/index.html), which extends standard `assert_eq!` and `assert_ne!` macros, to provide colorful diff.
File `Cargo.toml`:

```toml

# standard crate data is left out
[dev-dependencies]
pretty_assertions = "1"
```

File `src/lib.rs`:

```rust

pub fn add(a: i32, b: i32) -> i32 {
    a + b
}

#[cfg(test)]
mod tests {
    use super::*;
    use pretty_assertions::assert_eq; // crate for test-only use. Cannot be used in non-test code.

    #[test]
    fn test_add() {
        assert_eq!(add(2, 3), 5);
    }
}
```

## See Also

[Cargo](http://doc.crates.io/specifying-dependencies.html) docs on specifying dependencies.

# Unsafe Operations

As an introduction to this section, to borrow from [the official docs](https://doc.rust-lang.org/book/ch19-01-unsafe-rust.html),
“one should try to minimize the amount of unsafe code in a code base.” With that
in mind, let’s get started! Unsafe annotations in Rust are used to bypass
protections put in place by the compiler; specifically, there are four primary
things that unsafe is used for:

- dereferencing raw pointers
- calling functions or methods which are `unsafe` (including calling a function
over FFI, see [a previous chapter](https://doc.rust-lang.org/rust-by-example/print.html#foreign-function-interface) of the book)
- accessing or modifying static mutable variables
- implementing unsafe traits

### Raw Pointers

Raw pointers `*` and references `&T` function similarly, but references are
always safe because they are guaranteed to point to valid data due to the
borrow checker. Dereferencing a raw pointer can only be done through an unsafe
block.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

### Calling Unsafe Functions

Some functions can be declared as `unsafe`, meaning it is the programmer’s
responsibility to ensure correctness instead of the compiler’s. One example
of this is [`std::slice::from_raw_parts`](https://doc.rust-lang.org/std/slice/fn.from_raw_parts.html) which will create a slice given a
pointer to the first element and a length.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

For `slice::from_raw_parts`, one of the assumptions which _must_ be upheld is
that the pointer passed in points to valid memory and that the memory pointed to
is of the correct type. If these invariants aren’t upheld then the program’s
behaviour is undefined and there is no knowing what will happen.

# Inline assembly

Rust provides support for inline assembly via the `asm!` macro.
It can be used to embed handwritten assembly in the assembly output generated by the compiler.
Generally this should not be necessary, but might be where the required performance or timing
cannot be otherwise achieved. Accessing low level hardware primitives, e.g. in kernel code, may also demand this functionality.

> **Note**: the examples here are given in x86/x86-64 assembly, but other architectures are also supported.

Inline assembly is currently supported on the following architectures:

- x86 and x86-64
- ARM
- AArch64
- RISC-V

## Basic usage

Let us start with the simplest possible example:

```rust

#![allow(unused)]
fn main() {
#[cfg(target_arch = "x86_64")] {
use std::arch::asm;

unsafe {
    asm!("nop");
}
}
}
```

This will insert a NOP (no operation) instruction into the assembly generated by the compiler.
Note that all `asm!` invocations have to be inside an `unsafe` block, as they could insert
arbitrary instructions and break various invariants. The instructions to be inserted are listed
in the first argument of the `asm!` macro as a string literal.

## Inputs and outputs

Now inserting an instruction that does nothing is rather boring. Let us do something that
actually acts on data:

```rust

#![allow(unused)]
fn main() {
#[cfg(target_arch = "x86_64")] {
use std::arch::asm;

let x: u64;
unsafe {
    asm!("mov {}, 5", out(reg) x);
}
assert_eq!(x, 5);
}
}
```

This will write the value `5` into the `u64` variable `x`.
You can see that the string literal we use to specify instructions is actually a template string.
It is governed by the same rules as Rust [format strings](https://doc.rust-lang.org/std/fmt/#syntax).
The arguments that are inserted into the template however look a bit different than you may
be familiar with. First we need to specify if the variable is an input or an output of the
inline assembly. In this case it is an output. We declared this by writing `out`.
We also need to specify in what kind of register the assembly expects the variable.
In this case we put it in an arbitrary general purpose register by specifying `reg`.
The compiler will choose an appropriate register to insert into
the template and will read the variable from there after the inline assembly finishes executing.

Let us see another example that also uses an input:

```rust

#![allow(unused)]
fn main() {
#[cfg(target_arch = "x86_64")] {
use std::arch::asm;

let i: u64 = 3;
let o: u64;
unsafe {
    asm!(
        "mov {0}, {1}",
        "add {0}, 5",
        out(reg) o,
        in(reg) i,
    );
}
assert_eq!(o, 8);
}
}
```

This will add `5` to the input in variable `i` and write the result to variable `o`.
The particular way this assembly does this is first copying the value from `i` to the output,
and then adding `5` to it.

The example shows a few things:

First, we can see that `asm!` allows multiple template string arguments; each
one is treated as a separate line of assembly code, as if they were all joined
together with newlines between them. This makes it easy to format assembly
code.

Second, we can see that inputs are declared by writing `in` instead of `out`.

Third, we can see that we can specify an argument number, or name as in any format string.
For inline assembly templates this is particularly useful as arguments are often used more than once.
For more complex inline assembly using this facility is generally recommended, as it improves
readability, and allows reordering instructions without changing the argument order.

We can further refine the above example to avoid the `mov` instruction:

```rust

#![allow(unused)]
fn main() {
#[cfg(target_arch = "x86_64")] {
use std::arch::asm;

let mut x: u64 = 3;
unsafe {
    asm!("add {0}, 5", inout(reg) x);
}
assert_eq!(x, 8);
}
}
```

We can see that `inout` is used to specify an argument that is both input and output.
This is different from specifying an input and output separately in that it is guaranteed to assign both to the same register.

It is also possible to specify different variables for the input and output parts of an `inout` operand:

```rust

#![allow(unused)]
fn main() {
#[cfg(target_arch = "x86_64")] {
use std::arch::asm;

let x: u64 = 3;
let y: u64;
unsafe {
    asm!("add {0}, 5", inout(reg) x => y);
}
assert_eq!(y, 8);
}
}
```

## Late output operands

The Rust compiler is conservative with its allocation of operands. It is assumed that an `out`
can be written at any time, and can therefore not share its location with any other argument.
However, to guarantee optimal performance it is important to use as few registers as possible,
so they won’t have to be saved and reloaded around the inline assembly block.
To achieve this Rust provides a `lateout` specifier. This can be used on any output that is
written only after all inputs have been consumed. There is also an `inlateout` variant of this
specifier.

Here is an example where `inlateout` _cannot_ be used in `release` mode or other optimized cases:

```rust

#![allow(unused)]
fn main() {
#[cfg(target_arch = "x86_64")] {
use std::arch::asm;

let mut a: u64 = 4;
let b: u64 = 4;
let c: u64 = 4;
unsafe {
    asm!(
        "add {0}, {1}",
        "add {0}, {2}",
        inout(reg) a,
        in(reg) b,
        in(reg) c,
    );
}
assert_eq!(a, 12);
}
}
```

In unoptimized cases (e.g. `Debug` mode), replacing `inout(reg) a` with `inlateout(reg) a` in the
above example can continue to give the expected result. However, with `release` mode or other
optimized cases, using `inlateout(reg) a` can instead lead to the final value `a = 16`, causing the
assertion to fail.

This is because in optimized cases, the compiler is free to allocate the same register for inputs
`b` and `c` since it knows that they have the same value. Furthermore, when `inlateout` is used, `a`
and `c` could be allocated to the same register, in which case the first `add` instruction would
overwrite the initial load from variable `c`. This is in contrast to how using `inout(reg) a`
ensures a separate register is allocated for `a`.

However, the following example can use `inlateout` since the output is only modified after all input
registers have been read:

```rust

#![allow(unused)]
fn main() {
#[cfg(target_arch = "x86_64")] {
use std::arch::asm;

let mut a: u64 = 4;
let b: u64 = 4;
unsafe {
    asm!("add {0}, {1}", inlateout(reg) a, in(reg) b);
}
assert_eq!(a, 8);
}
}
```

As you can see, this assembly fragment will still work correctly if `a` and `b` are assigned to the same register.

## Explicit register operands

Some instructions require that the operands be in a specific register.
Therefore, Rust inline assembly provides some more specific constraint specifiers.
While `reg` is generally available on any architecture, explicit registers are highly architecture specific. E.g. for x86 the general purpose registers `eax`, `ebx`, `ecx`, `edx`, `ebp`, `esi`, and `edi` among others can be addressed by their name.

```rust

#![allow(unused)]
fn main() {
#[cfg(target_arch = "x86_64")] {
use std::arch::asm;

let cmd = 0xd1;
unsafe {
    asm!("out 0x64, eax", in("eax") cmd);
}
}
}
```

In this example we call the `out` instruction to output the content of the `cmd` variable to port `0x64`. Since the `out` instruction only accepts `eax` (and its sub registers) as operand we had to use the `eax` constraint specifier.

> **Note**: unlike other operand types, explicit register operands cannot be used in the template string: you can’t use `{}` and should write the register name directly instead. Also, they must appear at the end of the operand list after all other operand types.

Consider this example which uses the x86 `mul` instruction:

```rust

#![allow(unused)]
fn main() {
#[cfg(target_arch = "x86_64")] {
use std::arch::asm;

fn mul(a: u64, b: u64) -> u128 {
    let lo: u64;
    let hi: u64;

    unsafe {
        asm!(
            // The x86 mul instruction takes rax as an implicit input and writes
            // the 128-bit result of the multiplication to rax:rdx.
            "mul {}",
            in(reg) a,
            inlateout("rax") b => lo,
            lateout("rdx") hi
        );
    }

    ((hi as u128) << 64) + lo as u128
}
}
}
```

This uses the `mul` instruction to multiply two 64-bit inputs with a 128-bit result.
The only explicit operand is a register, that we fill from the variable `a`.
The second operand is implicit, and must be the `rax` register, which we fill from the variable `b`.
The lower 64 bits of the result are stored in `rax` from which we fill the variable `lo`.
The higher 64 bits are stored in `rdx` from which we fill the variable `hi`.

## Clobbered registers

In many cases inline assembly will modify state that is not needed as an output.
Usually this is either because we have to use a scratch register in the assembly or because instructions modify state that we don’t need to further examine.
This state is generally referred to as being “clobbered”.
We need to tell the compiler about this since it may need to save and restore this state around the inline assembly block.

```rust

use std::arch::asm;

#[cfg(target_arch = "x86_64")]
fn main() {
    // three entries of four bytes each
    let mut name_buf = [0_u8; 12];
    // String is stored as ascii in ebx, edx, ecx in order
    // Because ebx is reserved, the asm needs to preserve the value of it.
    // So we push and pop it around the main asm.
    // 64 bit mode on 64 bit processors does not allow pushing/popping of
    // 32 bit registers (like ebx), so we have to use the extended rbx register instead.

    unsafe {
        asm!(
            "push rbx",
            "cpuid",
            "mov [rdi], ebx",
            "mov [rdi + 4], edx",
            "mov [rdi + 8], ecx",
            "pop rbx",
            // We use a pointer to an array for storing the values to simplify
            // the Rust code at the cost of a couple more asm instructions
            // This is more explicit with how the asm works however, as opposed
            // to explicit register outputs such as `out("ecx") val`
            // The *pointer itself* is only an input even though it's written behind
            in("rdi") name_buf.as_mut_ptr(),
            // select cpuid 0, also specify eax as clobbered
            inout("eax") 0 => _,
            // cpuid clobbers these registers too
            out("ecx") _,
            out("edx") _,
        );
    }

    let name = core::str::from_utf8(&name_buf).unwrap();
    println!("CPU Manufacturer ID: {}", name);
}

#[cfg(not(target_arch = "x86_64"))]
fn main() {}
```

In the example above we use the `cpuid` instruction to read the CPU manufacturer ID.
This instruction writes to `eax` with the maximum supported `cpuid` argument and `ebx`, `edx`, and `ecx` with the CPU manufacturer ID as ASCII bytes in that order.

Even though `eax` is never read we still need to tell the compiler that the register has been modified so that the compiler can save any values that were in these registers before the asm. This is done by declaring it as an output but with `_` instead of a variable name, which indicates that the output value is to be discarded.

This code also works around the limitation that `ebx` is a reserved register by LLVM. That means that LLVM assumes that it has full control over the register and it must be restored to its original state before exiting the asm block, so it cannot be used as an input or output **except** if the compiler uses it to fulfill a general register class (e.g. `in(reg)`). This makes `reg` operands dangerous when using reserved registers as we could unknowingly corrupt our input or output because they share the same register.

To work around this we use `rdi` to store the pointer to the output array, save `ebx` via `push`, read from `ebx` inside the asm block into the array and then restore `ebx` to its original state via `pop`. The `push` and `pop` use the full 64-bit `rbx` version of the register to ensure that the entire register is saved. On 32 bit targets the code would instead use `ebx` in the `push`/`pop`.

This can also be used with a general register class to obtain a scratch register for use inside the asm code:

```rust

#![allow(unused)]
fn main() {
#[cfg(target_arch = "x86_64")] {
use std::arch::asm;

// Multiply x by 6 using shifts and adds
let mut x: u64 = 4;
unsafe {
    asm!(
        "mov {tmp}, {x}",
        "shl {tmp}, 1",
        "shl {x}, 2",
        "add {x}, {tmp}",
        x = inout(reg) x,
        tmp = out(reg) _,
    );
}
assert_eq!(x, 4 * 6);
}
}
```

## Symbol operands and ABI clobbers

By default, `asm!` assumes that any register not specified as an output will have its contents preserved by the assembly code. The [`clobber_abi`](https://doc.rust-lang.org/stable/reference/inline-assembly.html#abi-clobbers) argument to `asm!` tells the compiler to automatically insert the necessary clobber operands according to the given calling convention ABI: any register which is not fully preserved in that ABI will be treated as clobbered. Multiple `clobber_abi` arguments may be provided and all clobbers from all specified ABIs will be inserted.

```rust

#![allow(unused)]
fn main() {
#[cfg(target_arch = "x86_64")] {
use std::arch::asm;

extern "C" fn foo(arg: i32) -> i32 {
    println!("arg = {}", arg);
    arg * 2
}

fn call_foo(arg: i32) -> i32 {
    unsafe {
        let result;
        asm!(
            "call {}",
            // Function pointer to call
            in(reg) foo,
            // 1st argument in rdi
            in("rdi") arg,
            // Return value in rax
            out("rax") result,
            // Mark all registers which are not preserved by the "C" calling
            // convention as clobbered.
            clobber_abi("C"),
        );
        result
    }
}
}
}
```

## Register template modifiers

In some cases, fine control is needed over the way a register name is formatted when inserted into the template string. This is needed when an architecture’s assembly language has several names for the same register, each typically being a “view” over a subset of the register (e.g. the low 32 bits of a 64-bit register).

By default the compiler will always choose the name that refers to the full register size (e.g. `rax` on x86-64, `eax` on x86, etc).

This default can be overridden by using modifiers on the template string operands, just like you would with format strings:

```rust

#![allow(unused)]
fn main() {
#[cfg(target_arch = "x86_64")] {
use std::arch::asm;

let mut x: u16 = 0xab;

unsafe {
    asm!("mov {0:h}, {0:l}", inout(reg_abcd) x);
}

assert_eq!(x, 0xabab);
}
}
```

In this example, we use the `reg_abcd` register class to restrict the register allocator to the 4 legacy x86 registers (`ax`, `bx`, `cx`, `dx`) of which the first two bytes can be addressed independently.

Let us assume that the register allocator has chosen to allocate `x` in the `ax` register.
The `h` modifier will emit the register name for the high byte of that register and the `l` modifier will emit the register name for the low byte. The asm code will therefore be expanded as `mov ah, al` which copies the low byte of the value into the high byte.

If you use a smaller data type (e.g. `u16`) with an operand and forget to use template modifiers, the compiler will emit a warning and suggest the correct modifier to use.

## Memory address operands

Sometimes assembly instructions require operands passed via memory addresses/memory locations.
You have to manually use the memory address syntax specified by the target architecture.
For example, on x86/x86\_64 using Intel assembly syntax, you should wrap inputs/outputs in `[]` to indicate they are memory operands:

```rust

#![allow(unused)]
fn main() {
#[cfg(target_arch = "x86_64")] {
use std::arch::asm;

fn load_fpu_control_word(control: u16) {
    unsafe {
        asm!("fldcw [{}]", in(reg) &control, options(nostack));
    }
}
}
}
```

## Labels

Any reuse of a named label, local or otherwise, can result in an assembler or linker error or may cause other strange behavior. Reuse of a named label can happen in a variety of ways including:

- explicitly: using a label more than once in one `asm!` block, or multiple times across blocks.
- implicitly via inlining: the compiler is allowed to instantiate multiple copies of an `asm!` block, for example when the function containing it is inlined in multiple places.
- implicitly via LTO: LTO can cause code from _other crates_ to be placed in the same codegen unit, and so could bring in arbitrary labels.

As a consequence, you should only use GNU assembler **numeric** [local labels](https://sourceware.org/binutils/docs/as/Symbol-Names.html#Local-Labels) inside inline assembly code. Defining symbols in assembly code may lead to assembler and/or linker errors due to duplicate symbol definitions.

Moreover, on x86 when using the default Intel syntax, due to [an LLVM bug](https://bugs.llvm.org/show_bug.cgi?id=36144), you shouldn’t use labels exclusively made of `0` and `1` digits, e.g. `0`, `11` or `101010`, as they may end up being interpreted as binary values. Using `options(att_syntax)` will avoid any ambiguity, but that affects the syntax of the _entire_`asm!` block. (See [Options](https://doc.rust-lang.org/rust-by-example/print.html#options), below, for more on `options`.)

```rust

#![allow(unused)]
fn main() {
#[cfg(target_arch = "x86_64")] {
use std::arch::asm;

let mut a = 0;
unsafe {
    asm!(
        "mov {0}, 10",
        "2:",
        "sub {0}, 1",
        "cmp {0}, 3",
        "jle 2f",
        "jmp 2b",
        "2:",
        "add {0}, 2",
        out(reg) a
    );
}
assert_eq!(a, 5);
}
}
```

This will decrement the `{0}` register value from 10 to 3, then add 2 and store it in `a`.

This example shows a few things:

- First, that the same number can be used as a label multiple times in the same inline block.
- Second, that when a numeric label is used as a reference (as an instruction operand, for example), the suffixes “b” (“backward”) or ”f” (“forward”) should be added to the numeric label. It will then refer to the nearest label defined by this number in this direction.

## Options

By default, an inline assembly block is treated the same way as an external FFI function call with a custom calling convention: it may read/write memory, have observable side effects, etc. However, in many cases it is desirable to give the compiler more information about what the assembly code is actually doing so that it can optimize better.

Let’s take our previous example of an `add` instruction:

```rust

#![allow(unused)]
fn main() {
#[cfg(target_arch = "x86_64")] {
use std::arch::asm;

let mut a: u64 = 4;
let b: u64 = 4;
unsafe {
    asm!(
        "add {0}, {1}",
        inlateout(reg) a, in(reg) b,
        options(pure, nomem, nostack),
    );
}
assert_eq!(a, 8);
}
}
```

Options can be provided as an optional final argument to the `asm!` macro. We specified three options here:

- `pure` means that the asm code has no observable side effects and that its output depends only on its inputs. This allows the compiler optimizer to call the inline asm fewer times or even eliminate it entirely.
- `nomem` means that the asm code does not read or write to memory. By default the compiler will assume that inline assembly can read or write any memory address that is accessible to it (e.g. through a pointer passed as an operand, or a global).
- `nostack` means that the asm code does not push any data onto the stack. This allows the compiler to use optimizations such as the stack red zone on x86-64 to avoid stack pointer adjustments.

These allow the compiler to better optimize code using `asm!`, for example by eliminating pure `asm!` blocks whose outputs are not needed.

See the [reference](https://doc.rust-lang.org/stable/reference/inline-assembly.html) for the full list of available options and their effects.

# Compatibility

The Rust language is evolving rapidly, and because of this certain compatibility
issues can arise, despite efforts to ensure forwards-compatibility wherever
possible.

- [Raw identifiers](https://doc.rust-lang.org/rust-by-example/print.html#raw-identifiers)

# Raw identifiers

Rust, like many programming languages, has the concept of “keywords”.
These identifiers mean something to the language, and so you cannot use them in
places like variable names, function names, and other places.
Raw identifiers let you use keywords where they would not normally be allowed.
This is particularly useful when Rust introduces new keywords, and a library
using an older edition of Rust has a variable or function with the same name
as a keyword introduced in a newer edition.

For example, consider a crate `foo` compiled with the 2015 edition of Rust that
exports a function named `try`. This keyword is reserved for a new feature in
the 2018 edition, so without raw identifiers, we would have no way to name the
function.

```rust

extern crate foo;

fn main() {
    foo::try();
}
```

You’ll get this error:

```text

error: expected identifier, found keyword `try`
 --> src/main.rs:4:4
  |
4 | foo::try();
  |      ^^^ expected identifier, found keyword
```

You can write this with a raw identifier:

```rust

extern crate foo;

fn main() {
    foo::r#try();
}
```

# Meta

Some topics aren’t exactly relevant to how you program runs but provide you
tooling or infrastructure support which just makes things better for
everyone. These topics include:

- [Documentation](https://doc.rust-lang.org/rust-by-example/print.html#documentation): Generate library documentation for users via the included
`rustdoc`.
- [Playground](https://doc.rust-lang.org/rust-by-example/print.html#playground): Integrate the Rust Playground in your documentation.

# Documentation

Use `cargo doc` to build documentation in `target/doc`, `cargo doc --open`
will automatically open it in your web browser.

Use `cargo test` to run all tests (including documentation tests), and `cargo test --doc` to only run documentation tests.

These commands will appropriately invoke `rustdoc` (and `rustc`) as required.

## Doc comments

Doc comments are very useful for big projects that require documentation. When
running `rustdoc`, these are the comments that get compiled into
documentation. They are denoted by a `///`, and support [Markdown](https://en.wikipedia.org/wiki/Markdown).

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

To run the tests, first build the code as a library, then tell `rustdoc` where
to find the library so it can link it into each doctest program:

```shell

$ rustc doc.rs --crate-type lib
$ rustdoc --test --extern doc="libdoc.rlib" doc.rs
```

## Doc attributes

Below are a few examples of the most common `#[doc]` attributes used with
`rustdoc`.

### `inline`

Used to inline docs, instead of linking out to separate page.

```rust

#[doc(inline)]
pub use bar::Bar;

/// bar docs
pub mod bar {
    /// the docs for Bar
    pub struct Bar;
}
```

### `no_inline`

Used to prevent linking out to separate page or anywhere.

```rust

// Example from libcore/prelude
#[doc(no_inline)]
pub use crate::mem::drop;
```

### `hidden`

Using this tells `rustdoc` not to include this in documentation:

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

For documentation, `rustdoc` is widely used by the community. It’s what is used
to generate the [std library docs](https://doc.rust-lang.org/std/).

### See also:

- [The Rust Book: Making Useful Documentation Comments](https://doc.rust-lang.org/book/ch14-02-publishing-to-crates-io.html#making-useful-documentation-comments)
- [The rustdoc Book](https://doc.rust-lang.org/rustdoc/index.html)
- [The Reference: Doc comments](https://doc.rust-lang.org/stable/reference/comments.html#doc-comments)
- [RFC 1574: API Documentation Conventions](https://rust-lang.github.io/rfcs/1574-more-api-documentation-conventions.html#appendix-a-full-conventions-text)
- [RFC 1946: Relative links to other items from doc comments (intra-rustdoc links)](https://rust-lang.github.io/rfcs/1946-intra-rustdoc-links.html)
- [Is there any documentation style guide for comments? (reddit)](https://www.reddit.com/r/rust/comments/ahb50s/is_there_any_documentation_style_guide_for/)

# Playground

The [Rust Playground](https://play.rust-lang.org/) is a way to experiment with
Rust code through a web interface.

## Using it with `mdbook`

In [`mdbook`](https://github.com/rust-lang/mdBook), you can make code examples playable and editable.

```

XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

This allows the reader to both run your code sample, but also modify and tweak
it. The key here is the adding of the word `editable` to your codefence block
separated by a comma.

````markdown

```rust,editable
//...place your code here
```
````

Additionally, you can add `ignore` if you want `mdbook` to skip your code when
it builds and tests.

````markdown

```rust,editable,ignore
//...place your code here
```
````

## Using it with docs

You may have noticed in some of the [official Rust docs](https://doc.rust-lang.org/core/) a
button that says “Run”, which opens the code sample up in a new tab in Rust
Playground. This feature is enabled if you use the `#[doc]` attribute called
[`html_playground_url`](https://doc.rust-lang.org/rustdoc/write-documentation/the-doc-attribute.html#html_playground_url).

````text

#![doc(html_playground_url = "https://play.rust-lang.org/")]
//! ```
//! println!("Hello World");
//! ```
````

### See also:

- [The Rust Playground](https://play.rust-lang.org/)
- [The Rust Playground On Github](https://github.com/integer32llc/rust-playground/)
- [The rustdoc Book](https://doc.rust-lang.org/rustdoc/what-is-rustdoc.html)
