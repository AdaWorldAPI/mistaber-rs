"""Domain-neutral fixtures for the Mistaber Kripke-rule oracle.

Fixtures are authored here as plain fact tuples, not copied from upstream.
`render()` turns them into ASP text for Clingo; the scalar interpreter reads
the tuples directly, so the two oracles share no parser.

World names are AUTHORITY / INTERPRETATION scopes. Taxonomic `is_a` edges
are content facts and are never rendered as `accessible/2` (see
`adapter.taxon_edge_to_accessible`, which refuses).
"""

from __future__ import annotations

from dataclasses import dataclass, field

Fact = tuple[str, ...]


@dataclass(frozen=True)
class Fixture:
    fixture_id: str
    facts: tuple[Fact, ...]
    # Extra ASP rules (content program or deliberately non-stratified input).
    # The scalar interpreter refuses any fixture that carries rules.
    rules: tuple[str, ...] = ()
    # Evidence lineage: rule id -> origin evidence id. Absent = unknown.
    lineage: dict[str, str] = field(default_factory=dict)

    def render(self, order: list[int] | None = None) -> str:
        idx = order if order is not None else list(range(len(self.facts)))
        lines = [f"{f[0]}({', '.join(f[1:])})." for f in (self.facts[i] for i in idx)]
        return "\n".join(lines + list(self.rules)) + "\n"


def _worlds(*ws: str) -> list[Fact]:
    return [("world", w) for w in ws]


# F1: assertion / endorsement / inheritance / override / diamond / chain /
# provenance gap, all on one proposition `p` plus a provenance-less `g`.
MODES = Fixture(
    "F1-modes",
    tuple(
        _worlds("base", "a", "b", "c", "d", "e")
        + [
            ("asserts", "base", "p"),
            ("asserts_rule", "base", "p", "r_base_p"),
            ("accessible", "a", "base"),
            ("accessible", "b", "base"),
            ("endorses", "b", "p"),
            ("endorses_rule", "b", "p", "r_b_endorse"),
            ("accessible", "c", "base"),
            ("override", "c", "p", "q"),
            ("accessible", "d", "a"),
            ("accessible", "d", "b"),
            ("accessible", "e", "d"),
            # g is asserted with no asserts_rule companion: a provenance gap.
            ("asserts", "base", "g"),
        ]
    ),
    # b's endorsement re-affirms the same origin observation (a copy).
    lineage={"r_base_p": "ev_F", "r_b_endorse": "ev_F"},
)

# F1-reversed: the same graph with one accessibility edge flipped. Used as
# a negative control: its normalized output must NOT equal F1's.
MODES_REVERSED = Fixture(
    "F1-reversed",
    tuple(
        ("accessible", "base", "a") if f == ("accessible", "a", "base") else f
        for f in MODES.facts
    ),
    lineage=MODES.lineage,
)

# F2: an accessibility cycle with no assertion. Nothing may hold
# (no self-supporting inheritance).
CYCLE = Fixture(
    "F2-cycle",
    tuple(
        _worlds("x", "y", "z")
        + [
            ("accessible", "x", "y"),
            ("accessible", "y", "x"),
            ("accessible", "z", "x"),
            ("asserts", "z", "t"),
            ("asserts_rule", "z", "t", "r_z_t"),
        ]
    ),
)

# F5: input that is legal but not self-consistent. A rule companion with no
# assertion (r_orphan) and an assertion in a world nobody declared (ghost).
# Upstream derives holds_via_rule(asserted, p, base, ...) but no holds(p, _),
# and nothing from ghost. A native fixpoint must not let either propagate.
GATES = Fixture(
    "F5-gates",
    tuple(
        _worlds("base", "a")
        + [
            ("accessible", "a", "base"),
            ("asserts_rule", "base", "p", "r_orphan"),
            ("accessible", "a", "ghost"),
            ("asserts", "ghost", "h"),
            ("asserts_rule", "ghost", "h", "r_ghost"),
        ]
    ),
)

# F3: even negative cycle over asserts/2 (legal upstream: asserts is
# cwa=false, safe_negation). Two stable models; brave != cautious.
NAF = Fixture(
    "F3-naf",
    tuple(_worlds("m", "n") + [("accessible", "n", "m")]),
    rules=(
        "asserts(m, x1) :- not asserts(m, x2).",
        "asserts(m, x2) :- not asserts(m, x1).",
    ),
)

