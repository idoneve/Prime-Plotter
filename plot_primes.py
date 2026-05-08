import glob
import math
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import subprocess
import sys
import datashader as ds
import datashader.transfer_functions as tf


def compile_c_program():
    print("Compiling C program...")
    result = subprocess.run(["make", "parallel_build"], capture_output=True, text=True)
    if result.returncode != 0:
        print("Failed to compile C with make parallel_build")
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
            print(result.stderr)
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
            print(result.stderr)
            return False
        print("C program ran successfully...\n")
    return True


def clean_directory():
    print("Cleaning up directory...")
    result = subprocess.run(args=["make", "clean"], capture_output=True, text=True)
    if result.returncode != 0:
        print("Failed to clean directory with make clean")
        return False
    print("Directory cleaned succesfully")
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
    dfs = []
    for f in files:
        basename = os.path.basename(f)
        parts = basename.replace(".csv", "").split("_")
        p_id = int(parts[0][1:])
        t_id = int(parts[1][1:])

        df = pd.read_csv(f, header=None, names=["prime"])
        df["process"] = p_id
        df["thread"] = t_id
        dfs.append(df)
    df = pd.concat(dfs).sort_values("prime")
    np.save("all_primes.npy", df["prime"].to_numpy(dtype=np.uint64))
    df.to_csv("all_primes.csv", index=False)
    return df


def plot_primes(primes, gaps, log_toggle, save_only=False):
    _, axes = plt.subplots(2, 1, figsize=(10, 6), sharex=True)
    if not log_toggle:
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

    axes[0].set_ylabel("Primes")
    axes[0].set_title(f"{len(primes)} Primes")
    axes[0].grid(True, alpha=0.3)

    axes[1].set_xlabel("Numbers")
    axes[1].set_ylabel("Gap to Next Prime")
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig("primes.png", dpi=200, bbox_inches="tight")
    if not save_only:
        plt.show()
    else:
        plt.close()


def plot_ulam_datashader(primes, save_only=False, n=3000):
    primes_set = set(primes)
    x_coords = []
    y_coords = []

    cx = cy = n // 2
    dx, dy = 1, 0
    step = 1
    steps_taken = 0
    legs_completed = 0
    x, y = cx, cy
    for i in range(1, n * n + 1):
        if 0 <= x < n and 0 <= y < n:
            if i in primes_set:
                x_coords.append(x)
                y_coords.append(y)
        if steps_taken == step:
            dx, dy = -dy, dx
            steps_taken = 0
            legs_completed += 1
            if legs_completed == 2:
                step += 1
                legs_completed = 0
        x += dx
        y += dy
        steps_taken += 1
    df = pd.DataFrame({"x": x_coords, "y": y_coords})
    cvs = ds.Canvas(
        plot_width=n,
        plot_height=n,
        x_range=(-0.5, n - 0.5),
        y_range=(-0.5, n - 0.5)
    )
    agg = cvs.points(df, "x", "y", agg=ds.count())
    img = tf.shade(agg, cmap=["white", "black"], how="linear")
    tf.set_background(img, "white")

    _, ax = plt.subplots(figsize=(10, 10))
    ax.imshow(img.to_pil(), aspect="equal", origin="upper")
    ax.set_title(f"Ulam Spiral — {len(primes):,} Primes")
    ax.axis("off")

    if not save_only:
        plt.show()
    ds.utils.export_image(img, "ulam_spiral", background="white")


def check_all_args(argv):
    if len(argv) == 2 and argv[1] == "clean":
        clean_directory()
        return False
    if not (5 <= len(argv) and len(argv) <= 10):
        print("Incorrect number of args received\n")
        print(
            "Create plot usage\n - python plot_primes.py [-b | --benchmark] [-v | --verbose] [-l | --large] [-g | --logarithmic] [-np | --no_plot] <processes> <threads> <iterations> <start_num>"
        )
        print(
            "Clean directory usage\n - python plot_primes.py clean (to clean directory)\n"
        )
        return False
    return True


