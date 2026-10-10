"""
Unit tests for the AST display used by debug mode. Run from the project
root with:

    python -m pytest
"""

from src.ast_printer import format_ast
from src.Lexical_Analyzer import Lexer
from src.Parser import Parser


def ast_of(source):
    return format_ast(Parser(Lexer(source).tokenize()).parse())


def test_empty_program():
    assert ast_of("") == "Program"


def test_spec_example_tree():
    # The example in section 8 of the project description.
    assert ast_of("y = x + 5 * 2;") == "\n".join([
        "Program",
        "`-- Assignment(=)",
        "    |-- Identifier(y)",
        "    `-- Binary(+)",
        "        |-- Identifier(x)",
        "        `-- Binary(*)",
        "            |-- Integer(5)",
        "            `-- Integer(2)",
    ])


def test_declarations_and_print():
    assert ast_of("int x; real y; print(2.5);") == "\n".join([
        "Program",
        "|-- Declaration(int x)",
        "|-- Declaration(real y)",
        "`-- Print",
        "    `-- Real(2.5)",
    ])


def test_parentheses_show_up_as_tree_shape():
    # (1 + 2) * 3: the + ends up under the *, no node for the parentheses.
    assert ast_of("print((1 + 2) * 3);") == "\n".join([
        "Program",
        "`-- Print",
        "    `-- Binary(*)",
        "        |-- Binary(+)",
        "        |   |-- Integer(1)",
        "        |   `-- Integer(2)",
        "        `-- Integer(3)",
    ])


def test_left_associativity_is_visible():
    # 10 - 5 - 2 groups as (10 - 5) - 2.
    assert ast_of("print(10 - 5 - 2);") == "\n".join([
        "Program",
        "`-- Print",
        "    `-- Binary(-)",
        "        |-- Binary(-)",
        "        |   |-- Integer(10)",
        "        |   `-- Integer(5)",
        "        `-- Integer(2)",
    ])
