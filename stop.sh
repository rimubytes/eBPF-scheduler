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