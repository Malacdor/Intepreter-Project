"""
Lexical analyzer for MiniLang.

Turns raw source text into a list of tokens. It walks through the text
one character at a time, and the character it's currently on decides
what kind of token comes next: a letter starts a word, a digit starts
a number, and so on.
"""

from src.Tokens import Token, TokenType


class LexicalError(Exception):
    def __init__(self, message, line):
        super().__init__(f"Lexical Error on line {line}: {message}")
        self.line = line


KEYWORDS = {
    "int": TokenType.INT,
    "real": TokenType.REAL,
    "print": TokenType.PRINT,
}

SINGLE_CHAR_TOKENS = {
    "+": TokenType.PLUS,
    "-": TokenType.MINUS,
    "*": TokenType.MULTIPLY,
    "/": TokenType.DIVIDE,
    "=": TokenType.ASSIGN,
    "(": TokenType.LEFT_PAREN,
    ")": TokenType.RIGHT_PAREN,
    ";": TokenType.SEMICOLON,
}


# We check letters and digits by hand rather than with str.isalpha() and
# str.isdigit(), because Python's versions accept characters like "é"
# and "²", which aren't allowed in MiniLang.
def is_letter(ch):
    return "a" <= ch <= "z" or "A" <= ch <= "Z"


def is_digit(ch):
    return "0" <= ch <= "9"


def is_word_char(ch):
    return is_letter(ch) or is_digit(ch) or ch == "_"


class Lexer:
    def __init__(self, source):
        self.source = source
        self.pos = 0
        self.line = 1

    def tokenize(self):
        tokens = []

        while self.pos < len(self.source):
            ch = self.source[self.pos]

            if ch in " \t\r":
                self.pos += 1
            elif ch == "\n":
                self.line += 1
                self.pos += 1
            elif is_letter(ch):
                tokens.append(self._read_word())
            elif is_digit(ch):
                tokens.append(self._read_number())
            elif ch in SINGLE_CHAR_TOKENS:
                tokens.append(Token(SINGLE_CHAR_TOKENS[ch], ch, self.line))
                self.pos += 1
            else:
                raise LexicalError(f"Unknown character '{ch}'", self.line)

        tokens.append(Token(TokenType.EOF, "", self.line))
        return tokens

    def _peek(self, offset=0):
        # Returns "" past the end of the input so callers don't need
        # to bounds-check before looking ahead.
        index = self.pos + offset
        if index < len(self.source):
            return self.source[index]
        return ""

    def _skip_while(self, condition):
        while self._peek() and condition(self._peek()):
            self.pos += 1

    def _read_word(self):
        start = self.pos
        self._skip_while(is_word_char)
        word = self.source[start:self.pos]

        # Keywords look exactly like identifiers, so we grab the whole
        # word first and then check whether it's reserved.
        token_type = KEYWORDS.get(word, TokenType.IDENTIFIER)
        return Token(token_type, word, self.line)

    def _read_number(self):
        start = self.pos
        self._skip_while(is_digit)
        token_type = TokenType.INTEGER_LITERAL

        if self._peek() == ".":
            # A real needs digits on both sides of the dot, so "10." is invalid.
            if not is_digit(self._peek(1)):
                bad_text = self.source[start:self.pos + 1]
                raise LexicalError(
                    f"Malformed real literal '{bad_text}' "
                    "(expected a digit after the decimal point)",
                    self.line,
                )
            self.pos += 1
            self._skip_while(is_digit)
            token_type = TokenType.REAL_LITERAL

        # If letters run straight into the number, like "2value", someone was
        # probably trying to write an identifier. Catching it here gives a much
        # clearer message than letting the parser trip over INTEGER_LITERAL(2)
        # followed by IDENTIFIER(value).
        if is_letter(self._peek()) or self._peek() == "_":
            self._skip_while(is_word_char)
            bad_text = self.source[start:self.pos]
            raise LexicalError(
                f"Invalid identifier '{bad_text}' "
                "(identifiers must start with a letter)",
                self.line,
            )

        return Token(token_type, self.source[start:self.pos], self.line)
