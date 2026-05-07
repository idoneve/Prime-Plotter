# Prime Plotter

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A high-performance parallel prime-number computation and visualization pipeline. Combines a multi-process, multi-threaded C sieve engine with Python-based analysis and publication-quality plotting.

---

## Overview

Prime Plotter computes primes at scale (tested up to 8 × 10⁹), verifies the Prime Number Theorem empirically, analyzes prime gaps, and generates Ulam spiral visualizations.

| Component | Technology | Purpose |
|-----------|-----------|---------|
| **Sieve Engine** | C + primesieve | Parallel prime generation |
| **Build System** | Makefile | Compilation, benchmarking, cleanup |
| **Data Pipeline** | Python (pandas, numpy) | Aggregation, statistics, .npy export |
| **Visualization** | matplotlib, datashader | PNT plots, gap analysis, Ulam spiral |

---

## Features

- **Segmented sieve** via primesieve — sieves billions of integers in minutes
- **Process + thread parallelism** — configurable fork() processes and pthread threads
- **Automated benchmarking** — wall time, user time, speedup, and efficiency across configurations
- **Prime Number Theorem verification** — density and average gap vs. theoretical predictions
- **Prime gap analysis** — distribution, twin primes, maximum gaps
- **Ulam spiral** — high-resolution datashader rendering with diagonal polynomial patterns
- **Publication-ready output** — all plots saved as PNG for LaTeX papers
- **LaTeX Paper on prime numbers** - the final paper using this repo for computations

---

## Installation

### Prerequisites

- C compiler (GCC or Clang)
- Make
- Python 3.10+
- [primesieve](https://github.com/kimwalisch/primesieve) (C library)

### Setup

```bash
# Clone the repository
git clone https://github.com/idoneve/Prime-Plotter.git
cd Prime-Plotter

# Install primesieve (macOS)
brew install primesieve

# Create virtual environment and install Python dependencies
python3 -m venv .venv
source .venv/bin/activate
pip install pandas matplotlib datashader
```

---

## Usage

All interaction is through the Python driver script.

### Basic prime generation

```bash
python plot_primes.py <processes> <threads> <range> <start>
```

**Example:** 4 processes, 8 threads, range of 1,000,000 starting from 1:

```bash
python plot_primes.py 4 8 1000000 1
```

### Command-line flags

| Flag | Description |
|------|-------------|
| `-v` | Verbose output (prime counts per process/thread) |
| `-b` | Benchmark mode with timing statistics |
| `-l` | Ulam spiral via datashader (replaces default scatter plot) |
| `-g` | Logarithmic scale for prime gap plot |
| `-s` | Save plots to PNG without displaying |
| `-np` | Skip plotting entirely (compute only) |
| `clean` | Remove all build artifacts and generated data |

### Examples

```bash
# Benchmark with verbose output, skip plotting
python plot_primes.py -b -v -np 4 8 1000000 1

# Generate Ulam spiral, save to PNG, no display
python plot_primes.py -l -s 4 8 10000000 1

# Log-scale gap plot
python plot_primes.py -g 8 8 4000000 1

# Clean up
python plot_primes.py clean

# Run benchmarks.sh
./benchmarks.sh
```

---

## Output

| File | Description |
|------|-------------|
| `primes/p*_t*.csv` | Per-thread prime lists |
| `all_primes.csv` | Merged and sorted primes |
| `all_primes.npy` | NumPy array for fast notebook loading |
| `primes_gaps.png` | Prime scatter and gap plot |
| `ulam_spiral.png` | Ulam spiral (datashader, high-res) |
| `pnt_density.png` | Prime density vs 1/ln(x) |
| `pnt_gaps.png` | Average gap vs ln(x) |
| `prime_gaps.png` | Gap distribution and analysis |
| `speedup.png` | Parallel speedup (log-log) |
| `efficiency.png` | Parallel efficiency |
| `benchmarks.txt` | Benchmark results |

---

## Notebook

A Jupyter notebook (`prime_notebook.ipynb`) walks through the full pipeline:

1. Sieve of Eratosthenes (with step-by-step visualization)
2. Parallelism: processes vs. threads (with benchmark analysis)
3. Prime Number Theorem (empirical verification)
4. Prime gaps (distribution, twin primes, maximal gaps)
5. Ulam spiral (with mathematical explanation)

All figures are generated at publication quality for LaTeX papers.

---

## Performance

Benchmarked on Apple Silicon (M-series) sieving 10⁷ ranges:

| Workers (P×T) | Wall Time | Speedup | Efficiency |
|---------------|-----------|---------|------------|
| 1×1 (1) | 5.54s | 1.0× | 100% |
| 2×2 (4) | 1.93s | 2.9× | 72% |
| 4×4 (16) | 1.77s | 3.1× | 19% |
| 8×8 (64) | 1.47s | 3.8× | 6% |
| 16×16 (256) | 1.64s | 3.4× | 1% |

**Sweet spot:** 64 workers (8 processes × 8 threads). Beyond this, process creation overhead dominates.

---

## Project Structure

```
Prime-Plotter/
├── prime_finder.c       # C sieve engine (fork + pthreads)
├── plot_primes.py       # Python driver and visualization
├── prime_notebook.ipynb # Analysis notebook
├── Makefile             # Build, benchmark, and cleanup
├── benchmarks.sh        # Run multiple benchmarks on different thread to process ratios
├── paper.pdf            # Compiled LaTeX paper
├── README.md
└── .gitignore
```

Generated at runtime (not tracked):
```
primes/                 # Per-thread CSV output
all_primes.csv          # Merged dataset
all_primes.npy          # NumPy export
*.png                   # All plot outputs
benchmarks.txt          # Benchmark results
```

---

## Purpose

This project was built for a Number Theory final to demonstrate:

- Parallel systems programming in C
- Process and thread coordination
- Empirical verification of the Prime Number Theorem
- Prime gap and twin prime analysis
- Ulam spiral visualization
- Reproducible computational mathematics

---

## License

MIT — see LICENSE for details.

---

## Acknowledgments

- [primesieve](https://github.com/kimwalisch/primesieve) by Kim Walisch — the gold standard for prime sieving
- [datashader](https://datashader.org/) — makes billion-point visualizations possible
- Stanisław Ulam — for doodling in a boring lecture