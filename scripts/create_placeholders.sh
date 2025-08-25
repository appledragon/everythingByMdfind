#!/bin/bash

# Create placeholder screenshots for documentation
# This creates simple placeholder images until real macOS screenshots are available

SCREENSHOTS_DIR="screenshots"
WIDTH=800
HEIGHT=600

# Create the directory if it doesn't exist
mkdir -p "$SCREENSHOTS_DIR"

# Function to create SVG placeholder
create_placeholder() {
    local filename="$1"
    local title="$2"
    local description="$3"
    
    cat > "$SCREENSHOTS_DIR/$filename" << EOF
<svg width="$WIDTH" height="$HEIGHT" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#f0f0f0;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#e0e0e0;stop-opacity:1" />
    </linearGradient>
  </defs>
  
  <!-- Background -->
  <rect width="100%" height="100%" fill="url(#bg)" stroke="#ccc" stroke-width="2"/>
  
  <!-- Title -->
  <text x="50%" y="30%" text-anchor="middle" font-family="Arial, sans-serif" font-size="24" font-weight="bold" fill="#333">
    $title
  </text>
  
  <!-- Description -->
  <text x="50%" y="45%" text-anchor="middle" font-family="Arial, sans-serif" font-size="16" fill="#666">
    $description
  </text>
  
  <!-- Placeholder indicator -->
  <text x="50%" y="70%" text-anchor="middle" font-family="Arial, sans-serif" font-size="14" fill="#999">
    📸 Screenshot Placeholder
  </text>
  
  <!-- Frame -->
  <rect x="10" y="10" width="$(($WIDTH-20))" height="$(($HEIGHT-20))" fill="none" stroke="#ddd" stroke-width="1" stroke-dasharray="5,5"/>
</svg>
EOF
}

echo "Creating placeholder screenshots..."

# Core Interface
create_placeholder "01-main-interface-light.png" "Main Interface - Light Mode" "Clean, intuitive interface in light theme"
create_placeholder "02-main-interface-dark.png" "Main Interface - Dark Mode" "Elegant dark theme for low-light environments"

# Search Functionality
create_placeholder "03-basic-search.png" "Basic Search" "Instant file search with real-time results"
create_placeholder "04-content-search.png" "Content Search" "Search inside file contents using Spotlight"
create_placeholder "05-advanced-filters.png" "Advanced Filters" "Comprehensive filtering options"
create_placeholder "06-directory-specific-search.png" "Directory Search" "Limit search to specific directories"

# Multi-Tab Interface
create_placeholder "07-multiple-tabs.png" "Multi-Tab Interface" "Multiple search sessions simultaneously"
create_placeholder "08-tab-management.png" "Tab Management" "Tab context menu and controls"

# Preview System
create_placeholder "09-preview-panel-text.png" "Text Preview" "Preview text files with encoding detection"
create_placeholder "10-preview-panel-image.png" "Image Preview" "Image preview with metadata information"
create_placeholder "11-preview-panel-video.png" "Video Preview" "Video preview with playback controls"

# Media Integration
create_placeholder "12-media-player-integrated.png" "Integrated Media Player" "Built-in media playback controls"
create_placeholder "13-media-player-standalone.png" "Standalone Player" "Separate media player window"

# File Operations
create_placeholder "14-context-menu.png" "Context Menu" "File operations and actions"
create_placeholder "15-multi-select.png" "Multi-Select" "Batch operations on multiple files"

# Quick Access
create_placeholder "16-bookmarks-menu.png" "Bookmarks Menu" "Quick access to common search types"
create_placeholder "17-large-files-search.png" "Large Files Search" "Find files larger than 50MB"

# Organization
create_placeholder "18-sorting-options.png" "Sorting Options" "Organize results by various criteria"
create_placeholder "19-lazy-loading.png" "Lazy Loading" "Efficient handling of large result sets"

# Data Operations
create_placeholder "20-csv-export.png" "CSV Export" "Export search results for analysis"
create_placeholder "21-path-operations.png" "Path Operations" "Copy paths and file information"

# Customization
create_placeholder "22-view-menu.png" "View Menu" "Interface customization options"
create_placeholder "23-search-history.png" "Search History" "Auto-completion and history"
create_placeholder "24-file-type-icons.png" "File Type Icons" "Emoji indicators for file types"

echo "✅ Created placeholder screenshots!"
echo "These SVG placeholders show the documentation structure."
echo "Run scripts/capture_screenshots.sh on macOS to capture real screenshots."