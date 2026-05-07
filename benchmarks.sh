#!/bin/bash

exec > benchmarks.txt 2>&1

procs=(1 2 4 8)
thrds=(1 2 4 8)
for i in {0..3}; do
    for j in {0..3}; do
        echo BENCHMARK RUN $(((i*4+j)+1))
        echo ==============================================
        echo ==============================================
        echo
        for k in {0..5}; do
            echo =====${k}=====
            python plot_primes.py -npb ${procs[i]} ${thrds[j]} $((10000000/(procs[i]*thrds[j]))) $((RANDOM * 100000))
            echo ==============
        done
        echo ==============================================
        echo ==============================================
        echo
    done
done
python plot_primes.py clean
echo =====FINISHED=====