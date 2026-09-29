"""
Unit tests for the lexer. Run from the project root with:

    python -m pytest
"""

import pytest

from src.Lexical_Analyzer import Lexer, LexicalError
from src.Tokens import TokenType as T


def token_strings(source):
    """Lex the source and return each token as it would show in debug mode."""
    return [str(tok) for tok in Lexer(source).tokenize()]


def lex_error(source):
    with pytest.raises(LexicalError) as caught:
        Lexer(source).tokenize()
    return str(caught.value)


# --- valid input ---

def test_example_from_spec():
    assert token_strings("int x; x = 10 + 5;") == [
        "INT", "IDENTIFIER(x)", "SEMICOLON",
        "IDENTIFIER(x)", "ASSIGN", "INTEGER_LITERAL(10)",
        "PLUS", "INTEGER_LITERAL(5)", "SEMICOLON",
        "EOF",
    ]


def test_every_operator_and_delimiter():
    types = [tok.type for tok in Lexer("+ - * / = ( ) ;").tokenize()]
    assert types == [
        T.PLUS, T.MINUS, T.MULTIPLY, T.DIVIDE, T.ASSIGN,
        T.LEFT_PAREN, T.RIGHT_PAREN, T.SEMICOLON, T.EOF,
    ]


def test_keywords():
    types = [tok.type for tok in Lexer("int real print").tokenize()]
    assert types == [T.INT, T.REAL, T.PRINT, T.EOF]


def test_keywords_are_case_sensitive():
    assert token_strings("Int PRINT") == ["IDENTIFIER(Int)", "IDENTIFIER(PRINT)", "EOF"]


def test_identifier_that_starts_with_a_keyword():
    # "integer" shouldn't get split into INT + "eger"
    assert token_strings("integer printer") == [
        "IDENTIFIER(integer)", "IDENTIFIER(printer)", "EOF",
    ]


def test_identifiers_with_digits_and_underscores():
    assert token_strings("total_score student1 temperature2") == [
        "IDENTIFIER(total_score)", "IDENTIFIER(student1)",
        "IDENTIFIER(temperature2)", "EOF",
    ]


def test_integer_and_real_literals():
    assert token_strings("0 250 3.14 10.5") == [
        "INTEGER_LITERAL(0)", "INTEGER_LITERAL(250)",
        "REAL_LITERAL(3.14)", "REAL_LITERAL(10.5)", "EOF",
    ]


def test_no_spaces_needed_between_tokens():
    assert token_strings("print(x*2.5);") == [
        "PRINT", "LEFT_PAREN", "IDENTIFIER(x)", "MULTIPLY",
        "REAL_LITERAL(2.5)", "RIGHT_PAREN", "SEMICOLON", "EOF",
    ]


def test_line_numbers():
    tokens = Lexer("int x;\n\nx = 1;\r\n\tprint(x);").tokenize()
    lines = {tok.lexeme: tok.line for tok in tokens if tok.type != T.SEMICOLON}
    assert lines["int"] == 1
    assert lines["="] == 3
    assert lines["print"] == 4


def test_empty_source_gives_just_eof():
    assert token_strings("") == ["EOF"]
    assert token_strings("   \n\t  ") == ["EOF"]


# --- lexical errors ---

def test_unknown_character():
    assert lex_error("x = 10 @ 5;") == "Lexical Error on line 1: Unknown character '@'"


def test_error_reports_the_right_line():
    assert lex_error("int x;\nint y;\ny = $x;").startswith("Lexical Error on line 3:")


@pytest.mark.parametrize("source, bad_char", [
    ("$total", "$"),
    ("_x", "_"),
    (".5", "."),
    ("café", "é"),   # non-ASCII letters aren't allowed
    ("x = ²;", "²"),  # neither are superscript digits
])
def test_characters_that_cant_start_a_token(source, bad_char):
    assert f"Unknown character '{bad_char}'" in lex_error(source)


def test_identifier_starting_with_digit():
    assert "Invalid identifier '2value'" in lex_error("int 2value;")


def test_real_with_no_digits_after_dot():
    assert "Malformed real literal '10.'" in lex_error("x = 10.;")
