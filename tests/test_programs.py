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


def test_debug_mode_prints_tokens(capsys):
    assert run("int x; x = 1; print(x);", debug=True)
    out = capsys.readouterr().out
    assert "IDENTIFIER(x)" in out
    assert "INTEGER_LITERAL(1)" in out
    assert out.rstrip().endswith("1")
