#!/bin/bash
# Clean macOS-specific files that shouldn't be in the repository

echo "🧹 Cleaning macOS system files..."

# Find and remove .DS_Store files
find . -name ".DS_Store" -type f -delete 2>/dev/null
echo "  ✓ Removed .DS_Store files"

# Find and remove ._* files (resource forks)
find . -name "._*" -type f -delete 2>/dev/null
echo "  ✓ Removed resource fork files"

# Find and remove .AppleDouble directories
find . -name ".AppleDouble" -type d -exec rm -rf {} + 2>/dev/null
echo "  ✓ Removed .AppleDouble directories"

echo "✅ macOS cleanup complete!"
