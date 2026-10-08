"""
Semantic analyzer for MiniLang.

The parser only checks that a program is shaped right. This pass checks
that it makes sense, before anything runs:

  - every variable is declared before it's used or assigned
  - no variable is declared twice
  - no variable is read before it's been given a value
  - a real value is never stored in an int variable

It walks the AST in order, keeping a symbol table of each variable's
declared type and whether it has been assigned yet. MiniLang has no
branches or loops, so statements always run top to bottom, which makes
the "assigned yet?" check exact rather than a guess.
"""

from src.ast_nodes import (Assignment, BinaryExpression, Declaration, Identifier,
                           IntegerLiteral, PrintStatement, RealLiteral)
from src.errors import MiniLangSemanticError


class Symbol:
    def __init__(self, type_name, line):
        self.type_name = type_name  # "int" or "real"
        self.declared_line = line
        self.assigned = False


class SemanticAnalyzer:
    def __init__(self):
        self._symbols = {}  # name -> Symbol

    def analyze(self, program):
        """Check the whole program, raising MiniLangSemanticError on the
        first problem found. Returns the symbol table if it's all fine."""
        for statement in program.statements:
            self._check_statement(statement)
        return self._symbols

    # ---- statements ----

    def _check_statement(self, statement):
        if isinstance(statement, Declaration):
            self._check_declaration(statement)
        elif isinstance(statement, Assignment):
            self._check_assignment(statement)
        elif isinstance(statement, PrintStatement):
            self._type_of(statement.expression)
        else:
            raise MiniLangSemanticError(
                statement.line,
                f"Unknown statement {type(statement).__name__}.")

    def _check_declaration(self, statement):
        existing = self._symbols.get(statement.name)
        if existing is not None:
            raise MiniLangSemanticError(
                statement.line,
                f"Variable '{statement.name}' is already declared "
                f"(first declared on line {existing.declared_line}).")
        self._symbols[statement.name] = Symbol(statement.type_name,
                                               statement.line)

    def _check_assignment(self, statement):
        symbol = self._symbols.get(statement.name)
        if symbol is None:
            raise MiniLangSemanticError(
                statement.line,
                f"Variable '{statement.name}' is assigned before it is declared.")

        # Check the right-hand side before marking the variable assigned,
        # so "int x; x = x + 1;" is caught as using x before it has a value.
        value_type = self._type_of(statement.expression)

        # An int fits in a real, but a real would lose its fraction in an int.
        if symbol.type_name == "int" and value_type == "real":
            raise MiniLangSemanticError(
                statement.line,
                f"Type mismatch: cannot assign a real value to int "
                f"variable '{statement.name}'.")

        symbol.assigned = True

    # ---- expressions ----

    def _type_of(self, expression):
        """Return "int" or "real" for an expression, checking it on the way."""
        if isinstance(expression, IntegerLiteral):
            return "int"
        if isinstance(expression, RealLiteral):
            return "real"
        if isinstance(expression, Identifier):
            return self._check_identifier(expression)
        if isinstance(expression, BinaryExpression):
            left = self._type_of(expression.left)
            right = self._type_of(expression.right)
            # Same rule the interpreter follows: any real makes it real.
            if left == "real" or right == "real":
                return "real"
            return "int"
        raise MiniLangSemanticError(
            expression.line,
            f"Unknown expression {type(expression).__name__}.")

    def _check_identifier(self, identifier):
        symbol = self._symbols.get(identifier.name)
        if symbol is None:
            raise MiniLangSemanticError(
                identifier.line,
                f"Variable '{identifier.name}' is used before it is declared.")
        if not symbol.assigned:
            raise MiniLangSemanticError(
                identifier.line,
                f"Variable '{identifier.name}' is used before it is assigned a value.")
        return symbol.type_name
