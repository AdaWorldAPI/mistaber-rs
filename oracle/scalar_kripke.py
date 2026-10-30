"""Independent scalar interpreter for the fact-only fragment of the upstream
Kripke holding rules (`kripke_rules.hll` @ the pinned commit).

It shares no code with Clingo: it reads fixture tuples, not ASP text, and
computes the least fixpoint by plain iteration. It refuses any fixture that
carries rules, because rules may introduce non-stratified negation that a
single fixpoint cannot represent.

Stratification argument for the accepted fragment: the only negated literals
in the holding rules are over `asserts/2`, `endorses/2` and `overridden/2`,
which are input relations (or derived from the input `override/3`), plus the
`holding_strength(weak, ...)` rule, which negates strong/moderate holdings
that are computed in a lower stratum.
"""

from __future__ import annotations

from fixtures import Fixture


class RefusedInput(Exception):
    """Input outside the admitted stratified, fact-only fragment."""


def interpret(fixture: Fixture) -> frozenset[str]:
    if fixture.rules:
        raise RefusedInput(f"{fixture.fixture_id}: rules present; fact-only fragment only")
    rel: dict[str, set[tuple[str, ...]]] = {}
    for f in fixture.facts:
        rel.setdefault(f[0], set()).add(tuple(f[1:]))
    world = {w for (w,) in rel.get("world", set())}
    asserts = rel.get("asserts", set())
    endorses = rel.get("endorses", set())
    accessible = rel.get("accessible", set())
    overridden = {(p, w) for (w, p, _r) in rel.get("override", set())}
    a_rule = rel.get("asserts_rule", set())
    e_rule = rel.get("endorses_rule", set())

    via: set[tuple[str, str, str]] = set()  # (mode, prop, world)
    via |= {("asserted", p, w) for (w, p) in asserts if w in world}
    via |= {("endorsed", p, w) for (w, p) in endorses if w in world}
    holds = {(p, w) for (_m, p, w) in via}
    changed = True
    while changed:
        changed = False
        for (child, parent) in accessible:
            for (p, w) in list(holds):
                if w != parent:
                    continue
                if (p, child) in overridden or (child, p) in asserts or (child, p) in endorses:
                    continue
                t = (f"inherited({parent})", p, child)
                if t not in via:
                    via.add(t)
                    holds.add((p, child))
                    changed = True

    strong = {(p, w) for (m, p, w) in via if m in ("asserted", "endorsed")}
    moderate = set()
    for (m, p, w) in via:
        if m.startswith("inherited("):
            parent = m[len("inherited("):-1]
            if (w, parent) in accessible and (
                ("asserted", p, parent) in via or ("endorsed", p, parent) in via
            ):
                moderate.add((p, w))
    weak = {(p, w) for (m, p, w) in via if m.startswith("inherited(")} - strong - moderate

    source = {(p, w, w) for (p, w) in strong}
    changed = True
    while changed:
        changed = False
        for (m, p, w) in via:
            if not m.startswith("inherited("):
                continue
            parent = m[len("inherited("):-1]
            for (p2, w2, o) in list(source):
                if p2 == p and w2 == parent and (p, w, o) not in source:
                    source.add((p, w, o))
                    changed = True

    vrule: set[tuple[str, str, str, str, str]] = set()
    vrule |= {("asserted", p, w, r, r) for (w, p, r) in a_rule if w in world}
    vrule |= {("endorsed", p, w, r, r) for (w, p, r) in e_rule if w in world}
    changed = True
    while changed:
        changed = False
        for (m, p, w) in via:
            if not m.startswith("inherited("):
                continue
            parent = m[len("inherited("):-1]
            for (_m2, p2, w2, _i, src) in list(vrule):
                t = (m, p, w, "r_kripke_inherit", src)
                if p2 == p and w2 == parent and t not in vrule:
                    vrule.add(t)
                    changed = True

    out: set[str] = set()
    out |= {f"holds({p},{w})" for (p, w) in holds}
    out |= {f"holds_via({m},{p},{w})" for (m, p, w) in via}
    out |= {f"holding_strength(strong,{p},{w})" for (p, w) in strong}
    out |= {f"holding_strength(moderate,{p},{w})" for (p, w) in moderate}
    out |= {f"holding_strength(weak,{p},{w})" for (p, w) in weak}
    out |= {f"inheritance_source({p},{w},{o})" for (p, w, o) in source}
    out |= {f"overridden({p},{w})" for (p, w) in overridden}
    out |= {f"holds_via_rule({m},{p},{w},{i},{s})" for (m, p, w, i, s) in vrule}
    return frozenset(out)
