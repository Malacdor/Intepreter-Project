"""
Token definitions shared by the lexer and the parser.

The lexer creates these and the parser consumes them, so if anything
in here changes, the parser probably has to change too.
"""

from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    # Keywords
    INT = auto()
    REAL = auto()
    PRINT = auto()

    # Names and numbers
    IDENTIFIER = auto()
    INTEGER_LITERAL = auto()
    REAL_LITERAL = auto()

    # Operators and punctuation
    ASSIGN = auto()
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    LEFT_PAREN = auto()
    RIGHT_PAREN = auto()
    SEMICOLON = auto()

    # Always the last token in the list, so the parser can tell when it's
    # run out of input (and complain if there are leftover tokens).
    EOF = auto()


# For these types the actual text matters, so debug output shows it,
# e.g. IDENTIFIER(x). A PLUS is always "+", so it doesn't need that.
_SHOW_LEXEME = {
    TokenType.IDENTIFIER,
    TokenType.INTEGER_LITERAL,
    TokenType.REAL_LITERAL,
}


@dataclass(frozen=True)
class Token:
    type: TokenType
    lexeme: str  # exact text from the source: "x", "10", "3.14", "+"
    line: int    # line it appeared on, used in error messages

    def __str__(self):
        if self.type in _SHOW_LEXEME:
            return f"{self.type.name}({self.lexeme})"
        return self.type.name
