// ---------------------------------------------------------------
// Header Includes
// ---------------------------------------------------------------
#include <vmlinux.h>
#include <bpf/bpf_helpers.h>
#include <bpf/bpf_tracing.h>

// ---------------------------------------------------------------
// Configuration Constants
// ---------------------------------------------------------------
/* Scheduler configuration */
#define SCHEDULER_NAME      "minimal_scheduler"
#define BASE_TIME_SLICE     5000000u // 5ms in nanoseconds
#define SHARED_DSQ_ID       0        // Global scheduling queue ID

/* Scheduler flags */
#define SCHEDULER_FLAGS     (SCX_OPS_ENQ_LAST | SCX_OPS_KEEP_BUILTIN_IDLE)

// ----------------------------------------------------------------
// Helper Macros
// ----------------------------------------------------------------
/**
 * @brief Macro for defining standard BPF struct operations
 * @param name Function name
 * @param args Function arguements
 */
#define BPF_STRUCT_OPS(name, args...) \
    SEC("struct_ops/"#name) BPF_PROG(name, ##args)

/**
 * @brief Macro for defining sleepable BPF operations
 * @param name Function name
 * @param args Function arguments
 */
#define BPF_STRUCT_OPS_SLEEPABLE(name, args...) \
    SEC("struct_ops.s/"#name)
    BPF_PROG(name, ##args)

// ----------------------------------------------------------------
// Scheduler Operations
// ----------------------------------------------------------------
/**
 * @brief Enqueue a task for execution
 * Calculates dynamic time slice based on queue length and dispatches task
 * 
 * @param p Task structure to be enqueued
 * @param enq_flags Enqueue flags
 * @return int Status code(0 on success)
 */
int BPF_STRUCT_OPS(sched_enqueue, struct task_struct *p, u64 enq_flags) {
    // Calculate time slice based on queue length
    u64 tasks_in_queue = scx_bpf_dsq_nr_queued(SHARED_DSQ_ID);
    u64 time_slice = BASE_TIME_SLICE;

    // Adjsut time slice if queue is not empty
    if (tasks_in_queue > 0) {
        time_slice /= tasks_in_queue;
    }

    // Dispatch task to shared queue
    scx_bpf_dispatch(p, SHARED_DSQ_ID, time_slice, enq_flags);
    return 0;
}

/**
 * @brief Dispatch a task from queue to CPU
 * Called when a CPU needs a new task to execute
 * 
 * @param cpu Target CPU ID
 * @param prev Previously running task
 * @return int Status Code (0 on success)
 */
int BPF_STRUCT_OPS(sched_dispatch, s32 cpu, struct task_struct *prev) {
    return scx_bpf_consume(SHARED_DSQ_ID);
}

// ---------------------------------------------------------
// Scheduler Definition Structure
// --------------------------------------------------------

/**
 * @brief Main scheduler operations structure
 * Defines the interface and behaviour of the scheduler
 */
SEC(".struct_ops.link")
struct sched_ext_ops sched_ops = {
    .enqueue  = (void *)sched_enqueue,
    .dispatch = (void *)sched_dispatch,
    .init     = (void *)sched_init,
    .flags    = SCHEDULER_FLAGS,
    .name     = SCHEDULER_NAME
};

// ----------------------------------------------------------
// License Declartion
// ----------------------------------------------------------
char _license[] SEC("license") = "GPL"