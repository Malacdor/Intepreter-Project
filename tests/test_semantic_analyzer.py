"""
Unit tests for the semantic analyzer. Run from the project root with:

    python -m pytest
"""

import pytest

from src.errors import MiniLangSemanticError
from src.Lexical_Analyzer import Lexer
from src.Parser import Parser
from src.Semantic_Analyzer import SemanticAnalyzer


def analyze(source):
    program = Parser(Lexer(source).tokenize()).parse()
    return SemanticAnalyzer().analyze(program)


def semantic_error(source):
    with pytest.raises(MiniLangSemanticError) as caught:
        analyze(source)
    return str(caught.value)


# --- valid programs ---

def test_empty_program():
    assert len(analyze("")) == 0


def test_declare_assign_print():
    analyze("int x; x = 10; print(x);")


def test_symbol_table_records_types():
    symbols = analyze("int count; real price; count = 1;")
    assert symbols["count"].type_name == "int"
    assert symbols["count"].initialized
    assert symbols["price"].type_name == "real"
    assert not symbols["price"].initialized


def test_int_value_into_real_variable_is_allowed():
    analyze("real r; r = 5; r = 2 + 3; print(r);")


def test_real_value_into_real_variable():
    analyze("real r; r = 2.5 * 2; print(r);")


def test_variable_used_after_assignment_in_later_expression():
    analyze("int x; int y; x = 1; y = x * 2 + x; print(y);")


def test_reassignment_using_own_value():
    analyze("int x; x = 1; x = x + 1; print(x);")


def test_printing_a_literal_needs_no_variables():
    analyze("print(1 + 2.5);")


def test_declared_but_never_used_is_fine():
    analyze("int unused;")


# --- undeclared variables ---

def test_use_of_undeclared_variable():
    assert semantic_error("print(ghost);") == (
        "Semantic Error on line 1: Variable 'ghost' is used before it is declared.")


def test_assignment_to_undeclared_variable():
    assert "'ghost' is assigned before it is declared" in semantic_error(
        "ghost = 1;")


def test_undeclared_variable_inside_expression():
    assert "'y' is used before it is declared" in semantic_error(
        "int x; x = 1 + (2 * y);")


def test_use_before_declaration_even_if_declared_later():
    assert "'x' is used before it is declared" in semantic_error(
        "print(x); int x;")


# --- duplicate declarations ---

def test_redeclaring_a_variable():
    assert semantic_error("int x;\nint x;") == (
        "Semantic Error on line 2: Variable 'x' is already declared "
        "(first declared on line 1).")


def test_redeclaring_with_a_different_type():
    assert "already declared" in semantic_error("int x; real x;")


# --- use before assignment ---

def test_use_before_assignment():
    assert "'x' is used before it is assigned a value" in semantic_error(
        "int x; print(x);")


def test_self_reference_in_first_assignment():
    # x has no value yet when x + 1 is computed.
    assert "'x' is used before it is assigned a value" in semantic_error(
        "int x; x = x + 1;")


def test_assigning_one_variable_doesnt_assign_another():
    assert "'b' is used before it is assigned a value" in semantic_error(
        "int a; int b; a = 1; print(a + b);")


# --- type mismatches ---

def test_real_literal_into_int_variable():
    assert semantic_error("int x;\nx = 2.5;") == (
        "Semantic Error on line 2: Type mismatch: cannot assign a real value "
        "to int variable 'x'.")


def test_mixed_expression_into_int_variable():
    assert "Type mismatch" in semantic_error("int x; x = 1 + 0.5;")


def test_real_variable_into_int_variable():
    assert "Type mismatch" in semantic_error(
        "real r; int x; r = 1.5; x = r;")


def test_real_division_into_int_variable():
    # 7.0 / 2 is a real even though 2 is an int.
    assert "Type mismatch" in semantic_error("int x; x = 7.0 / 2;")


def test_int_division_into_int_variable_is_fine():
    analyze("int x; x = 7 / 2;")


# --- error line numbers ---

def test_error_reports_the_line_of_the_bad_use():
    message = semantic_error("int x;\nint y;\nx = 1;\ny = x + z;\n")
    assert message.startswith("Semantic Error on line 4:")
