[English](README.md) | [中文](README_CN.md)

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
*   **Sortable Results:** Organize search results by name, size, date modified, or path.
*   **Multi-File Operations:** Perform actions on multiple files simultaneously:
    *   Multi-select files using Shift or Control (⌃) keys.
    *   Batch operations: Open, Delete, Copy, Move.
    *   Single-file operations: Open with VSCode, Copy paths.
    *   Open files in Finder.
*   **CSV Export:** Export search results to a CSV file for further analysis or record-keeping.
*   **Lazy Loading:** Handles large result sets efficiently by loading items in batches as you scroll.
*   **Drag & Drop:** Drag files directly to external applications (like VSCode).

## Usage

1.  Enter your search query in the "Search Query" field.
2.  Optionally, specify a directory to search within using the "Directory" field. Leave it empty to search everywhere.
3.  Use the "Advanced Filters" to refine your search based on file size, extension, and matching options.
4.  Click on the column headers ("Name", "Size", "Date Modified", "Path") to sort the results.
5.  Use Shift to select a range of files, or Command to select multiple individual files.
6.  Right-click on selected files to access the context menu with available actions.
7.  Drag selected files from the search results into other apps supporting drag & drop.

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

## Configuration

* **Dark Mode:** Enabled via the "Dark Mode" toggle in the View menu.
* **Search History:**  
  - The application remembers your search queries to provide auto-completion.  
  - You can disable search history via the "Enable History" toggle in the Help menu. When disabled, search queries will not be saved in the configuration file.
* **Preview Feature:**  
  - The application supports an integrated preview pane for files (text, image, or video).  
  - Toggle the preview display using the "Toggle Preview" option in the View menu.

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

0.0.1

## Acknowledgements

*   Thanks to the PyQt6 team for providing a powerful and versatile GUI framework.
*   Inspiration from other great file search tools.



![image](https://github.com/user-attachments/assets/2b372510-ece7-44b6-ab4e-5a1898318517)
