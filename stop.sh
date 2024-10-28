#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color
YELLOW='\033[1;33m'

# Configuration
SCHEDULER_NAME="minimal_scheduler"

echo -e "${YELLOW}Stopping eBPF scheduler...${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Error: Please run as root${NC}"
    exit 1
fi

# Check if bpftool is installed
command -v bpftool >/dev/null 2>&1 || {
    echo -e "${RED}Error: bpftool is required but not installed${NC}"
    exit 1
}

# Check if our scheduler is running
if [ -f "/sys/kernel/sched_ext/root/ops" ]; then
    CURRENT_SCHEDULER=$(cat /sys/kernel/sched_ext/root/ops)
    if [ "$CURRENT_SCHEDULER" != "$SCHEDULER_NAME" ]; then
        echo -e "${RED}Error: Our scheduler is not currently running${NC}"
        if [ ! -z "$CURRENT_SCHEDULER" ]; then
            echo -e "Current scheduler is: ${YELLOW}$CURRENT_SCHEDULER${NC}"
        fi
        exit 1
    fi
else
    echo -e "${RED}Error: No scheduler is currently running${NC}"
    exit 1
fi

# Unload the scheduler
echo -e "${YELLOW}Unloading scheduler...${NC}"
echo none > /sys/kernel/sched_ext/root/ops

if [ $? -ne 0 ]; then
    echo -e "${RED}Error: Failed to unload scheduler${NC}"
    exit 1
fi

# Verify the scheduler was unloaded
if [ -f "/sys/kernel/sched_ext/root/ops" ]; then
    CURRENT_SCHEDULER=$(cat /sys/kernel/sched_ext/root/ops)
    if [ -z "$CURRENT_SCHEDULER" ]; then
        echo -e "${GREEN}Scheduler successfully unloaded!${NC}"
        exit 0
    fi
fi

echo -e "${RED}Error: Scheduler failed to unload properly${NC}"
exit 1