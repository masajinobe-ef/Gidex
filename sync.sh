#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

function show_help() {
    echo -e "${BLUE}Usage: ./start.sh [options]${NC}"
    echo
    echo -e "${YELLOW}Options:${NC}"
    echo -e "  -u, --update      Update submodules"
    echo -e "  -c, --commit      Commit changes in submodules"
    echo -e "  -p, --push        Push changes in submodules"
    echo -e "  -m, --main-commit Commit changes in the Gidex project"
    echo -e "  -a, --all-push    Push all changes (submodules and main project)"
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
        read -p "Enter commit message for submodules: " commit_message
        git submodule foreach "git add . && git commit -m '$commit_message'"
        ;;
    -p | --push)
        echo -e "${GREEN}Pushing changes in submodules...${NC}"
        git submodule foreach "git push"
        ;;
    -m | --main-commit)
        echo -e "${GREEN}Committing changes in the main project...${NC}"
        read -p "Enter commit message for the main project: " main_commit_message
        git add .
        git commit -m "$main_commit_message"
        ;;
    -a | --all-push)
        echo -e "${GREEN}Pushing all changes (submodules and main project)...${NC}"
        git submodule foreach "git push"
        git push
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
uv sync
uv run src/main.py
