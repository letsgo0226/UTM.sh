#!/usr/bin/env python3
"""UTM Principle-Vector Layer v0.1.

Formal/metaphysical model only. This module does not assert that chakras,
complex phases, chronons, or ACIM terminology are empirically measured
physical entities.

Towel Principle  -> proper attribution / type separation
Secret Principle -> admissibility / validation
Immortality      -> invariant equivalence under admissible transformation
Chronon          -> model-time step with |delta_tau| = 1 and direction +/-1
IFR              -> maximize lawful transformation while preserving invariant
"""

from __future__ import annotations

from cmath import exp
from dataclasses import dataclass
from math import isclose, isfinite, pi
from typing import Any, Dict, Optional, Tuple

TAU = 2.0 * pi
EPS = 1e-9
FORMAL_SCOPE = "formal-metaphysical-model"


def canonical_phase(theta: float) -> float:
    """Reduce an angle to (-pi, pi]."""
    p = (theta + pi) % TAU - pi
    return pi if isclose(p, -pi, abs_tol=EPS) else p


@dataclass(frozen=True)
class ComplexNode:
    real: float
    phase: float

    def as_complex(self) -> complex:
        return complex(self.real, self.phase)


@dataclass(frozen=True)
class PrincipleVectorState:
    tick: int
    tau: int
    towel: ComplexNode
    secret: ComplexNode
    admitted: bool = True
    ontology_type: str = "formal-model"
    scope: str = FORMAL_SCOPE
    empirical_claim: bool = False

    @property
    def z(self) -> complex:
        return self.towel.as_complex() + self.secret.as_complex()

    @property
    def existential_image(self) -> complex:
        """exp(x+y) = exp(x) * exp(y)."""
        return exp(self.z)

    @property
    def phase_class(self) -> float:
        return canonical_phase(self.z.imag)

    @property
    def equivalence_class(self) -> Tuple[float, float]:
        """Canonical representative of z modulo 2*pi*i."""
        return (round(self.z.real, 12), round(self.phase_class, 12))

    @property
    def peace(self) -> bool:
        """Formal phase-coherence predicate; not an empirical measurement."""
        return self.admitted and isclose(self.phase_class, 0.0, abs_tol=EPS)

    def to_record(self) -> Dict[str, Any]:
        e = self.existential_image
        return {
            "protocol": "UTM-Principle-Vector/0.1",
            "scope": self.scope,
            "empirical_claim": self.empirical_claim,
            "tick": self.tick,
            "tau": self.tau,
            "towel": {"real": self.towel.real, "phase": self.towel.phase},
            "secret": {"real": self.secret.real, "phase": self.secret.phase},
            "z": {"real": self.z.real, "imag": self.z.imag},
            "phase_class": self.phase_class,
            "existential_image": {"real": e.real, "imag": e.imag},
            "equivalence_class": list(self.equivalence_class),
            "admitted": self.admitted,
            "peace": self.peace,
            "ontology_type": self.ontology_type,
        }


def towel_check(state: PrincipleVectorState) -> bool:
    """Fail closed on category confusion or unsupported ontology tags."""
    return (
        state.scope == FORMAL_SCOPE
        and state.empirical_claim is False
        and state.ontology_type in {
            "formal-model",
            "simulation",
            "symbolic-metaphysics",
        }
    )


def secret_check(state: PrincipleVectorState) -> bool:
    """Minimal admissibility gate for v0.1."""
    values = (
        state.towel.real,
        state.towel.phase,
        state.secret.real,
        state.secret.phase,
    )
    return (
        towel_check(state)
        and state.admitted is True
        and state.tick >= 0
        and all(isinstance(v, (int, float)) and isfinite(v) for v in values)
    )


def immortality_check(before: PrincipleVectorState, after: PrincipleVectorState) -> bool:
    """Preserve z modulo 2*pi*i across an admissible transition."""
    return before.equivalence_class == after.equivalence_class


def chronon_step(
    state: PrincipleVectorState,
    direction: int,
    *,
    towel: Optional[ComplexNode] = None,
    secret: Optional[ComplexNode] = None,
) -> PrincipleVectorState:
    if direction not in (-1, 1):
        raise ValueError("chronon direction must be -1 or +1")
    candidate = PrincipleVectorState(
        tick=state.tick + 1,
        tau=state.tau + direction,
        towel=towel or state.towel,
        secret=secret or state.secret,
        admitted=state.admitted,
        ontology_type=state.ontology_type,
        scope=state.scope,
        empirical_claim=state.empirical_claim,
    )
    if not secret_check(candidate):
        raise ValueError("Secret Principle rejected candidate state")
    return candidate


def validate_transition(before: PrincipleVectorState, after: PrincipleVectorState) -> bool:
    """Observe-only validation. It does not mutate an authoritative UTM state."""
    return (
        secret_check(before)
        and secret_check(after)
        and after.tick == before.tick + 1
        and abs(after.tau - before.tau) == 1
        and immortality_check(before, after)
    )


def ifr_score(before: PrincipleVectorState, after: PrincipleVectorState) -> Dict[str, Any]:
    """A non-optimizing diagnostic: lawful change + zero invariant loss."""
    representation_change = abs(after.z - before.z)
    invariant_preserved = immortality_check(before, after)
    return {
        "representation_change": representation_change,
        "invariant_preserved": invariant_preserved,
        "lawful_transition": validate_transition(before, after),
        "interpretation": "maximum lawful transformation with zero invariant loss",
    }


def _demo() -> None:
    s0 = PrincipleVectorState(
        tick=0,
        tau=0,
        towel=ComplexNode(1.0, pi / 4),
        secret=ComplexNode(2.0, -pi / 4),
    )
    s1 = chronon_step(
        s0,
        +1,
        towel=ComplexNode(1.0, pi / 4 + TAU),
    )
    assert validate_transition(s0, s1)
    print(s0.to_record())
    print(s1.to_record())
    print(ifr_score(s0, s1))


if __name__ == "__main__":
    _demo()
