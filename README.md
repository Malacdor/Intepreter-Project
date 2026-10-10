# MiniLang Interpreter (CS 3210, Project 2)

An interpreter for MiniLang, a small language with `int` and `real` variables,
assignment, arithmetic and `print`. A source file goes through four stages:

    source file -> Lexical Analyzer -> Parser -> Semantic Analyzer -> Interpreter

Invalid programs are rejected with a message that names the error category
and the line number. The interpreter never shows a Python traceback for a bad
program.

## Requirements

Python 3.8 or newer. The interpreter uses only the standard library. Running
the tests needs pytest (`pip install pytest`).

## Running a program

Run these from the project root, the folder that contains `Main.py` and `src/`:

    python Main.py program1.mini

This prints only what the program's `print` statements produce. The exit code
is 0 for success, 1 if the program had an error, and 2 for a bad command line
or an unreadable file.

A short example, saved as `program1.mini`:

    int width;
    int height;
    int area;
    width = 10;
    height = 5;
    area = width * height;
    print(area);

Output:

    50

## Debug / display mode

Add `--debug` to also see the token stream, the AST, the final symbol table and
the program output:

    python Main.py program1.mini --debug

The output has four sections, each with its own heading:

    TOKENS
    ------
    INT
    IDENTIFIER(width)
    ...

    AST
    ---
    Program
      Declaration(int width)
      ...

    SYMBOL TABLE
    ------------
    width int 10
    height int 5
    area int 50

    PROGRAM OUTPUT
    --------------
    50

Each symbol table row is the variable name, its type and its value. A variable
that was declared but never assigned shows `(uninitialized)`. If a stage fails,
the sections before it are still shown, followed by the error. After a runtime
error the symbol table and the output so far are shown as well.

## Running the tests

    python -m pytest

This runs the unit tests for each stage and the end to end program tests. To
check a single program by hand, run it with `python Main.py`.

## Test programs

`tests/programs` holds 21 MiniLang programs. Each `NAME.mini` has a
`NAME.expected` file with the exact expected output or error message.
`tests/test_programs.py` runs every pair. To add a test, drop in a new
`.mini` and `.expected` pair. `tests/README.md` lists which required behavior
each program covers.

## Project layout

    Main.py                  command line entry point and debug mode
    src/Tokens.py            token types and the Token class
    src/Lexical_Analyzer.py  source text to tokens
    src/Parser.py            tokens to AST (recursive descent)
    src/ast_nodes.py         AST node classes
    src/ast_printer.py       AST text display for debug mode
    src/Semantic_Analyzer.py declaration, initialization and type checks
    src/Interpreter.py       runs the AST
    src/errors.py            syntax, semantic and runtime error classes
    tests/                   unit tests and the .mini test programs

## Error categories

    Lexical Error on line 1: Unknown character '@'
    Syntax Error on line 2: Expected ';' after assignment.
    Semantic Error on line 3: Variable 'x' is used before it is declared.
    Runtime Error on line 5: Division by zero.

Processing stops at the first error.

## Design decisions

* **Parser.** A recursive descent parser with one method per grammar rule.
  Precedence comes from how the rules call each other, and left associativity
  comes from building each tree in a loop. Parentheses get no AST node because
  the tree shape already records the grouping.
* **Semantic analysis.** One pass over the statements in order. MiniLang has no
  branches or loops, so "has this variable been assigned yet?" can be answered
  exactly before the program runs. The right side of an assignment is checked
  before the variable counts as assigned, so `int x; x = x + 1;` is rejected.
* **Types.** An `int` may be assigned to a `real` variable and is converted.
  A `real` value cannot be assigned to an `int` variable. An expression with
  any real operand is real.
* **Integer division.** `int / int` truncates toward zero, so `7 / 2` is 3 and
  `-7 / 2` is -3, the same as C and Java.
* **Printing reals.** A real with no fractional part prints without a decimal
  point, so 20.0 prints as 20. This matches the example in section 18 of the
  project description. Other reals print normally, for example 2.5.
* **Interpreter checks.** The interpreter repeats the checks that would
  otherwise crash Python (unknown variable, division by zero), so a bad AST
  still produces a MiniLang error.
* **Very large input.** Extremely deep nesting or enormous numbers produce an
  error message instead of a Python traceback.
