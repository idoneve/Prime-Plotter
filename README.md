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
pip install pandas matplotlib
```

---

## Usage

All interaction is performed through the Python driver script.

### Run Prime Generation

```bash
python plot_primes.py [options] <processes> <threads> <range> <start>
```

Example:

```bash
python plot_primes.py -vl 4 8 1000000 1
```

This runs:

* 4 processes
* 8 threads per process
* Range size of 1,000,000
* Starting at 1

Output Plot:

[Untitled.pdf](https://github.com/user-attachments/files/25640701/Untitled.pdf)

---

## Command-Line Options

Flags may be provided individually or combined (e.g., `-vnp`).

| Flag | Description                               |
| ---- | ----------------------------------------- |
| `-v` | Verbose output                            |
| `-n` | Skip plotting                             |
| `-p` | Skip prime generation (use existing data) |
| `-b` | Enable large-scale processing mode        |

---

## Cleaning Output

Remove build artifacts and generated datasets:

```bash
python plot_primes.py clean
```

---

## Output

The program produces:

* Individual CSV files per process
* A merged dataset: `all_primes.csv`
* Visualization plots generated from aggregated data

---

## Project Structure

```
Prime-Plotter/
├── prime_finder.c
├── plot_primes.py
├── Makefile
└── README.md
```

Note: The `Primes/` directory and CSV files are generated at runtime and are not stored in the repository.

---

## Purpose

This project was created to demonstrate:

* Parallel systems programming in C
* Process and thread coordination
* Automated data pipelines
* Practical performance scaling techniques

---
