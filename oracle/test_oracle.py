"""Differential oracle tests: upstream Kripke rules under Clingo vs the
independent scalar interpreter, plus the source-qualification falsifiers.

Run: MISTABER_UPSTREAM=<mistaber checkout @ pinned commit> pytest oracle/
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent))

import qualify  # noqa: E402
from clingo_oracle import KRIPKE_PREDICATES, solve  # noqa: E402
from fixtures import (  # noqa: E402
    CYCLE, MODES, MODES_REVERSED, NAF, R, S, mammal, xlog_join,
)
from qualify import (  # noqa: E402
    CategoryError, MissingProvenance, Truth, UnknownIndependence,
    evidence_origins, naive_authority_agreement, qualified, truth,
)
from scalar_kripke import RefusedInput, interpret  # noqa: E402
from witness import StaleWitness, load_kripke_rules  # noqa: E402


# --- Gate F: differential parity ------------------------------------------

@pytest.mark.parametrize("fx", [MODES, MODES_REVERSED, CYCLE], ids=lambda f: f.fixture_id)
def test_scalar_matches_clingo_exactly(fx):
    r = solve(fx)
    assert len(r.models) == 1
    assert r.project(KRIPKE_PREDICATES)[0] == interpret(fx)


def test_reversed_edge_changes_the_answer():
    # Parity holds for both orientations, but they must not agree with each
    # other: orientation is load-bearing.
    good = solve(MODES).project(KRIPKE_PREDICATES)[0]
    bad = solve(MODES_REVERSED).project(KRIPKE_PREDICATES)[0]
    assert "holds(p,a)" in good and "holds(p,a)" not in bad
    assert good != bad


def test_cycle_has_no_self_support():
    atoms = solve(CYCLE).models[0]
    assert {a for a in atoms if a.startswith("holds(")} == {"holds(t,z)"}
    assert "holds(t,x)" not in atoms and "holds(t,y)" not in atoms
    assert "holds(t,z)" in atoms


# --- Holding modes, override, provenance ------------------------------------

def test_modes_are_kept_distinct():
    a = solve(MODES).models[0]
    assert "holds_via(inherited(base),p,a)" in a
    assert "holds_via(endorsed,p,b)" in a
    assert "holds_via(inherited(base),p,b)" not in a  # endorsement blocks inheritance
    assert "holding_strength(weak,p,e)" in a


def test_override_blocks_without_entailing_replacement():
    a = solve(MODES).models[0]
    assert "overridden(p,c)" in a
    assert "holds(p,c)" not in a
    assert "holds(q,c)" not in a  # override(c,p,q) does not assert q
    assert "holds(g,c)" in a       # override is per-proposition


def test_diamond_keeps_both_derivations_with_origins():
    hs = qualified(solve(MODES).models[0], "p", "d")
    assert [(h.holding_mode, h.immediate_rule, h.source_rule) for h in hs] == [
        ("inherited(a)", "r_kripke_inherit", "r_base_p"),
        ("inherited(b)", "r_kripke_inherit", "r_b_endorse"),
    ]


def test_provenance_gap_is_refused_not_silent():
    # Upstream: holds_via_rule/5 needs an asserts_rule/3 companion. Without
    # it, g holds everywhere and is attributed to no rule.
    atoms = solve(MODES).models[0]
    assert "holds(g,d)" in atoms
    with pytest.raises(MissingProvenance):
        qualified(atoms, "g", "d")


# --- Source independence (C6/C7, Gate G) -------------------------------------

def test_diamond_with_copied_endorsement_is_one_origin():
    atoms = solve(MODES).models[0]
    hs = qualified(atoms, "p", "d")
    assert evidence_origins(hs, MODES.lineage) == {"ev_F"}
    assert naive_authority_agreement(atoms, "p") == 2  # the wrong count


def test_endorsement_does_not_become_independent_evidence():
    copied = mammal("C6")
    indep = mammal("C6i")
    a6 = solve(copied).models[0]
    a6i = solve(indep).models[0]
    prop = "lays_eggs(platypus)"
    assert naive_authority_agreement(a6, prop) == 2
    assert evidence_origins(qualified(a6, prop, "reader"), copied.lineage) == {
        "ev_obs1_field_notes"}
    assert evidence_origins(qualified(a6i, prop, "reader"), indep.lineage) == {
        "ev_obs1_field_notes", "ev_obs3_specimen"}


def test_missing_lineage_is_unknown_independence():
    fx = mammal("C6")
    hs = qualified(solve(fx).models[0], "lays_eggs(platypus)", "reader")
    with pytest.raises(UnknownIndependence):
        evidence_origins(hs, {})


def test_disabling_lineage_dedupe_is_detected(monkeypatch):
    """Load-bearing disable: counting source RULES instead of lineage origins
    must make the copied-endorsement case report two witnesses."""
    def by_rule(holdings, lineage):
        return frozenset(h.source_rule for h in holdings)
    monkeypatch.setattr(qualify, "evidence_origins", by_rule)
    hs = qualify.qualified(solve(MODES).models[0], "p", "d")
    assert len(qualify.evidence_origins(hs, MODES.lineage)) == 2


# --- Mammal sequence C1..C5, defaults and OWA -------------------------------

def test_mammal_sequence():
    q = "live_birth(platypus)"
    c2 = solve(mammal("C2")).models
    assert truth("member(platypus,mammal)", c2) is Truth.TRUE
    assert truth("produces_milk(platypus)", c2) is Truth.TRUE
    assert truth("lays_eggs(platypus)", c2) is Truth.UNKNOWN  # not FALSE
    assert truth(q, c2) is Truth.UNKNOWN
    assert truth("live_birth(wombat)", c2) is Truth.TRUE
    c4 = solve(mammal("C4")).models
    assert truth(q, c4) is Truth.FALSE
    assert truth("member(platypus,mammal)", c4) is Truth.TRUE  # survives exception


def test_unsound_broad_default_is_caught_by_the_reference_table():
    # Ground truth (MIST-EPI5-0): platypus does not give live birth. A
    # mammal-wide default asserts it while evidence is still missing.
    m = solve(mammal("C2", unsound=True)).models
    assert truth("live_birth(platypus)", m) is Truth.TRUE


# --- Stable models and refusals ---------------------------------------------

def test_naf_keeps_every_stable_model():
    r = solve(NAF)
    assert len(r.models) == 2
    held = {a for a in r.brave if a.startswith("holds(")}
    assert held == {"holds(x1,m)", "holds(x2,m)", "holds(x1,n)", "holds(x2,n)"}
    assert not {a for a in r.cautious if a.startswith("holds(")}
    assert truth("holds(x1,n)", r.models) is Truth.BRAVE_ONLY


def test_scalar_refuses_rules():
    with pytest.raises(RefusedInput):
        interpret(NAF)


@pytest.mark.parametrize("seed", [1, 2, 3])
def test_row_reordering_keeps_answer_and_witness(seed):
    order = list(range(len(MODES.facts)))
    random.Random(seed).shuffle(order)
    base, shuffled = solve(MODES), solve(MODES, order)
    base.witness.require_same(shuffled.witness)
    assert base.models == shuffled.models


def test_stale_reference_bytes_are_refused():
    with pytest.raises(StaleWitness):
        load_kripke_rules(expected_sha256="0" * 64)


def test_witnesses_of_different_fixtures_do_not_compare():
    with pytest.raises(StaleWitness):
        solve(mammal("C4")).witness.require_same(solve(mammal("C6")).witness)


@pytest.mark.parametrize("call", [
    lambda: qualify.taxon_edge_to_accessible("platypus", "monotreme"),
    lambda: qualify.strength_to_epi5("moderate"),
    lambda: qualify.is_a_to_pearl3("monotreme", "mammal"),
])
def test_category_mappings_are_refused(call):
    with pytest.raises(CategoryError):
        call()


# --- Gate E: shared XLOG fixture --------------------------------------------

def test_xlog_join_answer_and_qualification():
    expected = {y for (x, y) in R if x == 1 for (y2, z) in S if y2 == y and z == 4}
    assert expected == {2}
    plain = solve(xlog_join(False))
    assert {a for a in plain.cautious if a.startswith("ans(src,")} == {"ans(src,2)"}
    # Same answer under the inheriting interpretation, via inheritance.
    assert "ans(curated,2)" in plain.cautious
    hs = qualified(plain.models[0], "r(1,2)", "curated")
    assert [(h.holding_mode, h.source_rule) for h in hs] == [("inherited(src)", "r_R_0")]
    # Override removes applicability in curated only.
    over = solve(xlog_join(True))
    assert "ans(curated,2)" not in over.cautious and "ans(src,2)" in over.cautious
    # An absent premise is unknown, not false.
    assert truth("holds(s(3,4),src)", plain.models) is Truth.UNKNOWN
