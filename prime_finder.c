#include <errno.h>
#include <inttypes.h>
#include <pthread.h>
#include <stdio.h>
#include <stdlib.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <unistd.h>

void make_primes_dir(void) {
  struct stat st = {0};
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

void make_primes_file(uint64_t *found, uint64_t pid, uint64_t tid,
                      uint64_t count) {
  char filename[512];
  snprintf(filename, sizeof(filename), "primes/primes_p%llu_t%llu.csv", pid,
           tid);

  FILE *file = fopen(filename, "w");
  if (file == NULL) {
    perror("Failed to open file");
    exit(1);
  } else {
    for (uint64_t i = 0; i < count; ++i) {
      fprintf(file, "%" PRIu64 ",%" PRIu64 ",%" PRIu64 "\n", pid, tid,
              found[i]);
    }
    fclose(file);
  }
}

uint64_t is_prime(uint64_t n) {
  if (n < 2) {
    return 0;
  }
  if (n == 2 || n == 3) {
    return 1;
  }
  if (n % 2 == 0 || n % 3 == 0) {
    return 0;
  }

  for (uint64_t i = 5; i * i <= n; i += 6) {
    if (n % i == 0 || n % (i + 2) == 0) {
      return 0;
    }
  }

  return 1;
}

void *thread_func(void *arg) {
  uint64_t *args = (uint64_t *)arg;
  uint64_t pid = args[0];
  uint64_t tid = args[1];
  uint64_t thread_num = args[2];
  uint64_t range = args[3];
  uint64_t start_num = args[4];
  free(arg);

  uint64_t tidx = pid * thread_num + tid;
  uint64_t start = start_num + tidx * range;
  uint64_t end = start + range;

  uint64_t *found = malloc(range * sizeof(uint64_t));
  uint64_t count = 0;
  if (start <= 2 && 2 < end) {
    found[count++] = 2;
  }

  uint64_t first = start;
  if (first < 3) {
    first = 3;
  }
  if (first % 2 == 0) {
    ++first;
  }

  for (uint64_t n = first; n < end; n += 2) {
    if (is_prime(n)) {
      found[count++] = n;
    }
  }

  make_primes_file(found, pid, tid, count);

  free(found);
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
  if (errno != 0 || *endptr != '\0' || start_num == 0) {
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
