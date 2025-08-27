[English](README.md) | [中文](README_CN.md) | [한국어](README_KO.md) | [日本語](README_JP.md)

<img width="1920" height="1080" alt="everything" src="https://github.com/user-attachments/assets/84dc4f48-201f-40f5-8b2b-9f8f6070a9b2" />

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
    *   Toggle between light and dark mode
    *   Show/hide preview panel
    *   Configurable search history
*   **CSV Export:** Export search results to a CSV file for further analysis or record-keeping.
*   **Lazy Loading:** Handles large result sets efficiently by loading items in batches as you scroll.
*   **Drag & Drop:** Drag files directly to external applications.
*   **Path Operations:** Copy file path, directory path, or filename to clipboard.

## Usage

1.  Enter your search query in the "Search Query" field.
2.  Optionally, specify a directory to search within using the "Directory" field. Leave it empty to search everywhere.
3.  Use the "Advanced Filters" to refine your search based on file size, extension, and matching options.
4.  Click on the column headers ("Name", "Size", "Date Modified", "Path") to sort the results.
5.  Toggle the Preview panel using the View menu to preview selected files.
6.  Use Bookmarks menu to quickly search for specific file types like videos, audio, images, applications, etc.
7.  Right-click on selected files to access the context menu with available actions.
8.  Drag selected files from the search results into other apps supporting drag & drop.
9.  For media files, use the integrated player controls or open in a standalone player window.
10. Toggle dark mode from the View menu for a more comfortable experience in low-light environments.

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
            'CFBundleVersion': '1.3.3',
            'CFBundleShortVersionString': '1.3.3',
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

1.3.3

## Acknowledgements

*   Thanks to the PyQt6 team for providing a powerful and versatile GUI framework.
*   Inspiration from other great file search tools.


