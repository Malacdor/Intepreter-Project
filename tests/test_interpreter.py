"""
Unit tests for the interpreter. The ASTs are built by hand so these tests
don't depend on the lexer or parser. Run from the project root with:

    python -m pytest
"""

import pytest

from src.ast_nodes import (Assignment, BinaryExpression, Declaration, Identifier,
                           IntegerLiteral, PrintStatement, Program, RealLiteral)
from src.errors import MiniLangRuntimeError
from src.Interpreter import Interpreter, format_value


def run(*statements):
    """Run the statements and return the lines they printed."""
    lines = []
    Interpreter(output=lines.append).run(Program(list(statements)))
    return lines


def runtime_error(*statements):
    with pytest.raises(MiniLangRuntimeError) as caught:
        run(*statements)
    return str(caught.value)


def num(value):
    if isinstance(value, float):
        return RealLiteral(value, 1)
    return IntegerLiteral(value, 1)


def binary(left, operator, right):
    return BinaryExpression(operator, left, right, 1)


def var(name):
    return Identifier(name, 1)


def print_(expression):
    return PrintStatement(expression, 1)


# --- printing values ---

def test_print_integer_literal():
    assert run(print_(num(42))) == ["42"]


def test_print_real_literal():
    assert run(print_(num(3.14))) == ["3.14"]


def test_each_print_is_its_own_line():
    assert run(print_(num(1)), print_(num(2))) == ["1", "2"]


def test_empty_program_prints_nothing():
    assert run() == []


# --- variables ---

def test_declare_assign_and_print():
    assert run(
        Declaration("int", "x", 1),
        Assignment("x", num(10), 2),
        print_(var("x")),
    ) == ["10"]


def test_reassignment_replaces_the_value():
    assert run(
        Declaration("int", "x", 1),
        Assignment("x", num(1), 2),
        Assignment("x", num(2), 3),
        print_(var("x")),
    ) == ["2"]


def test_assignment_can_use_the_variables_old_value():
    # x = x + 1;
    assert run(
        Declaration("int", "x", 1),
        Assignment("x", num(5), 2),
        Assignment("x", binary(var("x"), "+", num(1)), 3),
        print_(var("x")),
    ) == ["6"]


def test_int_assigned_to_real_variable_becomes_real():
    interpreter = Interpreter(output=lambda line: None)
    interpreter.run(Program([
        Declaration("real", "r", 1),
        Assignment("r", num(5), 2),
    ]))
    [(name, type_name, initialized, value)] = interpreter.symbol_table()
    assert (name, type_name, initialized) == ("r", "real", True)
    assert isinstance(value, float) and value == 5.0


# --- printing reals ---

@pytest.mark.parametrize("value, expected", [
    (20.0, "20"),     # whole-number reals print like ints (spec section 18)
    (-3.0, "-3"),
    (0.0, "0"),
    (2.5, "2.5"),
    (3.14, "3.14"),
    (-0.5, "-0.5"),
    (7, "7"),
])
def test_format_value(value, expected):
    assert format_value(value) == expected


def test_spec_end_to_end_example():
    # int x; real y; x = 10; y = x + 5 * 2; print(y);  ->  20
    assert run(
        Declaration("int", "x", 1),
        Declaration("real", "y", 2),
        Assignment("x", num(10), 3),
        Assignment("y", binary(var("x"), "+", binary(num(5), "*", num(2))), 4),
        print_(var("y")),
    ) == ["20"]


# --- symbol table ---

def test_symbol_table_after_a_run():
    interpreter = Interpreter(output=lambda line: None)
    interpreter.run(Program([
        Declaration("int", "width", 1),
        Declaration("real", "ratio", 2),
        Declaration("int", "unused", 3),
        Assignment("width", num(10), 4),
        Assignment("ratio", num(0.5), 5),
    ]))
    assert interpreter.symbol_table() == [
        ("width", "int", True, 10),
        ("ratio", "real", True, 0.5),
        ("unused", "int", False, None),
    ]


def test_symbol_table_shows_latest_value():
    interpreter = Interpreter(output=lambda line: None)
    interpreter.run(Program([
        Declaration("int", "x", 1),
        Assignment("x", num(1), 2),
        Assignment("x", num(99), 3),
    ]))
    assert interpreter.symbol_table() == [("x", "int", True, 99)]