def get_flags(argv):
    if not check_all_args(argv):
        return

    new_argv = []
    for arg in argv:
        if arg.startswith("-") and len(arg) > 2:
            new_argv.extend(f"-{c}" for c in arg[1:])
        else:
            new_argv.append(arg)
    return new_argv


def check_args(argv):
    if len(argv) != 5:
        print("Incorrect number of args received\n")
        print(
            "Create plot usage\n - python plot_primes.py [-b | --benchmark] [-v | --verbose] [-l | --large] [-g | --logarithmic] [-np | --no_plot] <processes> <threads> <iterations> <start_num>"
        )
        print(
            "Clean directory usage\n - python plot_primes.py clean (to clean directory)\n"
        )
        return False
    return True


def get_args(argv):
    verbose = False
    no_plot = False
    benchmark_toggle = False
    large_toggle = False
    log_toggle = False
    save_only = False

    if "--verbose" in argv or "-v" in argv:
        argv.remove("--verbose") if "--verbose" in argv else argv.remove("-v")
        verbose = True
    if "--no_plot" in argv or ("-n" in argv and "-p" in argv):
        if "--no_plot" in argv:
            argv.remove("--no_plot")
        else:
            argv.remove("-n")
            argv.remove("-p")
        no_plot = True
    if "--large" in argv or "-l" in argv:
        argv.remove("--large") if "--large" in argv else argv.remove("-l")
        large_toggle = True
    if "--log" in argv or "-g" in argv:
        argv.remove("--log") if "--log" in argv else argv.remove("-g")
        log_toggle = True
    if "--benchmark" in argv or "-b" in argv:
        argv.remove("--benchmark") if "--benchmark" in argv else argv.remove("-b")
        benchmark_toggle = True
    if "--save-only" in argv or "-s" in argv:
        argv.remove("--save-only") if "--save-only" in argv else argv.remove("-s")
        save_only = True
        if not check_args(argv):
            return
        df = load_prime_data(
            np.int64(argv[1]),
            np.int64(argv[2]),
            np.int64(argv[3]),
            np.int64(argv[4]),
            benchmark_toggle,
        )
    else:
        if not check_args(argv):
            return
        df = load_prime_data(
            np.int64(argv[1]),
            np.int64(argv[2]),
            np.int64(argv[3]),
            np.int64(argv[4]),
            benchmark_toggle,
        )
    return df, verbose, large_toggle, log_toggle, no_plot, save_only


def main():
    flags = get_flags(sys.argv.copy())
    if flags is None:
        return

    args = get_args(flags)
    if args is None:
        return

    df, verbose, large_toggle, log_toggle, no_plot, save_only = args
    if df is not None:
        primes = np.array(df["prime"])
        gaps = np.diff(primes)
        twin_primes = gaps[gaps == 2]

        print(
            f"Range: {df['prime'].min()} to {df['prime'].max()} ({df['prime'].max() - df['prime'].min()})\n"
        )

        print(f"Total primes found {len(df)}")
        print(
            f"Percentage of numbers that are primes {100 * len(primes) / (primes[-1] - primes[0]):.3f}%\n"
        )

        print(f"Total twin primes found {len(twin_primes)}")
        print(
            f"Percentage of primes that are twin primes {100 * len(twin_primes) / (primes[-1] - primes[0]):.3f}%\n"
        )

        print(f"Largest gap between primes found {max(gaps)}")
        print(f"Average prime gap {np.average(gaps):.3f}")
        print(
            f"Standard deviation {np.sqrt(np.average(gaps ** 2) / np.average(gaps) ** 2):.3f}"
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
            if large_toggle:
                n = int(math.sqrt(primes[-1])) + 1
                n = max(n, 3000)
                plot_ulam_datashader(primes, save_only, n)
            else:
                plot_primes(primes, gaps, log_toggle, save_only)
            print("\nProgram completed successfully")
    else:
        print("Program failed")


if __name__ == "__main__":
    main()
