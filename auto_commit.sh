#!/bin/bash

# Auto-commit script for AI-assisted development
# This script monitors changes and commits them automatically

# Function to commit changes
commit_changes() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local message="Auto-commit: AI-assisted changes at $timestamp"
    
    # Add all changes
    git add .
    
    # Check if there are changes to commit
    if ! git diff-index --quiet HEAD --; then
        git commit -m "$message"
        echo "✅ Committed changes: $message"
    else
        echo "ℹ️  No changes to commit"
    fi
}

# Function to monitor file changes
monitor_changes() {
    echo "🔍 Starting file change monitoring..."
    echo "Press Ctrl+C to stop monitoring"
    
    # Use fswatch to monitor file changes (macOS)
    if command -v fswatch >/dev/null 2>&1; then
        fswatch -o . | while read f; do
            echo "📝 Detected file change, committing..."
            commit_changes
        done
    else
        echo "⚠️  fswatch not found. Install with: brew install fswatch"
        echo "📝 Committing current changes..."
        commit_changes
    fi
}

# Main execution
echo "🤖 Auto-commit script for AI-assisted development"
echo "Branch: $(git branch --show-current)"

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ Error: Not in a git repository"
    exit 1
fi

# Check if we have uncommitted changes
if ! git diff-index --quiet HEAD --; then
    echo "📝 Found uncommitted changes, committing them first..."
    commit_changes
fi

# Start monitoring
monitor_changes 