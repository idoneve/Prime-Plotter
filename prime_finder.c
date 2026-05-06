#include <errno.h>
#include <inttypes.h>
#include <primesieve.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

void make_primes_dir(void) {
  struct stat st = { 0 };
  if (stat("primes", &st) == 0) {
    char cmd[256];
    snprintf(cmd, sizeof(cmd), "rm -rf primes");
    if (system(cmd) != 0) {
      perror("Failed to remove primes directory");
      exit(1);
    }
  }

  if (mkdir("primes", 0755) != 0) {
    perror("Failed to create primes directory");
    exit(1);
  }
}

void *thread_func(void *arg) {
    uint64_t *args = (uint64_t *)arg;
    uint64_t process_id = args[0];
    uint64_t thread_id  = args[1];
    uint64_t total_threads = args[2];
    uint64_t range = args[3];
    uint64_t start_num = args[4];
    
    uint64_t chunk = range / total_threads;
    uint64_t start = start_num + (process_id * range) + (thread_id * chunk);
    uint64_t end = (thread_id == total_threads - 1) 
                   ? start_num + ((process_id + 1) * range) - 1 
                   : start + chunk - 1;
    
    char filename[256];
    snprintf(filename, sizeof(filename), "primes/p%d_t%d.csv", 
             (int)process_id, (int)thread_id);
    FILE *fp = fopen(filename, "w");
    if (!fp) {
        perror("fopen failed");
        free(args);
        return NULL;
    }
    
    primesieve_iterator it;
    primesieve_init(&it);
    primesieve_skipto(&it, start, end);
    
    uint64_t prime;
    while ((prime = primesieve_next_prime(&it)) <= end) {
        fprintf(fp, "%" PRIu64 "\n", prime);
    }
    
    primesieve_free_iterator(&it);
    fclose(fp);
    free(args);
    return NULL;
}

int main(int argc, const char *argv[]) {
  if (argc != 5) {
    perror("Incorrect number of args");
    exit(1);
  }

  char *endptr;
  errno = 0;
  uint64_t process_num = strtoull(argv[1], &endptr, 10);
  if (errno != 0 || *endptr != '\0' || process_num == 0) {
    perror("Invalid process_num");
    exit(1);
  }
  uint64_t thread_num = strtoull(argv[2], &endptr, 10);
  if (errno != 0 || *endptr != '\0' || thread_num == 0) {
    perror("Invalid thread_num");
    exit(1);
  }
  uint64_t range = strtoull(argv[3], &endptr, 10);
  if (errno != 0 || *endptr != '\0' || range == 0) {
    perror("Invalid range");
    exit(1);
  }
  uint64_t start_num = strtoull(argv[4], &endptr, 10);
  if (errno != 0 || *endptr != '\0') {
    perror("Invalid starting number");
    exit(1);
  }

  make_primes_dir();

  pid_t pids[process_num];
  pthread_t threads[thread_num];
  for (uint64_t i = 0; i < process_num; ++i) {
    pids[i] = fork();
    if (pids[i] == -1) {
      perror("Creating fork failed");
      exit(1);
    } else if (pids[i] == 0) {
      for (uint64_t j = 0; j < thread_num; ++j) {
        uint64_t *args = malloc(5 * sizeof(uint64_t));
        args[0] = i;
        args[1] = j;
        args[2] = thread_num;
        args[3] = range;
        args[4] = start_num;
        if (pthread_create(&threads[j], NULL, thread_func, args) != 0) {
          perror("Creating thread failed");
          free(args);
          exit(1);
        }
      }

      for (uint64_t j = 0; j < thread_num; ++j) {
        if (pthread_join(threads[j], NULL) != 0) {
          perror("Joining thread failed");
          exit(1);
        }
      }

      exit(0);
    }
  }

  for (uint64_t i = 0; i < process_num; ++i) {
    int status;
    waitpid(pids[i], &status, 0);
  }

  return 0;
}
