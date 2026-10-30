"""Interpretation-qualified readings over oracle output, with typed refusals.

Nothing here computes holdings. It reads atoms produced by the Clingo or the
scalar oracle and answers: under which interpretation, by which mode, from
which immediate and source rule, and how many independent evidence origins.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum


class MissingProvenance(Exception):
    """A holding exists but no holds_via_rule/5 attributes it to a rule."""


class UnknownIndependence(Exception):
    """A source rule has no evidence-lineage entry, so independence is unknown."""


class CategoryError(Exception):
    """A mapping between two semantically different relations was requested."""


class Truth(Enum):
    TRUE = "true"            # in every stable model (cautious)
    FALSE = "false"          # explicit classical negation in every model
    BRAVE_ONLY = "brave"     # true in some stable models, not all
    UNKNOWN = "unknown"      # neither the atom nor its negation is entailed


def truth(atom: str, models: tuple[frozenset[str], ...]) -> Truth:
    neg = "-" + atom
    if models and all(atom in m for m in models):
        return Truth.TRUE
    if models and all(neg in m for m in models):
        return Truth.FALSE
    if any(atom in m for m in models):
        return Truth.BRAVE_ONLY
    return Truth.UNKNOWN


_VRULE = re.compile(r"^holds_via_rule\((.*)\)$")


def _split_args(s: str) -> list[str]:
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch == "," and depth == 0:
            out.append(cur)
            cur = ""
            continue
        depth += ch == "("
        depth -= ch == ")"
        cur += ch
    out.append(cur)
    return out


@dataclass(frozen=True)
class QualifiedHolding:
    proposition: str
    interpretation: str
    holding_mode: str
    immediate_rule: str
    source_rule: str


def qualified(atoms: frozenset[str], prop: str, world: str) -> list[QualifiedHolding]:
    out = []
    for a in atoms:
        m = _VRULE.match(a)
        if not m:
            continue
        mode, p, w, imm, src = _split_args(m.group(1))
        if p == prop and w == world:
            out.append(QualifiedHolding(p, w, mode, imm, src))
    # Every observed holding mode must be attributed. A partial list would
    # understate the evidence set (one diamond path attributed, one not).
    modes = set()
    for a in atoms:
        if a.startswith("holds_via(") and a.endswith(")"):
            mode, p, w = _split_args(a[len("holds_via("):-1])
            if p == prop and w == world:
                modes.add(mode)
    uncovered = modes - {h.holding_mode for h in out}
    if uncovered:
        raise MissingProvenance(
            f"holds({prop},{world}): no holds_via_rule/5 for modes {sorted(uncovered)}")
    return sorted(out, key=lambda h: (h.holding_mode, h.source_rule))


def evidence_origins(
    holdings: list[QualifiedHolding], lineage: dict[str, str]
) -> frozenset[str]:
    """Distinct origin-evidence ids behind the holdings. Two derivation paths
    or an endorsement that trace to the same origin count once."""
    origins = set()
    for h in holdings:
        if h.source_rule not in lineage:
            raise UnknownIndependence(f"no lineage for source rule {h.source_rule}")
        origins.add(lineage[h.source_rule])
    return frozenset(origins)


def naive_authority_agreement(atoms: frozenset[str], prop: str) -> int:
    """The WRONG count, kept as a falsifier: every world that asserts or
    endorses `prop` is treated as an independent witness."""
    return sum(
        1 for a in atoms
        if a.startswith(("holds_via(asserted,", "holds_via(endorsed,"))
        and _split_args(a[len("holds_via("):-1])[1] == prop
    )


# --- Mappings that must never be made implicitly --------------------------

def taxon_edge_to_accessible(child: str, parent: str) -> str:
    raise CategoryError(
        f"is_a({child},{parent}) is taxonomy; accessible/2 is authority "
        "inheritance. Map explicitly per fixture, never by default."
    )


def strength_to_epi5(level: str) -> int:
    raise CategoryError(
        f"holding_strength({level}) is an authority-derivation class, not an "
        "EpistemicState5 code; Epi5 values come only from its own contract."
    )


def is_a_to_pearl3(child: str, parent: str) -> int:
    raise CategoryError(
        f"is_a({child},{parent}) carries no intervention evidence; Pearl3 "
        "(CE64 bits 40..42) is not set by taxonomy."
    )
