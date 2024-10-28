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

