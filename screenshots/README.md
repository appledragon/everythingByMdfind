# Screenshots Directory

This directory contains demonstration screenshots for Everything by mdfind features.

## Screenshot Capture Guide for macOS Users

To capture high-quality screenshots for this documentation:

### Prerequisites
1. Ensure Everything by mdfind is installed and running
2. Have a variety of test files (documents, images, videos, audio) for demonstration
3. Ensure your macOS system has adequate test data indexed by Spotlight

### Capture Instructions

#### Using Built-in Screenshot Tools
```bash
# Capture specific window (Cmd+Shift+4, then Space, then click window)
# Or use Screenshot.app for more control

# For command line users:
screencapture -w -P screenshot-name.png  # Capture window with shadow
screencapture -W -P screenshot-name.png  # Capture window without shadow
```

#### Automated Screenshot Capture Script
A script to help automate screenshot capture is provided in `scripts/capture_screenshots.sh`

### Screenshot Requirements

#### Image Specifications
- **Format**: PNG (for transparency and quality)
- **Resolution**: Minimum 1920x1080, preferably 2560x1440 for Retina
- **Compression**: Use PNG compression level 6-9 for optimal file size
- **Color**: RGB color space

#### UI Guidelines
- Use realistic file names and content (no personal/sensitive data)
- Ensure consistent window sizing across related screenshots
- Capture both light and dark modes where applicable
- Include realistic search results with varied file types
- Show meaningful search queries and results

#### Content Preparation
Before capturing screenshots, prepare:
- Various file types (images, videos, audio, documents)
- Files with different sizes (small, medium, large >50MB)
- Sample text documents with searchable content
- Mixed file extensions (.pdf, .docx, .mp4, .jpg, etc.)

### Current Screenshots

#### Core Interface
- [ ] `01-main-interface-light.png` - Main interface in light mode
- [ ] `02-main-interface-dark.png` - Main interface in dark mode

#### Search Functionality  
- [ ] `03-basic-search.png` - Basic text search in action
- [ ] `04-content-search.png` - Content-based search results
- [ ] `05-advanced-filters.png` - Advanced filtering options
- [ ] `06-directory-specific-search.png` - Directory-limited search

#### Multi-Tab Interface
- [ ] `07-multiple-tabs.png` - Multiple search tabs open
- [ ] `08-tab-management.png` - Tab context menu

#### Preview System
- [ ] `09-preview-panel-text.png` - Text file preview
- [ ] `10-preview-panel-image.png` - Image preview with metadata
- [ ] `11-preview-panel-video.png` - Video preview with controls

#### Media Integration
- [ ] `12-media-player-integrated.png` - Integrated media player
- [ ] `13-media-player-standalone.png` - Standalone player window

#### File Operations
- [ ] `14-context-menu.png` - File context menu
- [ ] `15-multi-select.png` - Multiple file selection

#### Quick Access
- [ ] `16-bookmarks-menu.png` - Bookmarks dropdown menu
- [ ] `17-large-files-search.png` - Large files search results

#### Organization
- [ ] `18-sorting-options.png` - Column sorting demonstration
- [ ] `19-lazy-loading.png` - Large result set with loading

#### Data Operations
- [ ] `20-csv-export.png` - CSV export dialog
- [ ] `21-path-operations.png` - Path copy operations

#### Customization
- [ ] `22-view-menu.png` - View menu options
- [ ] `23-search-history.png` - Search history dropdown
- [ ] `24-file-type-icons.png` - File type emoji icons

## Contributing Screenshots

If you're contributing screenshots:

1. Follow the naming convention: `##-feature-description.png`
2. Ensure screenshots are high quality and clearly demonstrate the feature
3. Include a brief description in your pull request
4. Test that the screenshot renders correctly in the documentation

## Optimization

Before committing screenshots:
- Optimize PNG files using tools like ImageOptim or pngcrush
- Keep file sizes reasonable (< 2MB per image when possible)
- Ensure images are accessible and have good contrast

## Placeholder Images

Currently using placeholder images that should be replaced with actual screenshots on macOS.