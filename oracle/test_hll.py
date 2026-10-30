"""HLL front-end tests: fixture F1 written in HLL and compiled by the pinned
upstream compiler (emitter.py ASPEmitter.emit).

Hypothesis tested (direction ASSERTED: it HOLDS): an `asserts(w, p).` FACT
inside an `@rule` block gets NO `asserts_rule` companion (facts are emitted at
emitter.py lines 269-271, outside the companion loop at lines 280-304), so it
holds at runtime with no holds_via_rule/5 and `qualified` raises
MissingProvenance. The same atom written as a RULE (`:- world(base)`) does
get the companion. If the upstream emitter changes, test_fact_in_rule_block_*
fails and the hypothesis must be re-examined.

Run: MISTABER_UPSTREAM=<mistaber checkout @ pinned commit> pytest oracle/
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

from clingo_oracle import solve  # noqa: E402
from fixtures import MODES  # noqa: E402
from hll_oracle import compile_fixture, solve_hll  # noqa: E402
from qualify import MissingProvenance, Truth, qualified, truth  # noqa: E402


def test_compiled_text_has_world_structure_and_endorse_companion():
    text, _ = compile_fixture("modes")
    lines = set(text.splitlines())
    assert "world(d)." in lines
    assert "accessible(d, a)." in lines
    assert "accessible(d, b)." in lines
    assert "endorses_rule(b, p, r_endorse_b_0)." in lines


def test_rule_form_gets_asserts_rule_and_diamond_has_two_derivations():
    atoms = solve_hll("modes").models[0]
    assert "holds_via_rule(asserted,p,base,r_base_p,r_base_p)" in atoms
    srcs = {h.source_rule for h in qualified(atoms, "p", "d")}
    assert srcs == {"r_base_p", "r_endorse_b_0"}


def test_override_blocks_p_and_does_not_introduce_q():
    r = solve_hll("modes")
    assert truth("holds(p,c)", r.models) is Truth.UNKNOWN
    assert truth("holds(q,c)", r.models) is Truth.UNKNOWN
    assert "holds(p,c)" not in r.models[0] and "holds(q,c)" not in r.models[0]


def test_fact_in_rule_block_has_no_companion_so_provenance_is_missing():
    text, _ = compile_fixture("modes")
    # Mechanism: the fact is emitted, but no asserts_rule line follows it.
    assert "asserts(base, g)." in text.splitlines()
    assert not any(l.startswith("asserts_rule(base, g") for l in text.splitlines())
    # Symptom: it holds downstream yet cannot be attributed to a rule.
    atoms = solve_hll("modes").models[0]
    assert "holds(g,d)" in atoms
    with pytest.raises(MissingProvenance):
        qualified(atoms, "g", "d")


def test_parity_with_hand_written_fixture_on_rule_id_free_predicates():
    # holds_via_rule/5 is excluded: it carries rule ids, and the hand fixture
    # names the endorsement r_b_endorse while the compiler synthesizes
    # r_endorse_b_0. holds/2 and holds_via/3 carry no rule ids.
    names = frozenset({"holds", "holds_via"})
    hll = solve_hll("modes").project(names)
    hand = solve(MODES).project(names)
    assert len(hll) == len(hand) == 1
    assert hll == hand


def test_compiled_sha_is_deterministic():
    (t1, s1), (t2, s2) = compile_fixture("modes"), compile_fixture("modes")
    assert t1 == t2 and s1 == s2
    assert solve_hll("modes").witness.fixture_sha256 == s1
    assert solve_hll("modes").witness.fixture_id == "hll-modes"
