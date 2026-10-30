"""The committed goldens are what the oracle produces today, and the export
refuses what is not a single fixpoint of facts."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from export_goldens import EXPORTED, NotFactual, render  # noqa: E402
from fixtures import NAF  # noqa: E402

GOLDENS = Path(__file__).parent.parent / "goldens"


@pytest.mark.parametrize("fx", EXPORTED, ids=lambda f: f.fixture_id)
def test_committed_golden_is_current(fx):
    assert (GOLDENS / f"{fx.fixture_id}.tsv").read_text() == render(fx)


def test_goldens_directory_has_no_stray_files():
    assert {p.name for p in GOLDENS.glob("*.tsv")} == {
        f"{fx.fixture_id}.tsv" for fx in EXPORTED}


def test_naf_is_refused():
    with pytest.raises(NotFactual):
        render(NAF)


def test_diamond_golden_carries_two_inherited_modes_for_one_holding():
    text = (GOLDENS / "F1-modes.tsv").read_text()
    assert "atom\tholds(p,d)\n" in text
    assert "atom\tholds_via(inherited(a),p,d)\n" in text
    assert "atom\tholds_via(inherited(b),p,d)\n" in text
