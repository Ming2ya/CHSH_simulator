"""Core routines for Bell-state CHSH Monte Carlo experiments.

The project uses the polarization-photon convention:

    |+_theta> = cos(theta)|0> + sin(theta)|1>
    |-_theta> = -sin(theta)|0> + cos(theta)|1>

For |Phi+>, this gives E(theta_a, theta_b) = cos(2(theta_a - theta_b)).
"""

from __future__ import annotations

from dataclasses import dataclass
from math import radians, sqrt
from typing import Dict, Iterable, Mapping

import numpy as np


OUTCOMES = ("++", "+-", "-+", "--")
BELL_STATE_NAMES = ("phi_plus", "phi_minus", "psi_plus", "psi_minus")


@dataclass(frozen=True)
class MeasurementResult:
    pair: str
    theta_a_deg: float
    theta_b_deg: float
    shots: int
    probabilities: Mapping[str, float]
    counts: Mapping[str, int]
    e_sim: float
    e_theory: float

    @property
    def error(self) -> float:
        return self.e_sim - self.e_theory


@dataclass(frozen=True)
class ChshResult:
    bell_state: str
    shots: int
    seed: int | None
    measurements: tuple[MeasurementResult, ...]
    s_sim: float
    s_theory: float

    @property
    def error(self) -> float:
        return self.s_sim - self.s_theory

    @property
    def violates_classical_bound(self) -> bool:
        return abs(self.s_sim) > 2.0


def prepare_bell_state(name: str) -> np.ndarray:
    """Prepare one of the four Bell states from |00> using simple gates."""
    if name not in BELL_STATE_NAMES:
        raise ValueError(
            f"Unknown Bell state {name!r}. Choose one of {BELL_STATE_NAMES}."
        )

    zero_zero = np.array([1.0, 0.0, 0.0, 0.0], dtype=complex)
    identity = np.eye(2, dtype=complex)
    hadamard = np.array([[1.0, 1.0], [1.0, -1.0]], dtype=complex) / sqrt(2.0)
    pauli_x = np.array([[0.0, 1.0], [1.0, 0.0]], dtype=complex)
    pauli_z = np.array([[1.0, 0.0], [0.0, -1.0]], dtype=complex)
    cnot = np.array(
        [
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
            [0.0, 0.0, 1.0, 0.0],
        ],
        dtype=complex,
    )

    phi_plus = cnot @ np.kron(hadamard, identity) @ zero_zero
    if name == "phi_plus":
        return phi_plus
    if name == "phi_minus":
        return np.kron(identity, pauli_z) @ phi_plus
    if name == "psi_plus":
        return np.kron(identity, pauli_x) @ phi_plus
    return np.kron(identity, pauli_x @ pauli_z) @ phi_plus


def assert_normalized(state: np.ndarray, tolerance: float = 1e-10) -> None:
    norm = float(np.vdot(state, state).real)
    if abs(norm - 1.0) > tolerance:
        raise ValueError(f"State is not normalized: norm={norm:.12f}")


def polarization_basis(theta_rad: float) -> tuple[np.ndarray, np.ndarray]:
    plus = np.array([np.cos(theta_rad), np.sin(theta_rad)], dtype=complex)
    minus = np.array([-np.sin(theta_rad), np.cos(theta_rad)], dtype=complex)
    return plus, minus


def joint_probabilities(
    state: np.ndarray,
    theta_a_deg: float,
    theta_b_deg: float,
    tolerance: float = 1e-10,
) -> Dict[str, float]:
    """Return P(++), P(+-), P(-+), P(--) for polarization measurements."""
    assert_normalized(state, tolerance=tolerance)

    theta_a = radians(theta_a_deg)
    theta_b = radians(theta_b_deg)
    plus_a, minus_a = polarization_basis(theta_a)
    plus_b, minus_b = polarization_basis(theta_b)

    projectors = {
        "++": np.kron(plus_a, plus_b),
        "+-": np.kron(plus_a, minus_b),
        "-+": np.kron(minus_a, plus_b),
        "--": np.kron(minus_a, minus_b),
    }
    probabilities = {
        outcome: float(abs(np.vdot(projector, state)) ** 2)
        for outcome, projector in projectors.items()
    }
    total = sum(probabilities.values())
    if abs(total - 1.0) > tolerance:
        raise ValueError(
            f"Joint probabilities are not normalized for angles "
            f"({theta_a_deg}, {theta_b_deg}): total={total:.12f}"
        )
    return {key: value / total for key, value in probabilities.items()}


