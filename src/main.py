"""Command-line entry point for the MVP CHSH Monte Carlo experiment."""

from __future__ import annotations

import argparse
import csv
from math import sqrt
from pathlib import Path

from src.chsh import (
    AngleScanResult,
    BELL_STATE_NAMES,
    ChshResult,
    run_angle_scan,
    run_chsh,
    run_convergence,
    run_noise_scan,
)


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
        description="Monte Carlo CHSH verification for Bell states."
    )
    parser.add_argument("--shots", type=int, default=10000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument(
        "--bell",
        default="phi_plus",
        choices=BELL_STATE_NAMES,
        help="Bell state to simulate.",
    )
    parser.add_argument(
        "--visibility",
        type=float,
        default=1.0,
        help="Visibility of the Bell state before measurement.",
    )
    parser.add_argument(
        "--convergence-shots",
        type=parse_shot_list,
        default=DEFAULT_CONVERGENCE_SHOTS,
        help="Comma-separated shot counts for the convergence plot.",
    )
    parser.add_argument(
        "--angle-scan",
        action="store_true",
        help="Also scan b=theta, b'=-theta and save an angle scan figure.",
    )
    parser.add_argument("--scan-start", type=float, default=0.0)
    parser.add_argument("--scan-stop", type=float, default=45.0)
    parser.add_argument("--scan-points", type=int, default=91)
    parser.add_argument(
        "--scan-shots",
        type=int,
        default=None,
        help="Shots per angle-scan point. Defaults to --shots.",
    )
    parser.add_argument(
        "--noise-scan",
        action="store_true",
        help="Also scan visibility noise and save a noise figure.",
    )
    parser.add_argument("--noise-start", type=float, default=0.0)
    parser.add_argument("--noise-stop", type=float, default=1.0)
    parser.add_argument("--noise-points", type=int, default=101)
    parser.add_argument(
        "--noise-shots",
        type=int,
        default=None,
        help="Shots per noise-scan point. Defaults to --shots.",
    )
    parser.add_argument("--no-plot", action="store_true")
    return parser


def ensure_output_dirs() -> None:
    Path("results").mkdir(exist_ok=True)
    Path("figures").mkdir(exist_ok=True)


def print_result(result: ChshResult) -> None:
    print(f"Bell state: {result.bell_state}")
    print(f"Visibility: {result.visibility}")
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
        writer = csv.writer(csv_file, lineterminator="\n")
        writer.writerow(
            [
                "pair",
                "bell_state",
                "visibility",
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
                    result.bell_state,
                    result.visibility,
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
                result.bell_state,
                result.visibility,
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
        writer = csv.writer(csv_file, lineterminator="\n")
        writer.writerow(
            ["bell_state", "visibility", "shots", "seed", "s_sim", "s_theory", "error"]
        )
        for result in results:
            writer.writerow(
                [
                    result.bell_state,
                    result.visibility,
                    result.shots,
                    result.seed,
                    f"{result.s_sim:.10f}",
                    f"{result.s_theory:.10f}",
                    f"{result.error:.10f}",
                ]
            )


def write_angle_scan_csv(results: tuple[AngleScanResult, ...], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, lineterminator="\n")
        writer.writerow(
            [
                "bell_state",
                "visibility",
                "theta_deg",
                "shots",
                "seed",
                "s_sim",
                "s_theory",
                "error",
            ]
        )
        for scan_result in results:
            result = scan_result.result
            writer.writerow(
                [
                    result.bell_state,
                    result.visibility,
                    f"{scan_result.theta_deg:.10f}",
                    result.shots,
                    result.seed,
                    f"{result.s_sim:.10f}",
                    f"{result.s_theory:.10f}",
                    f"{result.error:.10f}",
                ]
            )


def write_noise_scan_csv(results: tuple[ChshResult, ...], path: Path) -> None:
    with path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, lineterminator="\n")
        writer.writerow(
            ["bell_state", "visibility", "shots", "seed", "s_sim", "s_theory", "error"]
        )
        for result in results:
            writer.writerow(
                [
                    result.bell_state,
                    f"{result.visibility:.10f}",
                    result.shots,
                    result.seed,
                    f"{result.s_sim:.10f}",
                    f"{result.s_theory:.10f}",
                    f"{result.error:.10f}",
                ]
            )


def plot_convergence(results: tuple[ChshResult, ...], path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

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
    bell_state = results[0].bell_state if results else "unknown"
    plt.title(f"CHSH convergence for {bell_state}")
    plt.grid(True, which="both", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def plot_angle_scan(results: tuple[AngleScanResult, ...], path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    theta_values = [result.theta_deg for result in results]
    s_sim = [result.s_sim for result in results]
    s_theory = [result.s_theory for result in results]
    bell_state = results[0].result.bell_state if results else "unknown"
    theory_bound = 2 * sqrt(2)
    optimal_theta = -22.5 if bell_state in {"phi_minus", "psi_plus"} else 22.5

    plt.figure(figsize=(8, 5))
    plt.plot(theta_values, s_theory, label="Theory S", color="tab:blue")
    plt.scatter(theta_values, s_sim, s=14, alpha=0.7, label="Monte Carlo S")
    plt.axhline(2.0, color="tab:red", linestyle="--", label="Classical bounds")
    plt.axhline(-2.0, color="tab:red", linestyle="--")
    plt.axhline(
        theory_bound,
        color="tab:green",
        linestyle=":",
        label=r"Quantum bounds",
    )
    plt.axhline(-theory_bound, color="tab:green", linestyle=":")
    plt.axvline(
        optimal_theta,
        color="tab:gray",
        linestyle="--",
        label=f"optimal theta = {optimal_theta:g} deg",
    )
    plt.xlabel("theta (deg), with b=theta and b'=-theta")
    plt.ylabel("CHSH S")
    plt.title(f"CHSH angle scan for {bell_state}")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def plot_noise_scan(results: tuple[ChshResult, ...], path: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    visibility_values = [result.visibility for result in results]
    s_sim = [result.s_sim for result in results]
    s_theory = [result.s_theory for result in results]
    bell_state = results[0].bell_state if results else "unknown"
    threshold = 1 / sqrt(2)

    plt.figure(figsize=(8, 5))
    plt.plot(visibility_values, s_theory, label="Theory S", color="tab:blue")
    plt.scatter(visibility_values, s_sim, s=14, alpha=0.7, label="Monte Carlo S")
    plt.axhline(2.0, color="tab:red", linestyle="--", label="Classical bound = 2")
    plt.axvline(
        threshold,
        color="tab:gray",
        linestyle="--",
        label=r"$v = 1/\sqrt{2}$",
    )
    plt.xlabel("visibility v")
    plt.ylabel("CHSH S")
    plt.title(f"CHSH noise scan for {bell_state}")
    plt.grid(True, alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(path, dpi=180)
    plt.close()


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    if args.shots <= 0:
        parser.error("--shots must be a positive integer.")
    if not 0.0 <= args.visibility <= 1.0:
        parser.error("--visibility must be between 0 and 1.")
    if args.scan_points < 2:
        parser.error("--scan-points must be at least 2.")
    if args.scan_shots is not None and args.scan_shots <= 0:
        parser.error("--scan-shots must be a positive integer.")
    if args.noise_points < 2:
        parser.error("--noise-points must be at least 2.")
    if args.noise_shots is not None and args.noise_shots <= 0:
        parser.error("--noise-shots must be a positive integer.")

    ensure_output_dirs()

    result = run_chsh(
        shots=args.shots,
        seed=args.seed,
        bell=args.bell,
        visibility=args.visibility,
    )
    print_result(result)
    write_summary_csv(result, Path("results/chsh_mvp_summary.csv"))

    convergence_results = run_convergence(
        args.convergence_shots,
        seed=args.seed,
        bell=args.bell,
        visibility=args.visibility,
    )
    write_convergence_csv(
        convergence_results,
        Path("results/chsh_mvp_convergence.csv"),
    )
    if not args.no_plot:
        plot_convergence(
            convergence_results,
            Path("figures/chsh_mvp_convergence.png"),
        )

    if args.angle_scan:
        scan_results = run_angle_scan(
            start_deg=args.scan_start,
            stop_deg=args.scan_stop,
            points=args.scan_points,
            shots=args.scan_shots or args.shots,
            seed=args.seed,
            bell=args.bell,
            visibility=args.visibility,
        )
        write_angle_scan_csv(scan_results, Path("results/chsh_angle_scan.csv"))
        if not args.no_plot:
            plot_angle_scan(scan_results, Path("figures/chsh_angle_scan.png"))

    if args.noise_scan:
        noise_results = run_noise_scan(
            start=args.noise_start,
            stop=args.noise_stop,
            points=args.noise_points,
            shots=args.noise_shots or args.shots,
            seed=args.seed,
            bell=args.bell,
        )
        write_noise_scan_csv(noise_results, Path("results/chsh_noise_scan.csv"))
        if not args.no_plot:
            plot_noise_scan(noise_results, Path("figures/chsh_noise_scan.png"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
