#!/bin/bash

procs=(1 2 4 8 16)
thrds=(1 2 4 8 16)
for i in {0..4}; do
    echo BENCHMARK RUN $((i+1))
    echo ==============================================
    echo ==============================================
    echo
    for j in {0..5}; do
        echo =====${j}=====
        python plot_primes.py -npb ${procs[i]} ${thrds[i]} $((10000000/(procs[i]*thrds[i]))) $((RANDOM * 100000))
        echo ==============
    done
    echo ==============================================
    echo ==============================================
    echo
done
python plot_primes.py clean
echo =====FINISHED=====