#!/bin/bash

# Screenshot Capture Script for Everything by mdfind
# This script helps macOS users capture high-quality screenshots for documentation

set -e

# Configuration
SCREENSHOTS_DIR="screenshots"
APP_NAME="Everything by mdfind"
DELAY=3  # Seconds to wait before capture

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_step() {
    echo -e "${BLUE}📸 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is designed for macOS only."
    exit 1
fi

# Check if Everything by mdfind is running
if ! pgrep -f "everything.py" > /dev/null; then
    print_warning "Everything by mdfind doesn't appear to be running."
    echo "Please start the application first with: python everything.py"
    read -p "Press Enter when the application is running, or Ctrl+C to exit..."
fi

# Create screenshots directory if it doesn't exist
mkdir -p "$SCREENSHOTS_DIR"

echo -e "${BLUE}"
echo "========================================="
echo "  Screenshot Capture Assistant"
echo "  for Everything by mdfind"
echo "========================================="
echo -e "${NC}"

# Screenshot capture function
capture_screenshot() {
    local filename="$1"
    local description="$2"
    local fullpath="$SCREENSHOTS_DIR/$filename"
    
    print_step "Preparing to capture: $description"
    echo "File: $fullpath"
    echo "Please arrange the application window to show: $description"
    echo "Screenshot will be taken in $DELAY seconds..."
    
    countdown=$DELAY
    while [ $countdown -gt 0 ]; do
        echo -ne "  $countdown\r"
        sleep 1
        ((countdown--))
    done
    
    # Capture the screenshot
    screencapture -w -P "$fullpath" 2>/dev/null
    
    if [ -f "$fullpath" ]; then
        print_success "Captured: $filename"
        
        # Get file size for confirmation
        size=$(ls -lh "$fullpath" | awk '{print $5}')
        echo "  File size: $size"
    else
        print_error "Failed to capture: $filename"
        echo "  Please try again manually"
    fi
    
    echo
    read -p "Press Enter to continue to the next screenshot..."
    echo
}

# Main screenshot capture sequence
echo "This script will help you capture all required screenshots for the documentation."
echo "Each screenshot will be captured after a $DELAY second countdown."
echo "Make sure the application window is visible and properly arranged before each capture."
echo
read -p "Press Enter to start the screenshot capture process..."
echo

# Core Interface Screenshots
capture_screenshot "01-main-interface-light.png" "Main interface in light mode"
capture_screenshot "02-main-interface-dark.png" "Main interface in dark mode (enable dark mode first)"

# Search Functionality
capture_screenshot "03-basic-search.png" "Basic text search with results"
capture_screenshot "04-content-search.png" "Content-based search results"
capture_screenshot "05-advanced-filters.png" "Advanced filtering options expanded"
capture_screenshot "06-directory-specific-search.png" "Directory-specific search"

# Multi-Tab Interface
capture_screenshot "07-multiple-tabs.png" "Multiple search tabs open"
capture_screenshot "08-tab-management.png" "Tab context menu (right-click on tab)"

# Preview System
capture_screenshot "09-preview-panel-text.png" "Text file preview panel"
capture_screenshot "10-preview-panel-image.png" "Image preview with metadata"
capture_screenshot "11-preview-panel-video.png" "Video preview with controls"

# Media Integration
capture_screenshot "12-media-player-integrated.png" "Integrated media player"
capture_screenshot "13-media-player-standalone.png" "Standalone player window"

# File Operations
capture_screenshot "14-context-menu.png" "File context menu (right-click on file)"
capture_screenshot "15-multi-select.png" "Multiple files selected"

# Quick Access
capture_screenshot "16-bookmarks-menu.png" "Bookmarks menu expanded"
capture_screenshot "17-large-files-search.png" "Large files search results"

# Organization
capture_screenshot "18-sorting-options.png" "Sortable column headers"
capture_screenshot "19-lazy-loading.png" "Large result set with lazy loading"

# Data Operations
capture_screenshot "20-csv-export.png" "CSV export dialog"
capture_screenshot "21-path-operations.png" "Path operations context menu"

# Customization
capture_screenshot "22-view-menu.png" "View menu options"
capture_screenshot "23-search-history.png" "Search history dropdown"
capture_screenshot "24-file-type-icons.png" "Various file types with emoji icons"

print_success "Screenshot capture complete!"
echo
echo "All screenshots have been saved to the '$SCREENSHOTS_DIR' directory."
echo "Please review the captured images and retake any that need improvement."
echo
echo "Next steps:"
echo "1. Review all screenshots for quality and content"
echo "2. Optimize image file sizes if needed"
echo "3. Commit the screenshots to the repository"
echo
echo "Thank you for contributing to the documentation!"