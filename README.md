# eBPF-scheduler

This project provides a basic tutorial for building a minimal Linux scheduler using `sched_ext` and eBPF directly in C. The scheduler operates with a First-In-First-Out(FIFO) approach, essentially functioning as a round-robin scheduler by using a global scheduling queue to distribute tasks across CPUs.

## Overview

- The Scheduler:

    - Utilizes a global dispatch queue (DSQ) from which each CPU fetches tasks to run
    - Orders tasks based on a round-robin mechanism, dispatching tasks in a FIFO manner
    - Adjusts each task's time slice according to the number of tasks in the queue, optimizing system responsiveness
    
---
### Requirements

To build and run this custom scheduler, you'll need:
    - A 6.12 kernel or a patched 6.11 kernel with `sched_ext` support
    - Recent versions of `clang` for compilation and `bpftool` for attaching the scheduler.
