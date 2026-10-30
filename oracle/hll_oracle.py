"""HLL front end for the oracle: compile a `.hll` fixture with the pinned
upstream compiler, then solve it together with the pinned Kripke rules.

The compiler is imported from `$MISTABER_UPSTREAM`; nothing is vendored.
"""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path

import clingo

from clingo_oracle import OracleResult
from witness import UPSTREAM_COMMIT, Witness, load_kripke_rules, require_pinned_compiler

HLL_DIR = Path(__file__).parent / "hll"


def compile_fixture(name: str) -> tuple[str, str]:
    """Compile hll/<name>.hll. Returns (ASP text, sha256 of that text)."""
    root = str(require_pinned_compiler())
    if root not in sys.path:
        sys.path.insert(0, root)
    from mistaber.dsl.compiler import compile_hll_file  # noqa: E402

    text = compile_hll_file(HLL_DIR / f"{name}.hll")
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()


def solve_hll(name: str) -> OracleResult:
    rules_text, lp_sha = load_kripke_rules()
    text, text_sha = compile_fixture(name)
    witness = Witness(UPSTREAM_COMMIT, lp_sha, f"hll-{name}", text_sha)
    ctl = clingo.Control(["0", "--warn=none"])
    ctl.add("base", [], rules_text)
    ctl.add("base", [], text)
    ctl.ground([("base", [])])
    models: list[frozenset[str]] = []
    with ctl.solve(yield_=True) as handle:
        for model in handle:
            models.append(frozenset(str(s).replace(" ", "")
                                    for s in model.symbols(atoms=True)))
    models.sort(key=lambda m: sorted(m))
    return OracleResult(witness, tuple(models))
