# MiniLang Test Suite

## Running the tests

From the project root:

    python -m pytest

This runs every unit test and every test program below. To run one program
by hand:

    python Main.py tests/programs/program_precedence.mini

## Test programs

Every program in `tests/programs/` comes as a pair:

* `NAME.mini` is the MiniLang source.
* `NAME.expected` is exactly what the interpreter should print: the program
  output, or the error message for an invalid program.

`test_programs.py` runs each `.mini` file through the full interpreter and
fails if the output differs from its `.expected` file in any way. To add a
test, drop a new pair into `tests/programs/`.

| Program | Valid? | What it checks | Expected result |
|---|---|---|---|
| `spec_example_area` | valid | The input/output example from section 13 | `50` |
| `spec_example_end_to_end` | valid | The example from section 18: an int expression promoted into a real variable | `20` |
| `program_int_arithmetic` | valid | `+ - * /` on int variables, int division | `15`, `-5`, `150`, `1` |
| `program_real_arithmetic` | valid | Real variables, real math, int stored in a real variable | `10`, `15`, `3`, `3.5`, `3` |
| `program_mixed_types` | valid | int and real in the same expression give a real; int / int stays int | `14.5`, `3.625`, `2`, `0`, `0.5` |
| `program_precedence` | valid | `*` and `/` before `+` and `-`, left to right at the same level | `14`, `20`, `10`, `2`, `3` |
| `program_parentheses` | valid | Parentheses override precedence, nested and redundant parentheses | `32`, `16`, `6`, `2`, `8` |
| `lexical_error_unknown_char` | invalid | Unknown character `@` | Lexical Error, line 2 |
| `lexical_error_bad_identifier` | invalid | Identifier starting with a digit (`2value`) | Lexical Error, line 2 |
| `lexical_error_malformed_real` | invalid | Real literal with no digits after the dot (`10.`) | Lexical Error, line 2 |
| `syntax_error_missing_semicolon` | invalid | Section 7 example: `int x` with no `;` | Syntax Error, line 1 |
| `syntax_error_bad_expression` | invalid | Section 7 example: `x = + 10;`, an expression starting with an operator | Syntax Error, line 2 |
| `syntax_error_unmatched_paren` | invalid | `print((x + 1) * 2;` with a missing `)` | Syntax Error, line 3 |
| `semantic_error_undeclared_variable` | invalid | Assigning to a variable that was never declared | Semantic Error, line 3 |
| `semantic_error_use_before_declaration` | invalid | Section 10 example: `x = 10; int x;` | Semantic Error, line 1 |
| `semantic_error_redeclaration` | invalid | Declaring the same name twice | Semantic Error, line 3 |
| `semantic_error_unassigned_variable` | invalid | Printing a declared variable that has no value | Semantic Error, line 5 |
| `semantic_error_uninitialized_in_expression` | invalid | Section 10 example: `int x; int y; y = x + 5;` | Semantic Error, line 3 |
| `semantic_error_type_mismatch` | invalid | Assigning a real expression to an int variable | Semantic Error, line 4 |
| `runtime_error_division_by_zero` | invalid | int division by a variable holding 0, after earlier output | `10`, then Runtime Error, line 6 |
| `runtime_error_real_division_by_zero` | invalid | real division by zero | `7.5`, then Runtime Error, line 6 |

## Required behavior coverage (section 14)

| Required behavior | Covered by |
|---|---|
| Basic variable declaration and assignment | `spec_example_area`, `program_int_arithmetic` |
| Arithmetic expressions | `program_int_arithmetic`, `program_real_arithmetic` |
| Operator precedence | `program_precedence`, `spec_example_end_to_end` |
| Parentheses | `program_parentheses`, `program_precedence` |
| int variables | `program_int_arithmetic`, `spec_example_area` |
| real variables | `program_real_arithmetic`, `spec_example_end_to_end` |
| Mixed int and real expressions | `program_mixed_types`, `program_real_arithmetic` |
| Undeclared variable | `semantic_error_undeclared_variable`, `semantic_error_use_before_declaration` |
| Duplicate declaration | `semantic_error_redeclaration` |
| Uninitialized variable | `semantic_error_unassigned_variable`, `semantic_error_uninitialized_in_expression` |
| Syntax error | `syntax_error_missing_semicolon`, `syntax_error_bad_expression`, `syntax_error_unmatched_paren` |
| Type error | `semantic_error_type_mismatch` |
| Lexical error | `lexical_error_unknown_char`, `lexical_error_bad_identifier`, `lexical_error_malformed_real` |
| Division by zero | `runtime_error_division_by_zero`, `runtime_error_real_division_by_zero` |

## Unit tests

Each stage also has its own unit tests:

| File | Tests |
|---|---|
| `test_lexer.py` | Lexical analyzer |
| `TestParser.py` | Parser, including syntax errors |
| `test_ast_printer.py` | AST display used by debug mode |
| `test_semantic_analyzer.py` | Semantic analyzer (all five rules from section 10) |
| `test_symbol_table.py` | Symbol table |
| `test_interpreter.py` | Interpreter, including the symbol table it keeps |
| `test_programs.py` | Runs the programs above, plus debug mode output |
