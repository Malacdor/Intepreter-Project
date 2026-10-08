"""
Runs a MiniLang program.

    python Main.py program.mini
    python Main.py program.mini --debug
"""

import sys

from src.errors import MiniLangError
from src.Interpreter import Interpreter
from src.Lexical_Analyzer import Lexer, LexicalError
from src.Parser import Parser
from src.Semantic_Analyzer import SemanticAnalyzer


def read_source(path):
    # open the .mini file and return its text
    with open(path, encoding="utf-8") as file:
        return file.read()


def run(source, debug=False):
    """Run a program through every stage, printing its output.

    Returns True if it ran to the end, or False if any stage reported an
    error (which gets printed instead of a Python traceback).
    """
    try:
        tokens = Lexer(source).tokenize()
        if debug:
            print("Tokens:")
            for token in tokens:
                print(f"  {token}")
            print()

        program = Parser(tokens).parse()

        SemanticAnalyzer().analyze(program)
        Interpreter().run(program)
        return True
    except (LexicalError, MiniLangError) as error:
        # Flush first so the error shows up after anything the program
        # already printed, even when stdout is buffered (e.g. piped).
        sys.stdout.flush()
        print(error, file=sys.stderr)
        return False


def main():
    # grab the file path and --debug flag, then call run()
    args = sys.argv[1:]
    debug = "--debug" in args
    paths = [arg for arg in args if arg != "--debug"]

    if len(paths) != 1:
        print("Usage: python Main.py program.mini [--debug]", file=sys.stderr)
        sys.exit(2)

    try:
        source = read_source(paths[0])
    except OSError as error:
        print(f"Could not read '{paths[0]}': {error.strerror}", file=sys.stderr)
        sys.exit(2)

    if not run(source, debug):
        sys.exit(1)


if __name__ == "__main__":
    main()
