#!/bin/bash

# Flutter Earth Git Push Script
# This script automates the git push process for the Flutter Earth project

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if git is available
check_git() {
    if ! command -v git &> /dev/null; then
        print_error "Git is not installed or not in PATH"
        exit 1
    fi
}

# Function to check if we're in a git repository
check_repo() {
    if ! git rev-parse --git-dir > /dev/null 2>&1; then
        print_error "Not in a git repository"
        exit 1
    fi
}

# Function to check git status
check_status() {
    print_status "Checking git status..."
    
    # Check if there are any changes
    if git diff-index --quiet HEAD --; then
        print_warning "No changes to commit"
        return 1
    else
        print_status "Changes detected"
        return 0
    fi
}

# Function to add all changes
add_changes() {
    print_status "Adding all changes..."
    git add .
    print_success "Changes added to staging area"
}

# Function to commit changes
commit_changes() {
    local commit_message="$1"
    
    if [ -z "$commit_message" ]; then
        # Generate default commit message
        commit_message="Update Flutter Earth project - $(date '+%Y-%m-%d %H:%M:%S')"
    fi
    
    print_status "Committing changes with message: $commit_message"
    git commit -m "$commit_message"
    print_success "Changes committed successfully"
}

# Function to push changes
push_changes() {
    print_status "Pushing changes to remote repository..."
    
    # Get current branch
    local current_branch=$(git branch --show-current)
    print_status "Current branch: $current_branch"
    
    # Push to remote
    if git push origin "$current_branch"; then
        print_success "Changes pushed successfully to $current_branch"
    else
        print_error "Failed to push changes"
        return 1
    fi
}

# Function to show git status
show_status() {
    print_status "Current git status:"
    echo "=================="
    git status --short
    echo "=================="
}

# Function to show recent commits
show_recent_commits() {
    print_status "Recent commits:"
    echo "=================="
    git log --oneline -5
    echo "=================="
}

# Function to check remote status
check_remote() {
    print_status "Checking remote status..."
    
    # Fetch latest changes
    git fetch origin
    
    # Check if local is behind remote
    local current_branch=$(git branch --show-current)
    local behind_count=$(git rev-list HEAD..origin/$current_branch --count)
    
    if [ "$behind_count" -gt 0 ]; then
        print_warning "Local branch is $behind_count commits behind remote"
        print_status "Consider pulling latest changes first"
        return 1
    else
        print_success "Local branch is up to date with remote"
        return 0
    fi
}

# Function to handle conflicts
handle_conflicts() {
    print_warning "Merge conflicts detected!"
    print_status "Please resolve conflicts manually and then run this script again"
    print_status "To abort merge: git merge --abort"
    print_status "To continue after resolving: git add . && git commit"
    exit 1
}

# Main function
main() {
    print_status "Starting Flutter Earth Git Push Script"
    echo "=============================================="
    
    # Check prerequisites
    check_git
    check_repo
    
    # Parse command line arguments
    local commit_message=""
    local auto_commit=false
    local show_info=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -m|--message)
                commit_message="$2"
                shift 2
                ;;
            -a|--auto)
                auto_commit=true
                shift
                ;;
            -s|--status)
                show_info=true
                shift
                ;;
            -h|--help)
                echo "Usage: $0 [OPTIONS]"
                echo "Options:"
                echo "  -m, --message MESSAGE  Commit message"
                echo "  -a, --auto            Auto-commit with default message"
                echo "  -s, --status          Show git status and recent commits"
                echo "  -h, --help            Show this help message"
                exit 0
                ;;
            *)
                print_error "Unknown option: $1"
                echo "Use -h or --help for usage information"
                exit 1
                ;;
        esac
    done
    
    # Show status if requested
    if [ "$show_info" = true ]; then
        show_status
        show_recent_commits
        check_remote
        exit 0
    fi
    
    # Check remote status
    if ! check_remote; then
        print_warning "Consider pulling latest changes before pushing"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            print_status "Aborted by user"
            exit 0
        fi
    fi
    
    # Check if there are changes to commit
    if ! check_status; then
        if [ "$auto_commit" = true ]; then
            print_warning "No changes to commit, but auto-commit was requested"
            exit 0
        else
            print_status "No changes to commit"
            exit 0
        fi
    fi
    
    # Show current status
    show_status
    
    # Auto-commit or prompt for action
    if [ "$auto_commit" = true ]; then
        add_changes
        commit_changes "$commit_message"
    else
        read -p "Add and commit changes? (Y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Nn]$ ]]; then
            print_status "Aborted by user"
            exit 0
        fi
        
        add_changes
        commit_changes "$commit_message"
    fi
    
    # Push changes
    if push_changes; then
        print_success "Git push completed successfully!"
        show_recent_commits
    else
        print_error "Git push failed"
        exit 1
    fi
}

# Handle script interruption
trap 'print_error "Script interrupted"; exit 1' INT TERM

# Run main function
main "$@" 