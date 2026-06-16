"""Command-line entry point for the MVP CHSH Monte Carlo experiment."""

from __future__ import annotations

import argparse
import csv
import os
import tempfile
from math import sqrt
from pathlib import Path

os.environ.setdefault(
    "MPLCONFIGDIR",
    str(Path(tempfile.gettempdir()) / "chsh_matplotlib"),
)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from src.chsh import ChshResult, run_chsh, run_convergence


DEFAULT_CONVERGENCE_SHOTS = (100, 500, 1000, 5000, 10000, 50000)


def parse_shot_list(raw: str) -> tuple[int, ...]:
    values = []
    for chunk in raw.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        value = int(chunk)
        if value <= 0:
            raise argparse.ArgumentTypeError("All shot counts must be positive.")
        values.append(value)
    if not values:
        raise argparse.ArgumentTypeError("At least one shot count is required.")
    return tuple(values)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Monte Carlo CHSH verification for the |Phi+> Bell state."
    )
    parser.add_argument("--shots", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--convergence-shots",
        type=parse_shot_list,
        default=DEFAULT_CONVERGENCE_SHOTS,
        help="Comma-separated shot counts for the convergence plot.",
    )
    parser.add_argument("--no-plot", action="store_true")
    return parser


def ensure_output_dirs() -> None:
    Path("results").mkdir(exist_ok=True)
    Path("figures").mkdir(exist_ok=True)


def print_result(result: ChshResult) -> None:
    print("Bell state: Phi+")
    print("Measurement convention: polarization basis")
    print(f"Shots: {result.shots}")
    print(f"Seed: {result.seed}")
    print()
    print(f"{'Pair':<8} {'E_sim':>10} {'E_theory':>10} {'Error':>10}")
    for measurement in result.measurements:
        print(
            f"{measurement.pair:<8} "
            f"{measurement.e_sim:>10.6f} "
            f"{measurement.e_theory:>10.6f} "
            f"{measurement.error:>10.6f}"
        )
    print()
    print(f"{'S_sim':<12}{result.s_sim:.6f}")
    print(f"{'S_theory':<12}{result.s_theory:.6f}")
    print(f"{'2sqrt(2)':<12}{2 * sqrt(2):.6f}")
    print(
        f"Classical bound violated: "
        f"{'yes' if result.violates_classical_bound else 'no'}"
    )


def write_summary_csv(result: ChshResult, path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(
            [
                "pair",
                "theta_a_deg",
                "theta_b_deg",
                "shots",
                "n_pp",
                "n_pm",
                "n_mp",
                "n_mm",
                "e_sim",
                "e_theory",
                "error",
            ]
        )
        for measurement in result.measurements:
            writer.writerow(
                [
                    measurement.pair,
                    measurement.theta_a_deg,
                    measurement.theta_b_deg,
                    measurement.shots,
                    measurement.counts["++"],
                    measurement.counts["+-"],
                    measurement.counts["-+"],
                    measurement.counts["--"],
                    f"{measurement.e_sim:.10f}",
                    f"{measurement.e_theory:.10f}",
                    f"{measurement.error:.10f}",
                ]
            )
        writer.writerow(
            [
                "S",
                "",
                "",
                result.shots,
                "",
                "",
                "",
                "",
                f"{result.s_sim:.10f}",
                f"{result.s_theory:.10f}",
                f"{result.error:.10f}",
            ]
        )


def write_convergence_csv(results: tuple[ChshResult, ...], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["shots", "seed", "s_sim", "s_theory", "error"])
        for result in results:
            writer.writerow(
                [
                    result.shots,
                    result.seed,
                    f"{result.s_sim:.10f}",
                    f"{result.s_theory:.10f}",
                    f"{result.error:.10f}",
                ]
            )


def plot_convergence(results: tuple[ChshResult, ...], path: Path) -> None:
    shots = [result.shots for result in results]
    s_values = [result.s_sim for result in results]
    theory = 2 * sqrt(2)

    plt.figure(figsize=(8, 5))
    plt.plot(shots, s_values, marker="o", label="Monte Carlo S")
    plt.axhline(2.0, color="tab:red", linestyle="--", label="Classical bound = 2")
    plt.axhline(
        theory,
        color="tab:green",
        linestyle=":",
        label=r"Quantum value = $2\sqrt{2}$",
    )
    plt.xscale("log")
    plt.xlabel("Shots")
    plt.ylabel("CHSH S")
    plt.title("CHSH convergence for |Phi+>")
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.shots <= 0:
        parser.error("--shots must be a positive integer.")

    ensure_output_dirs()

    result = run_chsh(shots=args.shots, seed=args.seed)
    print_result(result)
    write_summary_csv(result, Path("results/chsh_mvp_summary.csv"))

    convergence_results = run_convergence(args.convergence_shots, seed=args.seed)
    write_convergence_csv(
        convergence_results,
        Path("results/chsh_mvp_convergence.csv"),
    )
    if not args.no_plot:
        plot_convergence(
            convergence_results,
            Path("figures/chsh_mvp_convergence.png"),
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
