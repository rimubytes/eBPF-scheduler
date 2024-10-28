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
