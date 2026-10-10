"""
End-to-end tests: every tests/programs/*.mini program is run through
Main.run(), and everything it prints (output and errors) must match the
.expected file next to it. To add a test, just drop a new .mini/.expected
pair into tests/programs/.

    python -m pytest
"""

from pathlib import Path

import pytest

from Main import run

PROGRAMS_DIR = Path(__file__).parent / "programs"
PROGRAMS = sorted(PROGRAMS_DIR.glob("*.mini"))


@pytest.mark.parametrize("program", PROGRAMS, ids=lambda path: path.stem)
def test_program_output(program, capsys):
    expected_file = program.with_suffix(".expected")
    assert expected_file.exists(), f"{program.name} has no .expected file"

    finished = run(program.read_text(encoding="utf-8"))
    captured = capsys.readouterr()
    printed = captured.out + captured.err

    assert printed.strip() == expected_file.read_text(encoding="utf-8").strip()
    # A program should only fail if its expected output says it does.
    assert finished == ("Error on line" not in printed)


def test_debug_mode_shows_all_four_sections(capsys):
    assert run("int x; real y; x = 1; print(x);", debug=True)
    out = capsys.readouterr().out

    # Sections appear in pipeline order.
    headings = ["TOKENS", "AST", "SYMBOL TABLE", "PROGRAM OUTPUT"]
    positions = [out.index(f"{heading}\n") for heading in headings]
    assert positions == sorted(positions)

    assert "IDENTIFIER(x)" in out
    assert "Declaration(int x)" in out
    assert "x int 1" in out
    assert "y real (uninitialized)" in out
    assert out.rstrip().endswith("1")


def test_debug_mode_after_runtime_error(capsys):
    # The symbol table and output so far are still shown before the error.
    assert not run("int a; a = 5; print(a); print(a / 0);", debug=True)
    captured = capsys.readouterr()
    assert "a int 5" in captured.out
    assert captured.out.rstrip().endswith("5")
    assert captured.err.strip() == "Runtime Error on line 1: Division by zero."


def test_normal_mode_shows_only_program_output(capsys):
    assert run("int x; x = 1; print(x);")
    assert capsys.readouterr().out == "1\n"
