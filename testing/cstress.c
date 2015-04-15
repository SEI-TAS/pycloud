/*
 gcc -D _GNU_SOURCE -o cstress cstress.c -lm
*/

#include <ctype.h>
#include <errno.h>
#include <libgen.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <time.h>
#include <unistd.h>
#include <sys/wait.h>
#ifndef _GNU_SOURCE
#define _GNU_SOURCE
#endif
#include <sched.h>

#define err(OUT, STR, ARGS...) fprintf(OUT, STR, ##ARGS), fflush(OUT)

/* Implementation of check for option argument correctness.  */
#define assert_arg(A) \
if (++i == argc || ((arg = argv[i])[0] == '-' && \
!isdigit ((int)arg[1]) )) \
{ \
err (stderr, "missing argument to option '%s'\n", A); \
exit (1); \
}

int usage (int status);
long long atoll_b (const char *nptr);
long long calc_hog_time(void);
int hog_cpu(void);
int set_affinity(int core);
int child(int affinity, long long hog_time);

int main(int argc, char** argv) {
  int i, pid, children, affinity;
  long long cpu_count = 1;
  long long target_percent = 100;
  
  for (i = 1; i < argc; i++) {
  	char *arg = argv[i];
  	
  	if (strcmp (arg, "--cpu") == 0 || strcmp (arg, "-c") == 0) {
      assert_arg ("--cpu");
      cpu_count = atoll_b (arg);
      if (cpu_count <= 0) {
        err (stderr, "invalid number of cpu hogs: %lli\n", cpu_count);
        exit (1);
			}
    } else if (strcmp (arg, "--target") == 0 || strcmp (arg, "-t") == 0) {
      assert_arg ("--target");
      target_percent = atoll_b (arg);
      if (target_percent <= 0 || target_percent >= 100) {
        err (stderr, "invalid percentage: %lli\n", target_percent);
        exit (1);
			}
    } else if (strcmp (arg, "--help") == 0 || strcmp (arg, "-?") == 0) {
      usage(0);
    } else {
      err (stderr, "unrecognized option: %s\n", arg);
      usage(-1);
    }
  }
  
  fprintf(stdout, "CPU_Count: %lli\nTarget Percent: %lli\n", cpu_count, target_percent);
  
  
  long long hog_time =  0;
  if (target_percent < 100) {
    printf("Calculating sleep timers...\n");
    hog_time = calc_hog_time();
    fprintf(stdout, "Time / Spin: %lli usec\n", hog_time);
    // Convert to real duty cycle
    hog_time = (hog_time * 100 / target_percent) - hog_time;
    fprintf(stdout, "Time / Sleep: %lli usec\n", hog_time);
  }
  
  while (cpu_count > 0) {
    switch (pid = fork()) {
      case 0: //child
        sleep(2);
        exit(child(affinity, hog_time));
        break;
      case -1: //error
        err (stderr, "fork failed: %s\n", strerror (errno));
        break;
      default:
        printf("--> Created worker [%i]\n", pid);
        ++children;
        ++affinity;
    }
    --cpu_count;
  }
  
  while (children) {
    int status;
    if ((pid = wait (&status)) > 0) {
      --children;
    } else {
      err (stderr, "error waiting for worker: %s\n", strerror (errno));
      exit(-1);
    }
  }
  
  printf("All workers have finished\n");
  
  return 0;
}

int child(int affinity, long long hog_time) {
  int pid = getpid();
  if (set_affinity(affinity) != 0) {
    err(stderr, "[%i] Unable to set affinity!\n", pid);
    exit(-1);
  }
  if (set_fifo() != 0) {
    err(stderr, "[%i] Unable to set set FIFO!\n", pid);
    exit(-1);
  }
  
  printf("[%i] Worker starting on Core # %i\n", pid, affinity);
  
  while(1) {
    hog_cpu();
    usleep(hog_time);
  }
  
  return 0;
}

int set_fifo() {
  struct sched_param attr;
  
  if((attr.sched_priority = sched_get_priority_max(SCHED_FIFO)) < 0) {
    return -1;
  }
  
  return sched_setscheduler(0, SCHED_FIFO, &attr);
}

int set_affinity(int core) {
  cpu_set_t  mask;
  CPU_ZERO(&mask);
  CPU_SET(core, &mask);
  return sched_setaffinity(0, sizeof(mask), &mask);
}

long long tvdiff(struct timeval *t2, struct timeval *t1)
{
  long long diff = (t2->tv_usec + 1000000 * t2->tv_sec) - (t1->tv_usec + 1000000 * t1->tv_sec);
  return diff;
}

long long calc_hog_time(void) {
  int i;
  struct timeval starttime, endtime, diftime;
  gettimeofday(&starttime, NULL);
  // Spin for a while
  for (i = 0; i < 1000; i++) {
    hog_cpu();
  }
  gettimeofday(&endtime, NULL);
  
  long long diff = tvdiff(&endtime, &starttime);
  
  return diff / 1000;
}

int hog_cpu(void) {
  int i = 0;
  for (i = 0; i < 1000000; i++) {
    sqrt (32452843); //Some large prime #
  }
  return 0;
}

int usage (int status)
{
  char *mesg =
  "Usage: cstress [OPTION [ARG]] ...\n"
  " -c, --cpu N        spawn N workers spinning on sqrt()\n"
  " -t, --target N     attempt to force workers to N utilization\n"
  "Example: cstress --cpu 4 --target 85\n\n";
  
  fprintf (stdout, mesg);
  
  if (status <= 0)
    exit (-1 * status);
  
  return 0;
}

/* Convert a string representation of a number with an optional size suffix
 * to a long long.
 */
long long
atoll_b (const char *nptr)
{
  int pos;
  char suffix;
  long long factor = 0;
  long long value;
  
  if ((pos = strlen (nptr) - 1) < 0)
  {
    err (stderr, "invalid string\n");
    exit (1);
  }
  
  switch (suffix = nptr[pos])
  {
    case 'b':
    case 'B':
      factor = 0;
      break;
    case 'k':
    case 'K':
      factor = 10;
      break;
    case 'm':
    case 'M':
      factor = 20;
      break;
    case 'g':
    case 'G':
      factor = 30;
      break;
    default:
      if (suffix < '0' || suffix > '9')
      {
        err (stderr, "unrecognized suffix: %c\n", suffix);
        exit (1);
      }
  }
  
  if (sscanf (nptr, "%lli", &value) != 1)
  {
    err (stderr, "invalid number: %s\n", nptr);
    exit (1);
  }
  
  value = value << factor;
  
  return value;
}