def expectation_from_distribution(distribution: Mapping[str, float | int]) -> float:
    same = float(distribution["++"]) + float(distribution["--"])
    different = float(distribution["+-"]) + float(distribution["-+"])
    total = same + different
    if total <= 0:
        raise ValueError("Cannot compute expectation from an empty distribution.")
    return (same - different) / total


def sample_counts(
    probabilities: Mapping[str, float],
    shots: int,
    rng: np.random.Generator,
) -> Dict[str, int]:
    if shots <= 0:
        raise ValueError("shots must be a positive integer.")

    probability_vector = np.array([probabilities[outcome] for outcome in OUTCOMES])
    sampled = rng.multinomial(shots, probability_vector)
    return {outcome: int(count) for outcome, count in zip(OUTCOMES, sampled)}


def measure_pair(
    state: np.ndarray,
    pair: str,
    theta_a_deg: float,
    theta_b_deg: float,
    shots: int,
    rng: np.random.Generator,
) -> MeasurementResult:
    probabilities = joint_probabilities(state, theta_a_deg, theta_b_deg)
    counts = sample_counts(probabilities, shots, rng)
    return MeasurementResult(
        pair=pair,
        theta_a_deg=theta_a_deg,
        theta_b_deg=theta_b_deg,
        shots=shots,
        probabilities=probabilities,
        counts=counts,
        e_sim=expectation_from_distribution(counts),
        e_theory=expectation_from_distribution(probabilities),
    )


def default_chsh_angles() -> Dict[str, float]:
    return {"a": 0.0, "ap": 45.0, "b": 22.5, "bp": -22.5}


def run_chsh(
    shots: int,
    seed: int | None = 42,
    angles: Mapping[str, float] | None = None,
    bell: str = "phi_plus",
) -> ChshResult:
    """Run the default CHSH experiment for a selected Bell state."""
    selected_angles = dict(default_chsh_angles() if angles is None else angles)
    required = {"a", "ap", "b", "bp"}
    missing = required.difference(selected_angles)
    if missing:
        raise ValueError(f"Missing CHSH angle labels: {sorted(missing)}")

    state = prepare_bell_state(bell)
    rng = np.random.default_rng(seed)
    pairs = (
        ("a_b", selected_angles["a"], selected_angles["b"]),
        ("a_bp", selected_angles["a"], selected_angles["bp"]),
        ("ap_b", selected_angles["ap"], selected_angles["b"]),
        ("ap_bp", selected_angles["ap"], selected_angles["bp"]),
    )
    measurements = tuple(
        measure_pair(state, pair, theta_a, theta_b, shots, rng)
        for pair, theta_a, theta_b in pairs
    )
    by_pair = {measurement.pair: measurement.e_sim for measurement in measurements}
    by_pair_theory = {
        measurement.pair: measurement.e_theory for measurement in measurements
    }
    s_sim = by_pair["a_b"] + by_pair["a_bp"] + by_pair["ap_b"] - by_pair["ap_bp"]
    s_theory = (
        by_pair_theory["a_b"]
        + by_pair_theory["a_bp"]
        + by_pair_theory["ap_b"]
        - by_pair_theory["ap_bp"]
    )
    return ChshResult(
        bell_state=bell,
        shots=shots,
        seed=seed,
        measurements=measurements,
        s_sim=float(s_sim),
        s_theory=float(s_theory),
    )


def run_convergence(
    shot_values: Iterable[int],
    seed: int | None = 42,
    bell: str = "phi_plus",
) -> tuple[ChshResult, ...]:
    """Run CHSH experiments for multiple shot counts with deterministic seeds."""
    shot_values = tuple(shot_values)
    seed_sequence = np.random.SeedSequence(seed)
    child_sequences = seed_sequence.spawn(len(shot_values))
    results = []
    for shots, child_sequence in zip(shot_values, child_sequences):
        child_seed = int(child_sequence.generate_state(1)[0])
        results.append(run_chsh(shots=shots, seed=child_seed, bell=bell))
    return tuple(results)
