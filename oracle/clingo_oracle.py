"""Clingo reference oracle over the pinned upstream Kripke rules.

Every stable model is kept. `brave` is the union of the models, `cautious`
their intersection; a single model is never used as the answer.
"""

from __future__ import annotations

from dataclasses import dataclass

import clingo

from fixtures import Fixture
from witness import Witness, fixture_digest, load_kripke_rules, UPSTREAM_COMMIT

KRIPKE_PREDICATES = frozenset(
    {
        "holds",
        "holds_via",
        "holds_via_rule",
        "holding_strength",
        "inheritance_source",
        "overridden",
    }
)


@dataclass(frozen=True)
class OracleResult:
    witness: Witness
    models: tuple[frozenset[str], ...]

    @property
    def brave(self) -> frozenset[str]:
        out: set[str] = set()
        for m in self.models:
            out |= m
        return frozenset(out)

    @property
    def cautious(self) -> frozenset[str]:
        if not self.models:
            return frozenset()
        out = set(self.models[0])
        for m in self.models[1:]:
            out &= m
        return frozenset(out)

    def project(self, names: frozenset[str]) -> tuple[frozenset[str], ...]:
        return tuple(
            frozenset(a for a in m if a.lstrip("-").split("(", 1)[0] in names)
            for m in self.models
        )


def solve(fixture: Fixture, order: list[int] | None = None) -> OracleResult:
    rules_text, lp_sha = load_kripke_rules()
    fixture_text = fixture.render(order)
    # The witness is keyed on the fixture CONTENT, not its row order, so a
    # permissible reordering keeps the witness and must keep the answer.
    canonical = fixture.render(None)
    witness = Witness(UPSTREAM_COMMIT, lp_sha, fixture.fixture_id,
                      fixture_digest(canonical))
    ctl = clingo.Control(["0", "--warn=none"])
    ctl.add("base", [], rules_text)
    ctl.add("base", [], fixture_text)
    ctl.ground([("base", [])])
    models: list[frozenset[str]] = []
    with ctl.solve(yield_=True) as handle:
        for model in handle:
            models.append(frozenset(str(s).replace(" ", "")
                                    for s in model.symbols(atoms=True)))
    models.sort(key=lambda m: sorted(m))
    return OracleResult(witness, tuple(models))
