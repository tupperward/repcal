#!/bin/bash
# Test runner script for repcal project

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Repcal Test Suite ===${NC}\n"

# Check if pytest is installed
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}Error: pytest is not installed${NC}"
    echo "Install test dependencies with: pip install -r requirements-test.txt"
    exit 1
fi

# Parse command line arguments
COMPONENT="$1"
COVERAGE=""

if [[ "$2" == "--coverage" ]] || [[ "$1" == "--coverage" ]]; then
    COVERAGE="--cov=repcal_shared --cov=web --cov=bot --cov=webhook --cov-report=html --cov-report=term-missing"
fi

# Run tests based on component
case "$COMPONENT" in
    "shared")
        echo -e "${YELLOW}Running tests for repcal_shared package...${NC}"
        pytest tests/test_shared.py -m shared $COVERAGE
        ;;
    "web")
        echo -e "${YELLOW}Running tests for web application...${NC}"
        pytest tests/test_web.py -m web $COVERAGE
        ;;
    "bot")
        echo -e "${YELLOW}Running tests for Bluesky bot...${NC}"
        pytest tests/test_bot.py -m bot $COVERAGE
        ;;
    "webhook")
        echo -e "${YELLOW}Running tests for Discord webhook...${NC}"
        pytest tests/test_webhook.py -m webhook $COVERAGE
        ;;
    "unit")
        echo -e "${YELLOW}Running unit tests only...${NC}"
        pytest -m unit $COVERAGE
        ;;
    "integration")
        echo -e "${YELLOW}Running integration tests only...${NC}"
        pytest -m integration $COVERAGE
        ;;
    "fast")
        echo -e "${YELLOW}Running fast tests (excluding slow tests)...${NC}"
        pytest -m "not slow" $COVERAGE
        ;;
    "all"|"")
        echo -e "${YELLOW}Running all tests...${NC}"
        pytest tests/ $COVERAGE
        ;;
    "-h"|"--help"|"help")
        echo "Usage: ./run_tests.sh [component] [--coverage]"
        echo ""
        echo "Components:"
        echo "  all         - Run all tests (default)"
        echo "  shared      - Run repcal_shared package tests"
        echo "  web         - Run web application tests"
        echo "  bot         - Run Bluesky bot tests"
        echo "  webhook     - Run Discord webhook tests"
        echo "  unit        - Run unit tests only"
        echo "  integration - Run integration tests only"
        echo "  fast        - Run fast tests (exclude slow)"
        echo ""
        echo "Options:"
        echo "  --coverage  - Generate coverage report"
        echo ""
        echo "Examples:"
        echo "  ./run_tests.sh              # Run all tests"
        echo "  ./run_tests.sh web          # Run web tests only"
        echo "  ./run_tests.sh --coverage   # Run all tests with coverage"
        echo "  ./run_tests.sh bot --coverage # Run bot tests with coverage"
        exit 0
        ;;
    *)
        echo -e "${RED}Error: Unknown component '$COMPONENT'${NC}"
        echo "Run './run_tests.sh --help' for usage information"
        exit 1
        ;;
esac

# Check exit code
if [ $? -eq 0 ]; then
    echo -e "\n${GREEN}✓ All tests passed!${NC}"
else
    echo -e "\n${RED}✗ Some tests failed${NC}"
    exit 1
fi
