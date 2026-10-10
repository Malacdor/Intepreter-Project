"""
Interpreter for MiniLang.

Walks the AST the parser produced and actually runs the program: it keeps
each variable's type and current value in a symbol table, evaluates
expressions, and prints whatever print statements ask for.

The semantic analyzer should catch most mistakes before we get here, but
the interpreter still checks the ones that would otherwise crash Python
(an unknown variable, dividing by zero) so the user always gets a
MiniLang error instead of a traceback.
"""

from src.ast_nodes import (Assignment, BinaryExpression, Declaration, Identifier,
                           IntegerLiteral, PrintStatement, RealLiteral)
from src.errors import MiniLangRuntimeError
from src.symbol_table import SymbolTable


class Interpreter:
    def __init__(self, output=print):
        # output is called with each line a print statement produces.
        # Tests pass in a list's append to capture output instead of
        # writing to the screen.
        self._output = output
        self._symbols = SymbolTable()

    def run(self, program):
        for statement in program.statements:
            self._execute(statement)

    def symbol_table(self):
        """The variables as (name, type, initialized, value) rows, in the
        order they were declared. Debug mode shows these after a run, and
        after a runtime error they show the state at the failure."""
        return self._symbols.rows()

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
        if statement.name in self._symbols:
            raise MiniLangRuntimeError(
                statement.line,
                f"Variable '{statement.name}' is already declared.")
        self._symbols.declare(statement.name, statement.type_name,
                              statement.line)

    def _assign(self, statement):
        symbol = self._symbols.lookup(statement.name)
        if symbol is None:
            raise MiniLangRuntimeError(
                statement.line,
                f"Variable '{statement.name}' is assigned before it is declared.")

        value = self._evaluate(statement.expression)

        if symbol.type_name == "real":
            # Ints widen to reals, so "real r; r = 5;" stores 5.0.
            value = float(value)
        elif isinstance(value, float):
            raise MiniLangRuntimeError(
                statement.line,
                f"Cannot assign a real value to int variable '{statement.name}'.")

        symbol.value = value
        symbol.initialized = True

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
        symbol = self._symbols.lookup(identifier.name)
        if symbol is None:
            raise MiniLangRuntimeError(
                identifier.line,
                f"Variable '{identifier.name}' is used before it is declared.")
        if not symbol.initialized:
            raise MiniLangRuntimeError(
                identifier.line,
                f"Variable '{identifier.name}' is used before it is assigned a value.")
        return symbol.value


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
    # The project description's end-to-end example stores 20 in a real
    # variable and expects "20" to print, so a real with nothing after the
    # decimal point prints like an int. Other reals print normally ("2.5").
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)
