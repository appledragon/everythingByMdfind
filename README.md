[English](README.md) | [中文](README_CN.md) | [한국어](README_KO.md) | [日本語](README_JP.md) | [Français](README_FR.md) | [Deutsch](README_DE.md) | [Español](README_ES.md)

<img width="3836" height="2026" alt="image" src="https://github.com/user-attachments/assets/d86c3d6b-6fd4-4cfe-b64f-67c465bb3d3c" /><img width="3832" height="2024" alt="image" src="https://github.com/user-attachments/assets/a91d2b13-07ac-4cae-ab33-506f1fa3bca6" />


# Everything by mdfind

A powerful and efficient file search tool for macOS, leveraging the native Spotlight engine for lightning-fast results.

## Key Features

*   **Blazing Fast Search:** Utilizes the macOS Spotlight index for near-instantaneous file searching.
*   **Flexible Search Options:** Search by file name or content to quickly locate the files you need.
*   **Advanced Filtering:** Refine your searches with a variety of filters:
    *   File size range (minimum and maximum size in bytes)
    *   Specific file extensions (e.g., `pdf`, `docx`)
    *   Case-sensitive matching
    *   Full or partial match options
*   **Directory-Specific Search:** Limit your search to a specific directory for focused results.
*   **Rich Preview:** Preview various file types directly in the application:
    *   Text files with encoding detection
    *   Images (JPEG, PNG, GIF with animation support, BMP, WEBP, HEIC)
    *   SVG files with proper scaling and centering
    *   Video files with playback controls
    *   Audio files
*   **Integrated Media Player:**
    *   Video and audio playback with standard controls
    *   Standalone player window for media files
    *   Continuous playback mode
    *   Volume control and mute option
*   **Bookmarks:** Quick access to common searches:
    *   Large Files (>50MB)
    *   Video Files
    *   Audio Files
    *   Images
    *   Archives
    *   Applications
*   **Sortable Results:** Organize search results by name, size, date modified, or path.
*   **Multi-File Operations:** Perform actions on multiple files simultaneously:
    *   Multi-select files using Shift or Command (⌘) keys
    *   Batch operations: Open, Delete, Copy, Move, Rename
    *   Context menu for additional operations
*   **Multi-Tab Search Interface:** Work with multiple search sessions simultaneously:
    *   Create new tabs for different search queries
    *   Close, reorder, and manage tabs with right-click context menu
    *   Independent search results and settings per tab
    *   Chrome-like tab experience with scroll buttons for many tabs
*   **Customizable Interface:**
    *   6 beautiful themes to choose from:
        *   Light & Dark (system default)
        *   Tokyo Night & Tokyo Night Storm
        *   Chinolor Dark & Chinolor Light (Chinese traditional colors)
    *   System title bar theming that matches your selected theme
    *   Show/hide preview panel
    *   Configurable search history
*   **Multi-Format Export:** Export search results to multiple formats:
    *   JSON - Structured data format
    *   Excel (.xlsx) - Spreadsheet with formatting
    *   HTML - Web-ready table format
    *   Markdown - Documentation-friendly format
    *   CSV - Classic comma-separated values
*   **Lazy Loading:** Handles large result sets efficiently by loading items in batches as you scroll.
*   **Drag & Drop:** Drag files directly to external applications.
*   **Path Operations:** Copy file path, directory path, or filename to clipboard.

## Installation

1.  **Prerequisites:**
    *   Python 3.6+
    *   PyQt6

2.  **Clone the repository:**

    ```bash
    git clone https://github.com/appledragon/everythingByMdfind
    cd everythingByMdfind
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Run the application:**

    ```bash
    python everything.py
    ```

## Building a Standalone Application (Optional)

You can use py2app to create a standalone macOS application:

1.  **Install py2app:**

    ```bash
    pip install py2app
    ```

2.  **Create setup.py:**

    ```bash
    cat > setup.py << 'EOF'
    from setuptools import setup

    APP = ['everything.py']
    DATA_FILES = [
        ('', ['LICENSE.md', 'README.md']),
    ]
    OPTIONS = {
        'argv_emulation': False,
        'packages': ['PyQt6'],
        'excludes': [],
        'plist': {
            'CFBundleName': 'Everything',
            'CFBundleDisplayName': 'Everything',
            'CFBundleVersion': '1.3.6',
            'CFBundleShortVersionString': '1.3.6',
            'CFBundleIdentifier': 'com.appledragon.everythingbymdfind',
            'LSMinimumSystemVersion': '10.14',
            'NSHighResolutionCapable': True,
        }
    }

    setup(
        app=APP,
        data_files=DATA_FILES,
        options={'py2app': OPTIONS},
        setup_requires=['py2app'],
    )
    EOF
    ```

3.  **Build the application:**

    ```bash
    python setup.py py2app
    ```

    The macOS app bundle will be located in the `dist` directory.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bug fixes, feature requests, or general improvements.

## License

This project is licensed under the [MIT] License - see the [LICENSE.md](LICENSE.md) file for details.

## Author

Apple Dragon

## Version

1.3.6

## Acknowledgements

*   Thanks to the PyQt6 team for providing a powerful and versatile GUI framework.
*   Inspiration from other great file search tools.


