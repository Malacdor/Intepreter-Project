"""
Error types for the parser, semantic analyzer, and interpreter.

They all print the same way the lexer's LexicalError does:

    Syntax Error on line 3: Expected ';' after assignment.
"""


class MiniLangError(Exception):
    kind = "MiniLang"

    def __init__(self, line, message):
        super().__init__(f"{self.kind} Error on line {line}: {message}")
        self.line = line
        self.message = message


class MiniLangSyntaxError(MiniLangError):
    kind = "Syntax"


class MiniLangSemanticError(MiniLangError):
    kind = "Semantic"


class MiniLangRuntimeError(MiniLangError):
    kind = "Runtime"
