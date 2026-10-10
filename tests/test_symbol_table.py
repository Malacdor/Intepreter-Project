"""
Unit tests for the shared symbol table. Run from the project root with:

    python -m pytest
"""

from src.symbol_table import SymbolTable


def test_new_table_is_empty():
    table = SymbolTable()
    assert len(table) == 0
    assert table.rows() == []


def test_declare_records_name_type_and_line():
    table = SymbolTable()
    table.declare("count", "int", 3)
    symbol = table.lookup("count")
    assert symbol.name == "count"
    assert symbol.type_name == "int"
    assert symbol.declared_line == 3


def test_new_symbol_is_uninitialized():
    table = SymbolTable()
    symbol = table.declare("x", "real", 1)
    assert not symbol.initialized
    assert symbol.value is None


def test_lookup_of_undeclared_name_is_none():
    assert SymbolTable().lookup("ghost") is None


def test_contains():
    table = SymbolTable()
    table.declare("x", "int", 1)
    assert "x" in table
    assert "y" not in table


def test_names_are_case_sensitive():
    table = SymbolTable()
    table.declare("total", "int", 1)
    assert "Total" not in table


def test_rows_are_in_declaration_order():
    table = SymbolTable()
    table.declare("zeta", "int", 1)
    table.declare("alpha", "real", 2)
    width = table.declare("width", "int", 3)
    width.initialized = True
    width.value = 10
    assert table.rows() == [
        ("zeta", "int", False, None),
        ("alpha", "real", False, None),
        ("width", "int", True, 10),
    ]
