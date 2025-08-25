#!/usr/bin/env python3

"""
Create placeholder PNG images for documentation
This creates simple placeholder images until real macOS screenshots are available
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_placeholder_png(filename, title, description, width=800, height=600):
    """Create a placeholder PNG image with title and description"""
    
    # Create image with light gray background
    img = Image.new('RGB', (width, height), color='#f5f5f5')
    draw = ImageDraw.Draw(img)
    
    # Try to use a system font, fallback to default
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 32)
        desc_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 18)
        small_font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 14)
    except:
        # Fallback for non-macOS systems
        try:
            title_font = ImageFont.truetype("arial.ttf", 32)
            desc_font = ImageFont.truetype("arial.ttf", 18)
            small_font = ImageFont.truetype("arial.ttf", 14)
        except:
            title_font = ImageFont.load_default()
            desc_font = ImageFont.load_default()
            small_font = ImageFont.load_default()
    
    # Draw border
    draw.rectangle([(10, 10), (width-10, height-10)], outline='#ddd', width=2)
    draw.rectangle([(20, 20), (width-20, height-20)], outline='#eee', width=1)
    
    # Calculate text positions
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    title_x = (width - title_width) // 2
    title_y = height // 3
    
    desc_bbox = draw.textbbox((0, 0), description, font=desc_font)
    desc_width = desc_bbox[2] - desc_bbox[0]
    desc_x = (width - desc_width) // 2
    desc_y = title_y + 60
    
    placeholder_text = "📸 Screenshot Placeholder"
    placeholder_bbox = draw.textbbox((0, 0), placeholder_text, font=small_font)
    placeholder_width = placeholder_bbox[2] - placeholder_bbox[0]
    placeholder_x = (width - placeholder_width) // 2
    placeholder_y = height * 2 // 3
    
    # Draw text
    draw.text((title_x, title_y), title, fill='#333', font=title_font)
    draw.text((desc_x, desc_y), description, fill='#666', font=desc_font)
    draw.text((placeholder_x, placeholder_y), placeholder_text, fill='#999', font=small_font)
    
    # Add app icon placeholder
    icon_size = 64
    icon_x = (width - icon_size) // 2
    icon_y = height // 6
    draw.rectangle([(icon_x, icon_y), (icon_x + icon_size, icon_y + icon_size)], 
                   outline='#ccc', fill='#e8e8e8', width=2)
    draw.text((icon_x + 20, icon_y + 20), "🔍", font=title_font)
    
    return img

def main():
    """Create all placeholder images"""
    screenshots_dir = "screenshots"
    os.makedirs(screenshots_dir, exist_ok=True)
    
    screenshots = [
        ("01-main-interface-light.png", "Main Interface - Light Mode", "Clean, intuitive interface in light theme"),
        ("02-main-interface-dark.png", "Main Interface - Dark Mode", "Elegant dark theme for low-light environments"),
        ("03-basic-search.png", "Basic Search", "Instant file search with real-time results"),
        ("04-content-search.png", "Content Search", "Search inside file contents using Spotlight"),
        ("05-advanced-filters.png", "Advanced Filters", "Comprehensive filtering options"),
        ("06-directory-specific-search.png", "Directory Search", "Limit search to specific directories"),
        ("07-multiple-tabs.png", "Multi-Tab Interface", "Multiple search sessions simultaneously"),
        ("08-tab-management.png", "Tab Management", "Tab context menu and controls"),
        ("09-preview-panel-text.png", "Text Preview", "Preview text files with encoding detection"),
        ("10-preview-panel-image.png", "Image Preview", "Image preview with metadata information"),
        ("11-preview-panel-video.png", "Video Preview", "Video preview with playback controls"),
        ("12-media-player-integrated.png", "Integrated Media Player", "Built-in media playback controls"),
        ("13-media-player-standalone.png", "Standalone Player", "Separate media player window"),
        ("14-context-menu.png", "Context Menu", "File operations and actions"),
        ("15-multi-select.png", "Multi-Select", "Batch operations on multiple files"),
        ("16-bookmarks-menu.png", "Bookmarks Menu", "Quick access to common search types"),
        ("17-large-files-search.png", "Large Files Search", "Find files larger than 50MB"),
        ("18-sorting-options.png", "Sorting Options", "Organize results by various criteria"),
        ("19-lazy-loading.png", "Lazy Loading", "Efficient handling of large result sets"),
        ("20-csv-export.png", "CSV Export", "Export search results for analysis"),
        ("21-path-operations.png", "Path Operations", "Copy paths and file information"),
        ("22-view-menu.png", "View Menu", "Interface customization options"),
        ("23-search-history.png", "Search History", "Auto-completion and history"),
        ("24-file-type-icons.png", "File Type Icons", "Emoji indicators for file types"),
    ]
    
    print("Creating placeholder PNG screenshots...")
    
    for filename, title, description in screenshots:
        filepath = os.path.join(screenshots_dir, filename)
        img = create_placeholder_png(filename, title, description)
        img.save(filepath, 'PNG', optimize=True)
        print(f"✅ Created: {filename}")
    
    print(f"\n🎉 Created {len(screenshots)} placeholder screenshots!")
    print("These placeholders show the documentation structure.")
    print("Run scripts/capture_screenshots.sh on macOS to capture real screenshots.")

if __name__ == "__main__":
    main()