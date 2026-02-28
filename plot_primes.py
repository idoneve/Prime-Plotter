import glob
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import shutil
import subprocess
from sys import argv


def clean_directory():
    print("Cleaning up directory...")
    result = subprocess.run(args=["make", "clean"], capture_output=True, text=True)
    if result.returncode != 0:
        print("Failed to clean directory with make clean")
        return False
    print("Directory cleaned succesfully")
    return True


def compile_c_program():
    print("Compiling C program...")
    result = subprocess.run(["make", "parallel_build"], capture_output=True, text=True)
    if result.returncode != 0:
        print("Failed to compile C with make all")
        return False
    print("C program compliled succesfully...\n")
    return True


def run_c_program(processes, threads, iterations, start_num, benchmark_toggle=False):
    if benchmark_toggle:
        print(
            f"Running benchmark on prime finder with {processes} processes, {threads} threads, range {iterations}, start {start_num}..."
        )
        result = subprocess.run(
            [
                "make",
                "benchmark",
                f"ARGS={processes} {threads} {iterations} {start_num}",
            ],
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print("Failed to run C program with benchmark")
            return False
        print("C program and benchmark ran successfully\n")

        print("=== Timing Results ===")
        print(result.stderr)
        print("======================\n")
    else:
        print(
            f"Running prime finder with {processes} processes, {threads} threads, range {iterations}, start {start_num}..."
        )
        result = subprocess.run(
            ["./a.out", str(processes), str(threads), str(iterations), str(start_num)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print("Failed to run C program")
            return False
        print("C program ran successfully...\n")
    return True


def load_prime_data(processes, threads, iterations, start_num, benchmark_toggle=False):
    if (
        not clean_directory()
        or not compile_c_program()
        or not run_c_program(
            processes, threads, iterations, start_num, benchmark_toggle
        )
    ):
        return None

    files = glob.glob("primes/*.csv")
    if not files:
        print("Failed to find any prime files")
        return None

    df = pd.concat(
        [pd.read_csv(f, names=["process", "thread", "prime"]) for f in files]
    ).sort_values("prime")
    df.to_csv("all_primes.csv", index=False)
    return df


def plot_primes(primes, gaps, large_toggle):
    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    if not large_toggle:
        axes[0].scatter(
            primes,
            np.array([i for i in range(len(primes))]),
            s=30,
            c=primes,
            cmap="twilight",
            marker="o",
            alpha=0.9,
        )

        axes[1].scatter(
            primes[1:],
            gaps,
            s=30,
            c=primes[1:],
            cmap="twilight",
            marker="o",
            alpha=0.8,
        )
    else:
        axes[0].scatter(
            primes,
            np.array([i for i in range(len(primes))]),
            s=30,
            c="purple",
            marker=".",
            alpha=0.7,
        )
        axes[1].set_yscale("log")
        axes[1].scatter(
            primes[1:],
            gaps,
            s=30,
            c="purple",
            marker=".",
            alpha=0.3,
        )

    # axes[0].set_xlabel("Numbers")
    axes[0].set_ylabel("Primes")
    axes[0].set_title(f"{len(primes)} Primes")
    axes[0].grid(True, alpha=0.3)

    axes[1].set_xlabel("Numbers")
    axes[1].set_ylabel("Gap to Next Prime")
    # axes[1].set_title("Prime Gaps")
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.show()


def main():
    if len(argv) == 2 and argv[1] == "clean":
        clean_directory()
        return

    if (
        len(argv) != 5
        and len(argv) != 6
        and len(argv) != 7
        and len(argv) != 8
        and len(argv) != 9
    ):
        print("Incorrect number of args received\n")
        print(
            'Create plot usage\n - python plot_primes.py [-b | --benchmark] [-v | --verbose] [-l | --large] [-np | --no_plot] s<processes> <threads> <iterations> <start_num> <large_toggle> ("(t)rue" if running large values)'
        )
        print(
            "Clean directory usage\n - python plot_primes.py clean (to clean directory)\n"
        )
        return

    no_plot = False
    if "--no_plot" in argv or "-np" in argv:
        argv.remove("--no_plot") if "--no_plot" in argv else argv.remove("-np")
        no_plot = True
    large_toggle = False
    if "--large" in argv or "-l" in argv:
        argv.remove("--large") if "--large" in argv else argv.remove("-l")
        large_toggle = True
    verbose = False
    if "--verbose" in argv or "-v" in argv:
        argv.remove("--verbose") if "--verbose" in argv else argv.remove("-v")
        verbose = True
    if "--benchmark" in argv or "-b" in argv:
        argv.remove("--benchmark") if "--benchmark" in argv else argv.remove("-b")
        df = load_prime_data(
            np.int64(argv[1]),
            np.int64(argv[2]),
            np.int64(argv[3]),
            np.int64(argv[4]),
            True,
        )
    else:
        df = load_prime_data(
            np.int64(argv[1]),
            np.int64(argv[2]),
            np.int64(argv[3]),
            np.int64(argv[4]),
        )

    if df is not None:
        primes = np.array(df["prime"])
        gaps = np.diff(primes)
        twin_primes = gaps[gaps == 2]

        print(
            f"Range: {df['prime'].min()} to {df['prime'].max()} ({df['prime'].max() - df['prime'].min()})\n"
        )
        print(f"Total primes found {len(df)}")
        print(
            f"Percentage of numbers that are primes {100 * len(primes) / (primes[-1] - primes[0]):.3f}%"
        )
        print(
            f"Standard Deviation {np.sqrt(np.average(primes ** 2) / np.average(primes) ** 2):.3f}\n"
        )
        print(f"Total twin primes found {len(twin_primes)}")
        print(
            f"Percentage of primes that are twin primes {100 * len(twin_primes) / (primes[-1] - primes[0]):.3f}%\n"
        )
        print(f"Largest gap between primes found {max(gaps)}")
        print(f"Average prime gap {np.average(gaps):.3f}")
        print(
            f"Standard Deviation {np.sqrt(np.average(gaps ** 2) / np.average(gaps) ** 2):.3f}"
        )

        if verbose:
            print()
            print(
                (
                    df.groupby(["process", "thread"])
                    .size()
                    .reset_index(name="prime_count")
                ).to_string(index=False)
            )

        if not no_plot:
            plot_primes(primes, gaps, large_toggle)
    else:
        print("Failed to find prime data")
        return
    print("\nProgram completed")


if __name__ == "__main__":
    main()
