

from src.ast_nodes import (Assignment, BinaryExpression, Declaration, Identifier,
                       IntegerLiteral, PrintStatement, Program, RealLiteral)
from src.errors import MiniLangSyntaxError
from src.Tokens import Token, TokenType

T = TokenType


class Parser:
    def __init__(self, tokens):
        self._tokens = list(tokens)
        # Guarantee an EOF token so the parser never runs off the list.
        if not self._tokens or self._tokens[-1].type != T.EOF:
            last_line = self._tokens[-1].line if self._tokens else 1
            self._tokens.append(Token(T.EOF, "", last_line))
        self._pos = 0

    # ---- public entry point ----

    def parse(self):
        statements = []
        while not self._check(T.EOF):
            statements.append(self._statement())
        return Program(statements)

    # ---- grammar rules ----

    def _statement(self):
        token = self._peek()
        if token.type in (T.INT, T.REAL):
            return self._declaration()
        if token.type == T.IDENTIFIER:
            return self._assignment()
        if token.type == T.PRINT:
            return self._print_statement()
        raise MiniLangSyntaxError(
            token.line,
            f"Unexpected {self._describe(token)} at start of statement. "
            "Expected a declaration, assignment, or print statement.")

    def _declaration(self):
        type_token = self._advance()
        name_token = self._expect(
            T.IDENTIFIER,
            f"Expected identifier after type '{type_token.lexeme}'.")
        self._expect(T.SEMICOLON,
                     "Expected ';' after variable declaration.",
                     report_on_previous=True)
        return Declaration(type_token.lexeme, name_token.lexeme,
                           type_token.line)

    def _assignment(self):
        name_token = self._advance()
        self._expect(T.ASSIGN,
                     f"Expected '=' after identifier '{name_token.lexeme}'.")
        expression = self._expression()
        self._expect(T.SEMICOLON, "Expected ';' after assignment.",
                     report_on_previous=True)
        return Assignment(name_token.lexeme, expression, name_token.line)

    def _print_statement(self):
        print_token = self._advance()
        self._expect(T.LEFT_PAREN, "Expected '(' after 'print'.")
        expression = self._expression()
        self._expect(T.RIGHT_PAREN,
                     "Expected ')' after expression in print statement.")
        self._expect(T.SEMICOLON, "Expected ';' after print statement.",
                     report_on_previous=True)
        return PrintStatement(expression, print_token.line)

    def _expression(self):
        left = self._term()
        while self._check(T.PLUS, T.MINUS):
            operator = self._advance()
            right = self._term()
            left = BinaryExpression(operator.lexeme, left, right,
                                    operator.line)
        return left

    def _term(self):
        left = self._factor()
        while self._check(T.MULTIPLY, T.DIVIDE):
            operator = self._advance()
            right = self._factor()
            left = BinaryExpression(operator.lexeme, left, right,
                                    operator.line)
        return left

    def _factor(self):
        token = self._peek()
        if token.type == T.IDENTIFIER:
            self._advance()
            return Identifier(token.lexeme, token.line)
        if token.type == T.INTEGER_LITERAL:
            self._advance()
            return IntegerLiteral(int(token.lexeme), token.line)
        if token.type == T.REAL_LITERAL:
            self._advance()
            return RealLiteral(float(token.lexeme), token.line)
        if token.type == T.LEFT_PAREN:
            self._advance()
            inner = self._expression()
            self._expect(T.RIGHT_PAREN,
                         "Expected ')' to close parenthesized expression.")
            return inner
        raise MiniLangSyntaxError(
            token.line,
            f"Expected an expression but found {self._describe(token)}.")

    # ---- helpers ----

    def _peek(self):
        return self._tokens[self._pos]

    def _previous(self):
        return self._tokens[self._pos - 1]

    def _advance(self):
        token = self._tokens[self._pos]
        if token.type != T.EOF:
            self._pos += 1
        return token

    def _check(self, *types):
        return self._peek().type in types

    def _expect(self, token_type, message, report_on_previous=False):
        """Consume a token of the given type or raise a syntax error.

        For a missing ';' the useful line is the end of the statement,
        not the start of the next one, so callers can ask for the line
        of the previous token.
        """
        if self._check(token_type):
            return self._advance()
        if report_on_previous and self._pos > 0:
            line = self._previous().line
        else:
            line = self._peek().line
        raise MiniLangSyntaxError(line, message)

    @staticmethod
    def _describe(token):
        if token.type == T.EOF:
            return "end of input"
        return f"'{token.lexeme}'"
