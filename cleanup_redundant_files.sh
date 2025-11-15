#!/bin/bash

# Cleanup Script for Python AI IDE
# Removes 11 redundant files identified during refactoring
# Run this script from the repository root directory

echo "🧹 Starting cleanup of redundant files..."
echo ""

# Counter for deleted files
deleted=0
failed=0

# Function to delete file if it exists
delete_file() {
    if [ -f "$1" ]; then
        rm "$1"
        if [ $? -eq 0 ]; then
            echo "✅ Deleted: $1"
            ((deleted++))
        else
            echo "❌ Failed to delete: $1"
            ((failed++))
        fi
    else
        echo "⚠️  Not found: $1"
    fi
}

echo "📄 Removing documentation spam..."
delete_file "BUGFIXES.md"
delete_file "DEEP_REFACTORING_COMPLETE.md"
delete_file "HOTFIX_SUMMARY.md"
delete_file "PYTHON_3.13_COMPATIBILITY_FIX.md"
delete_file "REFACTORING.md"

echo ""
echo "💾 Removing code duplicates..."
delete_file "app.py"
delete_file "config.py"
delete_file "js/socket-integration.js"
delete_file "js/ui-integration.js"
delete_file "backend/services/terminal_service_secure.py"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 Cleanup Summary:"
echo "   ✅ Files deleted: $deleted"
echo "   ❌ Failed: $failed"
echo "   ⚠️  Not found: $((11 - deleted - failed))"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $deleted -gt 0 ]; then
    echo "🎉 Cleanup complete! Don't forget to commit the changes:"
    echo "   git add -A"
    echo "   git commit -m 'Remove redundant files after refactoring'"
    echo "   git push"
else
    echo "⚠️  No files were deleted. They may have already been removed."
fi

echo ""
