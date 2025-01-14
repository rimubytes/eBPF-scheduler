#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}Error: Tests must be run as root${NC}"
    exit 1
fi

# Check for required Python packages
echo -e "${YELLOW}Checking dependencies...${NC}"
python3 -c "import psutil" 2>/dev/null || {
    echo -e "${RED}Error: psutil package is required${NC}"
    echo "Please install it using: pip3 install psutil"
    exit 1
}

# Run the tests
echo -e "${YELLOW}Running scheduler tests...${NC}"
python3 test_scheduler.py

# Store test result
TEST_RESULT=$?

# Check the result
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}All tests passed successfully!${NC}"
else
    echo -e "${RED}Tests failed with exit code $TEST_RESULT${NC}"
fi

exit $TEST_RESULT