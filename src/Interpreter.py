"""
Interpreter for MiniLang.

Walks the AST the parser produced and actually runs the program: it keeps
track of each variable's type and value, evaluates expressions, and
prints whatever print statements ask for.

The semantic analyzer should catch most mistakes before we get here, but
the interpreter still checks the ones that would otherwise crash Python
(an unknown variable, dividing by zero) so the user always gets a
MiniLang error instead of a traceback.
"""

from src.ast_nodes import (Assignment, BinaryExpression, Declaration, Identifier,
                           IntegerLiteral, PrintStatement, RealLiteral)
from src.errors import MiniLangRuntimeError


class Interpreter:
    def __init__(self, output=print):
        # output is called with each line a print statement produces.
        # Tests pass in a list's append to capture output instead of
        # writing to the screen.
        self._output = output
        self._types = {}   # name -> "int" or "real"
        self._values = {}  # name -> current value; missing until assigned

    def run(self, program):
        for statement in program.statements:
            self._execute(statement)

    # ---- statements ----

    def _execute(self, statement):
        if isinstance(statement, Declaration):
            self._declare(statement)
        elif isinstance(statement, Assignment):
            self._assign(statement)
        elif isinstance(statement, PrintStatement):
            self._output(format_value(self._evaluate(statement.expression)))
        else:
            raise MiniLangRuntimeError(
                statement.line,
                f"Don't know how to run {type(statement).__name__}.")

    def _declare(self, statement):
        if statement.name in self._types:
            raise MiniLangRuntimeError(
                statement.line,
                f"Variable '{statement.name}' is already declared.")
        self._types[statement.name] = statement.type_name

    def _assign(self, statement):
        declared_type = self._types.get(statement.name)
        if declared_type is None:
            raise MiniLangRuntimeError(
                statement.line,
                f"Variable '{statement.name}' is assigned before it is declared.")

        value = self._evaluate(statement.expression)

        if declared_type == "real":
            # Ints widen to reals, so "real r; r = 5;" stores 5.0.
            value = float(value)
        elif isinstance(value, float):
            raise MiniLangRuntimeError(
                statement.line,
                f"Cannot assign a real value to int variable '{statement.name}'.")

        self._values[statement.name] = value

    # ---- expressions ----

    def _evaluate(self, expression):
        if isinstance(expression, IntegerLiteral):
            return expression.value
        if isinstance(expression, RealLiteral):
            return expression.value
        if isinstance(expression, Identifier):
            return self._lookup(expression)
        if isinstance(expression, BinaryExpression):
            left = self._evaluate(expression.left)
            right = self._evaluate(expression.right)
            return apply_operator(expression.operator, left, right,
                                  expression.line)
        raise MiniLangRuntimeError(
            expression.line,
            f"Don't know how to evaluate {type(expression).__name__}.")

    def _lookup(self, identifier):
        if identifier.name not in self._types:
            raise MiniLangRuntimeError(
                identifier.line,
                f"Variable '{identifier.name}' is used before it is declared.")
        if identifier.name not in self._values:
            raise MiniLangRuntimeError(
                identifier.line,
                f"Variable '{identifier.name}' is used before it is assigned a value.")
        return self._values[identifier.name]


def apply_operator(operator, left, right, line):
    if operator == "+":
        return left + right
    if operator == "-":
        return left - right
    if operator == "*":
        return left * right
    if operator == "/":
        if right == 0:
            raise MiniLangRuntimeError(line, "Division by zero.")
        if isinstance(left, int) and isinstance(right, int):
            return int_divide(left, right)
        return left / right
    raise MiniLangRuntimeError(line, f"Unknown operator '{operator}'.")


def int_divide(left, right):
    # Python's // rounds toward negative infinity (-7 // 2 == -4), but
    # integer division in C and Java truncates toward zero (-7 / 2 == -3),
    # which is what people expect from an int / int in a language like this.
    quotient = abs(left) // abs(right)
    if (left < 0) != (right < 0):
        return -quotient
    return quotient


def format_value(value):
    # Python already prints ints as "15" and floats as "2.5" or "3.0",
    # which keeps reals visibly different from ints.
    return str(value)
