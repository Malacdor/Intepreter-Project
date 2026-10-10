"""
Runs a MiniLang program.

    python Main.py program.mini
    python Main.py program.mini --debug

Normal mode prints only what the program's print statements produce.
Debug mode also shows the token stream, the AST, and the final symbol table.
"""

import sys

from src.ast_printer import format_ast
from src.errors import MiniLangError
from src.Interpreter import Interpreter, format_value
from src.Lexical_Analyzer import Lexer, LexicalError
from src.Parser import Parser
from src.Semantic_Analyzer import SemanticAnalyzer


def read_source(path):
    # open the .mini file and return its text
    with open(path, encoding="utf-8") as file:
        return file.read()


def print_section(title, lines):
    """Print a titled block of lines for debug mode."""
    print(title)
    print("-" * len(title))
    for line in lines:
        print(line)
    print()


def format_symbol_table(rows):
    lines = []
    for name, type_name, initialized, value in rows:
        shown = format_value(value) if initialized else "(uninitialized)"
        lines.append(f"{name} {type_name} {shown}")
    return lines


def run_and_show(program):
    """Debug mode execution: run the program, then show the symbol table
    and the program output. Both sections are shown even if the program
    stops with a runtime error, so the state at the failure is visible."""
    printed = []
    interpreter = Interpreter(output=printed.append)
    try:
        interpreter.run(program)
    finally:
        print_section("SYMBOL TABLE",
                      format_symbol_table(interpreter.symbol_table()))
        print_section("PROGRAM OUTPUT", printed)


def run(source, debug=False):
    """Run a program through every stage, printing its output.

    Returns True if it ran to the end, or False if any stage reported an
    error (which gets printed instead of a Python traceback).
    """
    try:
        tokens = Lexer(source).tokenize()
        if debug:
            print_section("TOKENS", [str(token) for token in tokens])

        program = Parser(tokens).parse()
        if debug:
            print_section("AST", format_ast(program).split("\n"))

        SemanticAnalyzer().analyze(program)
        if debug:
            run_and_show(program)
        else:
            Interpreter().run(program)
        return True
    except (LexicalError, MiniLangError) as error:
        # Flush first so the error shows up after anything the program
        # already printed, even when stdout is buffered (e.g. piped).
        sys.stdout.flush()
        print(error, file=sys.stderr)
        return False
    except (RecursionError, OverflowError, ValueError):
        # Last resort for inputs that push Python past its own limits: an
        # expression nested thousands of levels deep, or a number too large
        # to convert. The user gets a message instead of a traceback.
        sys.stdout.flush()
        print("Error: the program is too deeply nested or uses a number "
              "too large to process.", file=sys.stderr)
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
    except UnicodeDecodeError:
        print(f"Could not read '{paths[0]}': the file is not valid UTF-8 text.",
              file=sys.stderr)
        sys.exit(2)

    if not run(source, debug):
        sys.exit(1)


if __name__ == "__main__":
    main()
