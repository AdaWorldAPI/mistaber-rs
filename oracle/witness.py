"""Source and version witnesses for the Mistaber reference oracle.

The oracle never vendors upstream code. It reads the generated Kripke rules
from a pinned upstream checkout and refuses to run when the bytes differ from
the pin. A result bundle carries the witness it was produced under; bundles
with different witnesses are never compared.
"""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from pathlib import Path

UPSTREAM_REPO = "BrainyBlaze/mistaber"
UPSTREAM_COMMIT = "b50bf3323056793830c35795eace57e43caa23b5"
KRIPKE_LP_PATH = "mistaber/ontology/worlds/kripke_rules.lp"
KRIPKE_HLL_PATH = "mistaber/dsl/worlds/kripke_rules.hll"
# sha256 of the committed generated file (with its 4-line header).
KRIPKE_LP_SHA256 = "6c55720475add0f81915c46a84da8146235cee38dffa0db73e72a7bf0e58a9e9"
KRIPKE_HLL_SHA256 = "df9020899dd02c8a0049fa264d855bb820fdf8b70378284a08b8cdda00de4fe8"


class StaleWitness(Exception):
    """The reference bytes or the fixture differ from the pinned witness."""


@dataclass(frozen=True)
class Witness:
    upstream_commit: str
    kripke_lp_sha256: str
    fixture_id: str
    fixture_sha256: str

    def require_same(self, other: "Witness") -> None:
        if self != other:
            raise StaleWitness(f"witness mismatch: {self} != {other}")


def upstream_root() -> Path:
    root = os.environ.get("MISTABER_UPSTREAM")
    if not root:
        raise StaleWitness(
            "set MISTABER_UPSTREAM to a checkout of "
            f"{UPSTREAM_REPO}@{UPSTREAM_COMMIT}"
        )
    return Path(root)


def load_kripke_rules(expected_sha256: str = KRIPKE_LP_SHA256) -> tuple[str, str]:
    """Return (program text, sha256). Refuse if the bytes are not the pin."""
    data = (upstream_root() / KRIPKE_LP_PATH).read_bytes()
    digest = hashlib.sha256(data).hexdigest()
    if digest != expected_sha256:
        raise StaleWitness(
            f"{KRIPKE_LP_PATH}: sha256 {digest} != pinned {expected_sha256}"
        )
    return data.decode("utf-8"), digest


def fixture_digest(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
