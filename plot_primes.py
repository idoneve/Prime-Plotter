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
    print("Directory cleaned succesfully...\n")

    if os.path.exists("all_primes.csv"):
        os.remove("all_primes.csv")
    if os.path.exists("primes"):
        print("Removing primes directory...")
        shutil.rmtree("primes")
        print("Primes directory successfully removed")
    print("Program Completed")
    return True


def compile_c_program():
    print("Compiling C program...")
    result = subprocess.run(["make", "parallel_build"], capture_output=True, text=True)
    if result.returncode != 0:
        print("Failed to compile C with make all")
        return False
    print("C program compliled succesfully...\n")
    return True


def run_c_program(processes, threads, iterations, start_num):
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


def load_prime_data(processes, threads, iterations, start_num):
    if (
        not clean_directory()
        or not compile_c_program()
        or not run_c_program(processes, threads, iterations, start_num)
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


def plot_primes(primes, gaps, large_scale_toggle):
    fig, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    if not large_scale_toggle:
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
        axes[0].set_xscale("log")
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
            s=10,
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

    if len(argv) != 6:
        print("Incorrect number of args received (expected 1 or 5)\n")
        print(
            'Create plot usage\n - python plot_primes.py <processes> <threads> <iterations> <start_num> <large_scale_toggle> ("(t)rue" if running large values)'
        )
        print(
            "Clean directory usage\n - python plot_primes.py clean (to clean directory)\n"
        )
        return

    large_scale_toggle = True if argv[5][0] == "t" else False
    df = load_prime_data(np.int64(argv[1]), np.int64(argv[2]), np.int64(argv[3]), np.int64(argv[4]))
    if df is not None:
        primes = np.array(df["prime"])
        gaps = np.diff(primes)

        print(f"Range: {df['prime'].min()} to {df['prime'].max()} ({df['prime'].max() - df['prime'].min()})\n")
        print(f"Total primes found {len(df)}")
        print(f"Total twin primes found {len(gaps[gaps==2])}")
        print(f"Largest gap between primes found {max(gaps)}\n")
        print(
            (
                df.groupby(["process", "thread"]).size().reset_index(name="prime_count")
            ).to_string(index=False)
        )

        plot_primes(primes, gaps, large_scale_toggle)
    else:
        print("Failed to find prime data")
        return
    print("\nProgram Completed")


if __name__ == "__main__":
    main()