def test_symbol_table_keeps_state_from_before_a_runtime_error():
    interpreter = Interpreter(output=lambda line: None)
    with pytest.raises(MiniLangRuntimeError):
        interpreter.run(Program([
            Declaration("int", "a", 1),
            Assignment("a", num(10), 2),
            Declaration("int", "b", 3),
            Assignment("b", binary(var("a"), "/", num(0)), 4),
        ]))
    assert interpreter.symbol_table() == [
        ("a", "int", True, 10),
        ("b", "int", False, None),
    ]


def test_empty_symbol_table():
    interpreter = Interpreter(output=lambda line: None)
    interpreter.run(Program([]))
    assert interpreter.symbol_table() == []


# --- arithmetic ---

@pytest.mark.parametrize("left, operator, right, expected", [
    (10, "+", 5, "15"),
    (10, "-", 15, "-5"),
    (6, "*", 7, "42"),
    (2.5, "+", 1.5, "4"),
    (1.5, "*", 2.0, "3"),
    (7.0, "/", 2.0, "3.5"),
])
def test_basic_operators(left, operator, right, expected):
    assert run(print_(binary(num(left), operator, num(right)))) == [expected]


def test_mixing_int_and_real_gives_real():
    assert run(print_(binary(num(1), "+", num(0.5)))) == ["1.5"]
    assert run(print_(binary(num(7), "/", num(2.0)))) == ["3.5"]


@pytest.mark.parametrize("left, right, expected", [
    (7, 2, "3"),
    (6, 3, "2"),
    (1, 2, "0"),
    # Truncates toward zero like C/Java, not toward -infinity like Python's //.
    (-7, 2, "-3"),
    (7, -2, "-3"),
    (-7, -2, "3"),
])
def test_int_division_truncates_toward_zero(left, right, expected):
    assert run(print_(binary(num(left), "/", num(right)))) == [expected]


def test_nested_expression():
    # (1 + 2) * (10 - 4) / 3  ->  3 * 6 / 3  ->  6
    tree = binary(
        binary(binary(num(1), "+", num(2)), "*", binary(num(10), "-", num(4))),
        "/",
        num(3),
    )
    assert run(print_(tree)) == ["6"]


# --- runtime errors ---

def test_int_division_by_zero():
    message = runtime_error(print_(BinaryExpression("/", num(1), num(0), 4)))
    assert message == "Runtime Error on line 4: Division by zero."


def test_real_division_by_zero():
    assert "Division by zero" in runtime_error(
        print_(binary(num(1.5), "/", num(0.0))))


def test_division_by_zero_through_a_variable():
    assert "Division by zero" in runtime_error(
        Declaration("int", "z", 1),
        Assignment("z", num(0), 2),
        print_(binary(num(10), "/", var("z"))),
    )


def test_output_before_an_error_is_kept():
    lines = []
    interpreter = Interpreter(output=lines.append)
    with pytest.raises(MiniLangRuntimeError):
        interpreter.run(Program([
            print_(num(1)),
            print_(binary(num(1), "/", num(0))),
            print_(num(2)),
        ]))
    assert lines == ["1"]


def test_use_of_undeclared_variable():
    message = runtime_error(PrintStatement(Identifier("ghost", 3), 3))
    assert message == ("Runtime Error on line 3: "
                       "Variable 'ghost' is used before it is declared.")


def test_assignment_to_undeclared_variable():
    assert "assigned before it is declared" in runtime_error(
        Assignment("ghost", num(1), 1))


def test_use_of_declared_but_unassigned_variable():
    assert "before it is assigned a value" in runtime_error(
        Declaration("int", "x", 1),
        print_(var("x")),
    )


def test_redeclaring_a_variable():
    assert "already declared" in runtime_error(
        Declaration("int", "x", 1),
        Declaration("real", "x", 2),
    )


def test_real_assigned_to_int_variable():
    assert "Cannot assign a real value to int variable 'x'" in runtime_error(
        Declaration("int", "x", 1),
        Assignment("x", num(2.5), 2),
    )
