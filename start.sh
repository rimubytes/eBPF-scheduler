#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No color
YELLOW='\033[1;33m]'

# Configuration
SCHEDULER_NAME="minimal_scheduler"
COMPILER="clang"
COMPILER_FLAGS="02 -g -target bpf -D__TARGET_ARCH_x86"
OUTPUT_FILE="scheduler.bpf.o"
SOURCE_FILE="scheduler.bpf.c"

echo -e "${YELLOW}Starting eBPF scheduler deployment...${NC}"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Error: Please run as root${NC}"
    exit 1
fi

# Check if required tools are installed
command -v $COMPILER >/dev/null 2>&1 || {
    echo -e "${RED}Error: $COMPILER is required but not installed${NC}"
    exit 1
}

command -v bpftool >/dev/null 2>&1 || {
    echo -e "${RED}Error: bpftool is required but not installed${NC}"
    exit 1
}

# Check if kernel supports sched_ext
if [ ! -d "/sys/kernel/sched_ext" ]; then
    echo -e "${RED}Error: sched_ext not supported by kernel${NC}"
    echo "Please ensure you have a kernel with sched_ext support enabled"
    exit 1
fi
