"""
Unit tests for the interpreter. The ASTs are built by hand so these tests
don't depend on the lexer or parser. Run from the project root with:

    python -m pytest
"""

import pytest

from src.ast_nodes import (Assignment, BinaryExpression, Declaration, Identifier,
                           IntegerLiteral, PrintStatement, Program, RealLiteral)
from src.errors import MiniLangRuntimeError
from src.Interpreter import Interpreter


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
    assert run(
        Declaration("real", "r", 1),
        Assignment("r", num(5), 2),
        print_(var("r")),
    ) == ["5.0"]


# --- arithmetic ---

@pytest.mark.parametrize("left, operator, right, expected", [
    (10, "+", 5, "15"),
    (10, "-", 15, "-5"),
    (6, "*", 7, "42"),
    (2.5, "+", 1.5, "4.0"),
    (1.5, "*", 2.0, "3.0"),
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
