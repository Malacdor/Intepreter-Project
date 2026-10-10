"""
Text display of the AST for debug mode.

For "y = x + 5 * 2;" it prints:

    Program
    `-- Assignment(=)
        |-- Identifier(y)
        `-- Binary(+)
            |-- Identifier(x)
            `-- Binary(*)
                |-- Integer(5)
                `-- Integer(2)

The node labels follow the example tree in the project description. The
branches are drawn with plain ASCII so the output shows up correctly in
any terminal, including the default Windows console.
"""

from src.ast_nodes import (Assignment, BinaryExpression, Declaration, Identifier,
                           IntegerLiteral, PrintStatement, Program, RealLiteral)


def format_ast(node):
    """Return the tree rooted at node as a multi-line string."""
    lines = [label(node)]
    _add_children(node, "", lines)
    return "\n".join(lines)


def _add_children(node, prefix, lines):
    kids = children(node)
    for index, child in enumerate(kids):
        last = index == len(kids) - 1
        lines.append(prefix + ("`-- " if last else "|-- ") + label(child))
        # Under the last child there's no more branch to continue, so its
        # own children get blank space instead of a "|".
        _add_children(child, prefix + ("    " if last else "|   "), lines)


def label(node):
    if isinstance(node, Program):
        return "Program"
    if isinstance(node, Declaration):
        return f"Declaration({node.type_name} {node.name})"
    if isinstance(node, Assignment):
        return "Assignment(=)"
    if isinstance(node, PrintStatement):
        return "Print"
    if isinstance(node, BinaryExpression):
        return f"Binary({node.operator})"
    if isinstance(node, Identifier):
        return f"Identifier({node.name})"
    if isinstance(node, IntegerLiteral):
        return f"Integer({node.value})"
    if isinstance(node, RealLiteral):
        return f"Real({node.value})"
    return type(node).__name__


def children(node):
    if isinstance(node, Program):
        return node.statements
    if isinstance(node, Assignment):
        # The target is stored as a plain name, so show it as an
        # Identifier node like the example tree does.
        return [Identifier(node.name, node.line), node.expression]
    if isinstance(node, PrintStatement):
        return [node.expression]
    if isinstance(node, BinaryExpression):
        return [node.left, node.right]
    return []
