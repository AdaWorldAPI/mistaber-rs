"""Export the Clingo oracle's answers as golden files for native probes.

One TSV per fixture: a provenance header, the input facts, and the derived
Kripke atoms of the single stable model. A native implementation reads the
facts, computes, and must reproduce the atoms exactly; it never needs Python
or Clingo.

Refused at export, never approximated:
- a fixture whose extra rules derive a Kripke INPUT predicate (F3-naf's even
  negative cycle over asserts/2): its answer is not one fixpoint of the facts;
- a fixture with more than one stable model.

Run: MISTABER_UPSTREAM=<mistaber checkout @ pinned commit> \
     python3 oracle/export_goldens.py <out-dir>
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from clingo_oracle import KRIPKE_PREDICATES, solve  # noqa: E402
from fixtures import CYCLE, MODES, MODES_REVERSED, NAF, Fixture, mammal, xlog_join  # noqa: E402
from witness import require_pinned_compiler  # noqa: E402

# Predicates the Kripke rules read. A fixture rule that derives one of these
# makes the input non-factual.
KRIPKE_INPUTS = frozenset({
    "world", "asserts", "endorses", "accessible", "override",
    "asserts_rule", "endorses_rule",
})

EXPORTED = (
    MODES, MODES_REVERSED, CYCLE,
    mammal("C2"), mammal("C4"), mammal("C6"), mammal("C6i"),
    xlog_join(False), xlog_join(True),
)
REFUSED = (NAF,)


class NotFactual(Exception):
    """The fixture's rules derive a Kripke input predicate."""


def _head_predicate(rule: str) -> str:
    head = rule.split(":-", 1)[0].strip().lstrip("-")
    m = re.match(r"[a-z_][A-Za-z0-9_]*", head)
    return m.group(0) if m else ""


def render(fx: Fixture) -> str:
    for r in fx.rules:
        if _head_predicate(r) in KRIPKE_INPUTS:
            raise NotFactual(f"{fx.fixture_id}: rule derives {_head_predicate(r)}: {r}")
    res = solve(fx)
    if len(res.models) != 1:
        raise NotFactual(f"{fx.fixture_id}: {len(res.models)} stable models")
    w = res.witness
    lines = [
        f"# fixture\t{w.fixture_id}",
        f"# upstream_commit\t{w.upstream_commit}",
        f"# kripke_lp_sha256\t{w.kripke_lp_sha256}",
        f"# fixture_sha256\t{w.fixture_sha256}",
    ]
    lines += ["fact\t" + "\t".join(f) for f in fx.facts]
    lines += ["atom\t" + a for a in sorted(res.project(KRIPKE_PREDICATES)[0])]
    return "\n".join(lines) + "\n"


def main(out: Path) -> None:
    require_pinned_compiler()
    out.mkdir(parents=True, exist_ok=True)
    for fx in EXPORTED:
        (out / f"{fx.fixture_id}.tsv").write_text(render(fx))
    for fx in REFUSED:
        try:
            render(fx)
        except NotFactual:
            continue
        raise SystemExit(f"{fx.fixture_id} was expected to be refused")


if __name__ == "__main__":
    main(Path(sys.argv[1]))