# --- Mammal fixture (C1..C10) ---------------------------------------------
# Taxonomy and traits live in a stratified CONTENT program that reads the
# observations holding in one designated reader interpretation.
TAXONOMY_PROGRAM = (
    "is_a(monotreme, mammal). is_a(therian, mammal).",
    "is_a(marsupial, therian). is_a(placental, therian).",
    "instance(wombat, marsupial). instance(possum, marsupial).",
    "instance(whale, placental). instance(fox, placental).",
    "instance(elephant, placental). instance(platypus, monotreme).",
    "member(X, T) :- instance(X, T).",
    "member(X, P) :- member(X, T), is_a(T, P).",
    "produces_milk(X) :- member(X, mammal).",
    "lays_eggs(X) :- holds(lays_eggs(X), reader).",
    "-live_birth(X) :- lays_eggs(X).",
    # Scoped default: therians give live birth unless explicitly excepted.
    "live_birth(X) :- member(X, therian), not -live_birth(X).",
)

# Deliberately unsound broad default, used only as a falsifier.
UNSOUND_DEFAULT = "live_birth(X) :- member(X, mammal), not -live_birth(X)."


def mammal(stage: str, *, unsound: bool = False) -> Fixture:
    """Stages: C2 = no reproductive evidence; C4 = egg-laying observed by
    obs1; C6 = obs2 endorses obs1 (copy); C6i = obs3 observes independently."""
    facts: list[Fact] = _worlds("obs1", "obs2", "obs3", "reader")
    facts += [
        ("accessible", "obs2", "obs1"),
        ("accessible", "reader", "obs2"),
        ("accessible", "reader", "obs3"),
    ]
    lineage: dict[str, str] = {}
    if stage in ("C4", "C6", "C6i"):
        facts += [
            ("asserts", "obs1", "lays_eggs(platypus)"),
            ("asserts_rule", "obs1", "lays_eggs(platypus)", "r_obs1"),
        ]
        lineage["r_obs1"] = "ev_obs1_field_notes"
    if stage in ("C6", "C6i"):
        facts += [
            ("endorses", "obs2", "lays_eggs(platypus)"),
            ("endorses_rule", "obs2", "lays_eggs(platypus)", "r_obs2_endorse"),
        ]
        lineage["r_obs2_endorse"] = "ev_obs1_field_notes"  # copied, not new
    if stage == "C6i":
        facts += [
            ("asserts", "obs3", "lays_eggs(platypus)"),
            ("asserts_rule", "obs3", "lays_eggs(platypus)", "r_obs3"),
        ]
        lineage["r_obs3"] = "ev_obs3_specimen"
    rules = TAXONOMY_PROGRAM + ((UNSOUND_DEFAULT,) if unsound else ())
    return Fixture(f"C-mammal-{stage}{'-unsound' if unsound else ''}",
                   tuple(facts), rules=rules, lineage=lineage)


# --- Gate E: shared XLOG relational fixture -------------------------------
R = [(1, 2), (1, 3), (9, 7)]
S = [(2, 4), (3, 5), (7, 4)]
SOURCE_REVISION = "xlog-fixture-v0"


def xlog_join(curated_override: bool) -> Fixture:
    facts: list[Fact] = _worlds("src", "curated")
    facts.append(("accessible", "curated", "src"))
    lineage = {}
    for i, (a, b) in enumerate(R):
        rid = f"r_R_{i}"
        facts += [("asserts", "src", f"r({a},{b})"),
                  ("asserts_rule", "src", f"r({a},{b})", rid)]
        lineage[rid] = f"ev_{SOURCE_REVISION}_R_{i}"
    for i, (a, b) in enumerate(S):
        rid = f"r_S_{i}"
        facts += [("asserts", "src", f"s({a},{b})"),
                  ("asserts_rule", "src", f"s({a},{b})", rid)]
        lineage[rid] = f"ev_{SOURCE_REVISION}_S_{i}"
    if curated_override:
        facts.append(("override", "curated", "r(1,2)", "retracted"))
    rules = (
        "ans(W, Y) :- holds(r(1,Y), W), holds(s(Y,4), W).",
    )
    return Fixture(f"E-xlog-{'override' if curated_override else 'plain'}",
                   tuple(facts), rules=rules, lineage=lineage)
