#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color
YELLOW='\033[1;33m'

# Configuration
SCHEDULER_NAME="minimal_scheduler"

echo -e "${YELLOW}Stopping eBPF scheduler...${NC}"