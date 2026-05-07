# Prime Plotter

Prime Plotter is a parallel prime-number computation and visualization pipeline combining high-performance C processing with Python-based data aggregation and analysis.

The project demonstrates process/thread parallelism, automated data workflows, and reproducible numerical visualization.

---

## Overview

The system consists of three components:

* **Prime computation (C)**
  A multithreaded, multi-process program generates prime numbers across configurable numeric ranges.

* **Build & execution (Makefile)**
  Handles compilation, execution, and output file management.

* **Data processing (Python)**
  Orchestrates execution, aggregates CSV outputs, and produces analytical plots.

---

## Requirements

* Python 3.x
* GCC (or compatible C compiler)
* Make
* Python packages:

```bash
pip install pandas matplotlib datashader colorcet
```

---

## Usage

All interaction is performed through the Python driver script.

### Run Prime Generation

```bash
python plot_primes.py [-b] [-v] [-l] [-g] [-s] [-np] <processes> <threads> <range> <start>
```

Example:

```bash
# Ulam spiral with log scale gaps, only saved to PNG
python plot_primes.py -lgs 4 8 1000000 1
```

This runs:

* 4 processes
* 8 threads per process
* Range size of 1,000,000
* Starting at 1

Output Plot:

![Untitled](https://github.com/user-attachments/assets/fcc364a8-151d-4ee9-8155-95722f52686a)

---

## Command-Line Options

Flags may be provided individually or combined (e.g., `-vnp`).

| Flag | Description                             |
| ---- | ----------------------------------------- |
| `-v` | Verbose output                     
| `-np`| Skip plotting
| `-s` | Save only (doesn't show plot only save to .png)              
| `-b` | Enable benchmarking         
| `-l` | Enable large scale plotting (using the Ulam spiral)
| `-g` | Enable log scaling in the plot

---

## Cleaning Output

Remove build artifacts and generated datasets:

```bash
python plot_primes.py clean
```

---

## Output

The program produces:

- Individual CSV files per process (in `primes/` directory)
- A merged dataset: `all_primes.csv`
- NumPy array: `all_primes.npy`
- Gap/scatter plot: `primes_gaps.png`
- Ulam spiral: `ulam_spiral.png`

---

## Project Structure

```
Prime-Plotter/
├── prime_finder.c
├── plot_primes.py
├── Makefile
├── .gitignore
└── README.md
```

Note: The `primes/` directory and CSV files are generated at runtime and are not stored in the repository.

---

## Purpose

This project was created to demonstrate:

* Parallel systems programming in C
* Process and thread coordination
* Automated data pipelines
* Practical performance scaling techniques
* Prime number distribution analysis
* Ulam spiral visualization
* Empirical verification of the Prime Number Theorem

---
