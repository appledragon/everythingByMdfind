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
*   **Bookmarks:** Quick access to common searches:
    *   Large Files (>50MB)
    *   Video Files
    *   Audio Files
    *   Images
    *   Archives
*   **Sortable Results:** Organize search results by name, size, date modified, or path.
*   **Multi-File Operations:** Perform actions on multiple files simultaneously:
    *   Multi-select files using Shift or Command (⌘) keys
    *   Batch operations: Open, Delete, Copy, Move, Rename
    *   Context menu for additional operations
*   **Customizable Interface:**
    *   Toggle between light and dark mode
    *   Show/hide preview panel
    *   Configurable search history
*   **CSV Export:** Export search results to a CSV file for further analysis or record-keeping.
*   **Lazy Loading:** Handles large result sets efficiently by loading items in batches as you scroll.
*   **Drag & Drop:** Drag files directly to external applications.

## Usage

1.  Enter your search query in the "Search Query" field.
2.  Optionally, specify a directory to search within using the "Directory" field. Leave it empty to search everywhere.
3.  Use the "Advanced Filters" to refine your search based on file size, extension, and matching options.
4.  Click on the column headers ("Name", "Size", "Date Modified", "Path") to sort the results.
5.  Toggle the Preview panel using the View menu to preview selected files.
6.  Use Bookmarks menu to quickly search for specific file types.
7.  Right-click on selected files to access the context menu with available actions.
8.  Drag selected files from the search results into other apps supporting drag & drop.

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

You can use PyInstaller to create a standalone application:

1.  **Install PyInstaller:**

    ```bash
    pip install pyinstaller
    ```

2.  **Create the standalone application:**

    ```bash
    pyinstaller --onefile everything.py
    ```

    The executable will be located in the `dist` directory.

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bug fixes, feature requests, or general improvements.

## License

This project is licensed under the [MIT] License - see the [LICENSE.md](LICENSE.md) file for details.

## Author

Apple Dragon

## Version

1.0.0

## Acknowledgements

*   Thanks to the PyQt6 team for providing a powerful and versatile GUI framework.
*   Inspiration from other great file search tools.

![image](https://github.com/user-attachments/assets/2b372510-ece7-44b6-ab4e-5a1898318517)

