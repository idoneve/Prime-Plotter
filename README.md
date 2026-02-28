All commands go through the python file which uses the Makefile to run the C program generating the primes in the Primes directory, the python file concats them together into one all_primes.csv file. Using pandas the csv file is read in and then graphs the primes.

The usage for the python file is:
    1. python plot_primes.py <processes> <threads> <range> <start_num> <large_scale_toggle> <("(t)rue" if running large values)>
    2. python plot_primes.py clean

1 takes in a number for processes, threads, range, and start_num. 
    Processes: The number of forked processes to run in parallel
    Threads: The number of threads each process creates to run in paralell
    Range: The amount of number each thread checks
    Start_num: The number as which to start looking for primes

2 simply cleans any .o, .d, .out files and the ALL of the prime csv files including all_primes.csv