#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

function show_help() {
    echo -e "${BLUE}Usage: ./sync.sh [options]${NC}"
    echo
    echo -e "${YELLOW}Options:${NC}"
    echo -e "  -u, --update      Update submodules"
    echo -e "  -c, --commit      Commit changes in submodules"
    echo -e "  -p, --push        Push changes in submodules"
    echo -e "  -h, --help        Show this help message"
}

if [[ $# -eq 0 ]]; then
    echo -e "${RED}Error: No arguments provided.${NC}"
    show_help
    exit 1
fi

while [[ "$1" != "" ]]; do
    case $1 in
    -u | --update)
        echo -e "${GREEN}Updating submodules...${NC}"
        git submodule update --remote
        ;;
    -c | --commit)
        echo -e "${GREEN}Committing changes in submodules...${NC}"
        read -p "Enter commit message: " commit_message
        git submodule foreach "git add . && git commit -m '$commit_message'"
        ;;
    -p | --push)
        echo -e "${GREEN}Pushing changes in submodules...${NC}"
        git submodule foreach "git push"
        ;;
    -h | --help)
        show_help
        exit 0
        ;;
    *)
        echo -e "${RED}Error: Unknown argument '$1'.${NC}"
        show_help
        exit 1
        ;;
    esac
    shift
done

echo -e "${GREEN}Running main script...${NC}"
uv run src/main.py
