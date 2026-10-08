"""
AST node definitions shared by the parser, semantic analyzer, and interpreter.

The parser builds these, and the later stages walk them. Every node keeps
the line it came from so errors can point back to the source.
"""

from dataclasses import dataclass


@dataclass
class Program:
    statements: list


# ---- statements ----

@dataclass
class Declaration:
    type_name: str  # "int" or "real"
    name: str
    line: int


@dataclass
class Assignment:
    name: str
    expression: object
    line: int


@dataclass
class PrintStatement:
    expression: object
    line: int


# ---- expressions ----

@dataclass
class BinaryExpression:
    operator: str  # "+", "-", "*", or "/"
    left: object
    right: object
    line: int


@dataclass
class Identifier:
    name: str
    line: int


@dataclass
class IntegerLiteral:
    value: int
    line: int


@dataclass
class RealLiteral:
    value: float
    line: int
