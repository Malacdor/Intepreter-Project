"""
Symbol table shared by the semantic analyzer and the interpreter.

Each declared variable gets one entry holding the four fields the project
description asks for: its name, its type, whether it has been given a
value yet, and that value.

The semantic analyzer fills in name, type, and initialized while it checks
the program (it never knows actual values). The interpreter keeps its own
table the same way and also stores each value as the program runs, which
is what debug mode shows as the final symbol table.

The table only stores facts. Deciding what counts as an error (and which
kind) is left to whichever stage is using it.
"""


class Symbol:
    def __init__(self, name, type_name, declared_line):
        self.name = name
        self.type_name = type_name  # "int" or "real"
        self.declared_line = declared_line
        self.initialized = False
        self.value = None  # set once initialized, by the interpreter


class SymbolTable:
    def __init__(self):
        # dicts keep insertion order, so iterating gives variables in the
        # order they were declared.
        self._symbols = {}

    def declare(self, name, type_name, line):
        symbol = Symbol(name, type_name, line)
        self._symbols[name] = symbol
        return symbol

    def lookup(self, name):
        """Return the variable's Symbol, or None if it isn't declared."""
        return self._symbols.get(name)

    def __contains__(self, name):
        return name in self._symbols

    def __getitem__(self, name):
        return self._symbols[name]

    def __iter__(self):
        return iter(self._symbols.values())

    def __len__(self):
        return len(self._symbols)

    def rows(self):
        """One (name, type, initialized, value) tuple per variable, in
        declaration order, for displaying the table."""
        return [(symbol.name, symbol.type_name, symbol.initialized, symbol.value)
                for symbol in self]
