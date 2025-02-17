import sys
import os
import json
import subprocess
import time
import csv
import shutil

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QCheckBox, QPushButton, QTreeWidget, QTreeWidgetItem, QProgressBar, QMenu,
    QFileDialog, QMessageBox, QGroupBox, QInputDialog, QPlainTextEdit, QSplitter, QStackedWidget, QCompleter
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QUrl, QMimeData
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtGui import QPixmap

CONFIG_PATH = os.path.expanduser("~/.everythingByMdfind.json")
DEBOUNCE_DELAY = 800

def read_config():
    if not os.path.isfile(CONFIG_PATH):
        return {}
    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def write_config(data):
    try:
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except:
        pass


# Custom QTreeWidget to support drag and drop of files to external applications
class DraggableTreeWidget(QTreeWidget):
    """Custom QTreeWidget to support drag and drop of files to external applications"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragEnabled(True)

    def mimeTypes(self):
        return ['text/uri-list']

    def mimeData(self, items):
        mime_data = QMimeData()
        urls = []
        for item in items:
            path = item.text(3)  # column 3 is the full path
            urls.append(QUrl.fromLocalFile(path))
        mime_data.setUrls(urls)
        return mime_data


# Convert file size to a human-readable string
def format_size(size):
    """Convert file size to a human-readable string"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size < 1024:
            return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} TB"


# Thread class to run mdfind in the background.
# Reads results line by line based on search parameters and sends them to the main thread.
class SearchWorker(QThread):
    """Thread class to run mdfind in the background.
    Reads results line by line based on search parameters and sends them to the main thread."""
    progress_signal = pyqtSignal(int)
    result_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)
    
    def __init__(self, query, directory, search_by_file_name, match_case, full_match):
        super().__init__()
        self.query = query
        self.directory = directory
        self.search_by_file_name = search_by_file_name
        self.match_case = match_case
        self.full_match = full_match
        self._is_running = True
        self.process = None

    def run(self):
        files_info = []
        idx = 0

        cmd = ["mdfind"]

        # Construct search query pattern
        full_match_str = "" if self.full_match else "*"
        case_modifier = "" if self.match_case else "cd"

        if self.search_by_file_name:
            query_str = f'kMDItemFSName == "{full_match_str}{self.query}{full_match_str}"{case_modifier}'
        else:
            query_str = f'kMDItemTextContent == "{full_match_str}{self.query}{full_match_str}"{case_modifier}'
        cmd.append(query_str)

        if self.directory:
            dir_expanded = os.path.expanduser(self.directory)
            cmd.extend(["-onlyin", dir_expanded])

        try:
            self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        except Exception as e:
            self.error_signal.emit(str(e))
            return

        try:
            while self._is_running:
                line = self.process.stdout.readline()
                if not line:
                    break
                idx += 1
                path = line.strip()
                if path and os.path.isfile(path):
                    try:
                        size_ = os.path.getsize(path)
                        mtime = os.path.getmtime(path)
                        files_info.append((os.path.basename(path), size_, mtime, path))
                    except Exception as e:
                        print(f"Error processing file {path}: {e}")
                if idx % 10 == 0:
                    self.progress_signal.emit(min(100, idx % 100))
            self.process.wait()
            self.result_signal.emit(files_info)
        except Exception as e:
            self.error_signal.emit(str(e))
        finally:
            self.progress_signal.emit(0)

    def stop(self):
        self._is_running = False
        if self.process is not None:
            try:
                self.process.terminate()
            except Exception:
                pass


class MdfindApp(QMainWindow):
    def __init__(self):
        super().__init__()
        # Load dark mode and history settings from config
        config = read_config()
        self.dark_mode = config.get("dark_mode", False)
        self.history_enabled = config.get("history_enabled", True)
        self.setWindowTitle("Everything by mdfind")
        size = config.get("window_size", {"width": 1920, "height": 1080})
        self.resize(size["width"], size["height"])

        # ========== Menu Bar ==========
        menubar = self.menuBar()
        help_menu = menubar.addMenu('Help')
        about_action = help_menu.addAction('About')
        about_action.triggered.connect(self.show_about_dialog)

        # Add a "History" menu
        history_menu = menubar.addMenu('History')
        clear_history_action = history_menu.addAction('Clear History')
        clear_history_action.triggered.connect(self.clear_history)
        enable_history_action = history_menu.addAction("Enable History")
        enable_history_action.setCheckable(True)
        enable_history_action.setChecked(self.history_enabled)
        enable_history_action.triggered.connect(self.toggle_history)

        # Add a "View" menu
        view_menu = menubar.addMenu('View')
        toggle_preview_action = view_menu.addAction('Toggle Preview')
        toggle_preview_action.setCheckable(True)
        toggle_preview_action.setChecked(False)
        toggle_preview_action.triggered.connect(self.toggle_preview)
        # Added dark mode toggle action in the View menu
        dark_mode_action = view_menu.addAction('Dark Mode')
        dark_mode_action.setCheckable(True)
        dark_mode_action.setChecked(self.dark_mode)
        dark_mode_action.triggered.connect(self.toggle_dark_mode)
        if self.dark_mode:
            self.set_dark_mode()
        else:
            self.set_non_dark_mode()
        # Search thread variables
        self.search_worker = None
        self.all_file_data = []
        self.file_data = []
        self.ignore_no_results = False

        # ======= Main layout: QSplitter, left for search/list and right for preview ===========
        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Orientation.Horizontal)
        self.setCentralWidget(splitter)

        # ========== Left side ==========
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)

        # First row: Search Query input and statistics
        form_layout = QHBoxLayout()
        lbl_query = QLabel("Search Query:")
        self.edit_query = QLineEdit()
        self.lbl_items_found = QLabel("0 items found")

        form_layout.addWidget(lbl_query)
        form_layout.addWidget(self.edit_query, 3)
        form_layout.addWidget(self.lbl_items_found, 1)
        left_layout.addLayout(form_layout)

        # Second row: Directory selection (optional)
        form_layout2 = QHBoxLayout()
        lbl_dir = QLabel("Directory (optional):")
        self.edit_dir = QLineEdit()
        self.edit_dir.setPlaceholderText(" Leave empty to search everywhere")
        btn_select_dir = QPushButton("Select Dir")
        btn_select_dir.clicked.connect(self.select_directory)

        form_layout2.addWidget(lbl_dir)
        form_layout2.addWidget(self.edit_dir, 3)
        form_layout2.addWidget(btn_select_dir, 1)
        left_layout.addLayout(form_layout2)

        # Advanced Filters group
        group_advanced = QGroupBox("Advanced Filters")
        adv_layout = QHBoxLayout()

        lbl_min_size = QLabel("Min Size (bytes):")
        self.edit_min_size = QLineEdit()
        lbl_max_size = QLabel("Max Size (bytes):")
        self.edit_max_size = QLineEdit()
        lbl_extension = QLabel("File Extension:")
        self.edit_extension = QLineEdit()
        self.edit_extension.setPlaceholderText(" e.g., pdf;docx")

        self.chk_file_name = QCheckBox("Search by File Name")
        self.chk_file_name.setChecked(True)
        self.chk_match_case = QCheckBox("Match Case")
        self.chk_full_match = QCheckBox("Full Match")

        adv_layout.addWidget(lbl_min_size, 1)
        adv_layout.addWidget(self.edit_min_size, 2)
        adv_layout.addWidget(lbl_max_size, 1)
        adv_layout.addWidget(self.edit_max_size, 2)
        adv_layout.addWidget(lbl_extension, 1)
        adv_layout.addWidget(self.edit_extension, 2)
        adv_layout.addWidget(self.chk_file_name, 2)
        adv_layout.addWidget(self.chk_match_case, 2)
        adv_layout.addWidget(self.chk_full_match, 2)

        group_advanced.setLayout(adv_layout)
        left_layout.addWidget(group_advanced)

        # Search results list
        self.tree = DraggableTreeWidget()
        self.tree.setColumnCount(4)
        self.tree.setHeaderLabels(["Name", "Size", "Date Modified", "Path"])
        self.tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        self.tree.setSelectionBehavior(QTreeWidget.SelectionBehavior.SelectRows)
        self.tree.setSortingEnabled(False)
        self.tree.setColumnWidth(0, 200)
        self.tree.setColumnWidth(1, 80)
        self.tree.setColumnWidth(2, 150)
        self.tree.setColumnWidth(3, 400)
        self.tree.header().setSectionsClickable(True)
        self.tree.header().setSortIndicatorShown(True)
        self.tree.header().sectionClicked.connect(self.on_header_clicked)
        left_layout.addWidget(self.tree, stretch=1)

        # Progress bar and Export button
        self.progress = QProgressBar()
        self.progress.setMaximum(100)
        left_layout.addWidget(self.progress)

        btn_export = QPushButton("Export to CSV")
        btn_export.clicked.connect(self.export_to_csv)
        left_layout.addWidget(btn_export, alignment=Qt.AlignmentFlag.AlignRight)

        splitter.addWidget(left_container)

        # ========== Right side Preview ==========
        self.preview_container = QWidget()
        preview_layout = QVBoxLayout(self.preview_container)
        
        # New header layout with Preview title and close button
        header_layout = QHBoxLayout()
        preview_title = QLabel("<b>Preview</b>")
        header_layout.addWidget(preview_title)
        header_layout.addStretch()
        preview_layout.addLayout(header_layout)
        
        # Create vertical splitter for preview (top) and metadata (bottom)
        self.preview_splitter = QSplitter(Qt.Orientation.Vertical)
        preview_layout.addWidget(self.preview_splitter, stretch=1)

        # Keep the existing QStackedWidget as top
        self.preview_stack = QStackedWidget()

        # 1) Text Preview
        self.text_preview = QPlainTextEdit()
        self.text_preview.setReadOnly(True)

        # 2) Image Preview: Fixed size, scale manually if needed
        self.image_label = QLabel()
        self.image_label.setFixedSize(500, 400)
        self.image_label.setScaledContents(False)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 3) Video Preview: Fixed size with aspect ratio maintained
        self.video_widget = QVideoWidget()
        self.video_widget.setFixedSize(500, 400)
        # If supported, try to maintain aspect ratio:
        self.video_widget.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)  # Available in some versions
        self.audio_output = QAudioOutput()
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setAudioOutput(self.audio_output)

        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)

        # Add to stack
        self.preview_stack.addWidget(self.text_preview)  # index 0
        self.preview_stack.addWidget(self.image_label)   # index 1
        self.preview_stack.addWidget(self.video_widget)  # index 2

        self.preview_splitter.addWidget(self.preview_stack)

        # Bottom pane: metadata info
        self.media_info = QPlainTextEdit()
        self.media_info.setReadOnly(True)
        self.preview_splitter.addWidget(self.media_info)

        splitter.addWidget(self.preview_container)
        splitter.setSizes([800, 400])  # Initial left-right ratio

        # Make the preview panel invisible by default
        self.preview_container.setVisible(False)

        # Load last sort settings from config
        config = read_config()
        self.sort_column = config.get("sort_column", -1)
        self.sort_order = Qt.SortOrder(config.get("sort_order", 0))  # 0 = Ascending, 1 = Descending

        # If there was a saved column, show it in the UI
        if self.sort_column != -1:
            self.tree.header().setSortIndicator(self.sort_column, self.sort_order)

        self.query_history = config.get("query_history", [])
        self.query_completer = QCompleter(self.query_history)
        self.query_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.edit_query.setCompleter(self.query_completer)

        # ========== Signal bindings ==========
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.start_search)
        self.edit_query.textChanged.connect(self.on_query_changed)
        self.edit_dir.textChanged.connect(self.on_dir_changed)

        self.chk_file_name.stateChanged.connect(lambda: self.search_timer.start(DEBOUNCE_DELAY))
        self.chk_match_case.stateChanged.connect(lambda: self.search_timer.start(DEBOUNCE_DELAY))
        self.chk_full_match.stateChanged.connect(lambda: self.search_timer.start(DEBOUNCE_DELAY))
        self.edit_min_size.textChanged.connect(self.reapply_filter)
        self.edit_max_size.textChanged.connect(self.reapply_filter)
        self.edit_extension.textChanged.connect(self.reapply_filter)
        self.tree.itemSelectionChanged.connect(self.on_tree_selection_changed)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.itemDoubleClicked.connect(self.open_with_default_app)

        self.single_context_menu = QMenu(self)
        self.single_context_menu.addAction("Open", self.open_with_default_app)
        self.single_context_menu.addAction("Delete", self.delete_file)
        self.single_context_menu.addAction("Copy to...", self.copy_file)
        self.single_context_menu.addAction("Move to...", self.move_file)
        self.single_context_menu.addAction("Rename", self.rename_file)
        self.single_context_menu.addAction("Copy full path with file name", self.copy_full_path)
        self.single_context_menu.addAction("Copy path without file name", self.copy_path_only)
        self.single_context_menu.addAction("Copy file name only", self.copy_file_name_only)
        self.single_context_menu.addAction("Open in Finder", self.open_in_finder)
        self.single_context_menu.addAction("Export to CSV", self.export_to_csv)

        self.multi_context_menu = QMenu(self)
        self.multi_context_menu.addAction("Open", self.open_multiple_files)
        self.multi_context_menu.addAction("Delete", self.delete_multiple_files)
        self.multi_context_menu.addAction("Copy to...", self.copy_multiple_files)
        self.multi_context_menu.addAction("Move to...", self.move_multiple_files)
        self.multi_context_menu.addAction("Batch Rename", self.batch_rename_files)

        self.batch_size = 100
        self.current_loaded = 0
        self.tree.verticalScrollBar().valueChanged.connect(self.check_scroll_position)

        # Recognizable extensions
        self.image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp"}
        self.video_extensions = {".mp4", ".mov", ".avi", ".mkv", ".mpg", ".mpeg"}

    # ========== Preview logic ==========
    def on_tree_selection_changed(self):
        # if preview is not visible, do nothing
        if not self.preview_container.isVisible():
            return
        
        selected_items = self.tree.selectedItems()
        if not selected_items or len(selected_items) != 1:
            # For multiple or no selection: stop video playback and clear preview
            self.media_player.stop()
            self.preview_stack.setCurrentIndex(0)
            self.text_preview.setPlainText("")
            self.media_info.setPlainText("")  # Clear bottom pane
            return

        path = selected_items[0].text(3)
        if not os.path.isfile(path):
            self.media_player.stop()
            self.preview_stack.setCurrentIndex(0)
            self.text_preview.setPlainText("No preview available.")
            self.media_info.setPlainText("")
            return

        # Stop previous video playback
        self.media_player.stop()

        # Display basic file info in the bottom pane
        file_stat = os.stat(path)
        size_kb = round(file_stat.st_size / 1024, 2)
        self.media_info.setPlainText(
            f"File: {path}\nSize: {size_kb} KB\nLast Modified: {time.ctime(file_stat.st_mtime)}"
        )

        # Check file extension
        _, ext = os.path.splitext(path)
        ext = ext.lower()

        if ext in self.image_extensions:
            pixmap = QPixmap(path)
            # Scale down using KeepAspectRatio if pixmap is larger than image_label
            if (pixmap.width() > self.image_label.width()) or (pixmap.height() > self.image_label.height()):
                pixmap = pixmap.scaled(
                    self.image_label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            self.image_label.setPixmap(pixmap)
            self.preview_stack.setCurrentIndex(1)

            # Show resolution info for images
            self.media_info.appendPlainText(
                f"Resolution: {pixmap.width()} x {pixmap.height()}"
            )

        elif ext in self.video_extensions:
            self.media_player.setSource(QUrl.fromLocalFile(path))
            self.media_player.play()
            self.preview_stack.setCurrentIndex(2)
        else:
            # Try to display as text
            try:
                with open(path, 'rb') as f:
                    chunk = f.read(512)
                chunk.decode('utf-8')
                with open(path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read(4096)
                self.text_preview.setPlainText(content)
                self.preview_stack.setCurrentIndex(0)
            except:
                self.text_preview.setPlainText("No preview available (not text, image, or video).")
                self.preview_stack.setCurrentIndex(0)
                
    def on_media_status_changed(self, status):
        if status == QMediaPlayer.MediaStatus.LoadedMedia:
            self.update_video_info()
            
    def update_video_info(self):
        size = self.media_player.videoSink().videoSize()
        duration_secs = self.media_player.duration() // 1000
        # Skip if resolution is invalid
        if size.width() <= 0 or size.height() <= 0:
            return
        self.media_info.appendPlainText(
            f"Resolution: {size.width()} x {size.height()}\n"
            f"Duration: {duration_secs} seconds"
        )

    # ========== Lazy loading ==========
    def check_scroll_position(self):
        scrollbar = self.tree.verticalScrollBar()
        if scrollbar.value() >= scrollbar.maximum() - 10:
            self.load_more_items()

    def load_more_items(self):
        if not self.file_data or self.current_loaded >= len(self.file_data):
            return
        end_idx = min(self.current_loaded + self.batch_size, len(self.file_data))
        items_to_load = self.file_data[self.current_loaded:end_idx]
        
        for item in items_to_load:
            name, size, mtime, path = item
            display_size = format_size(size)
            display_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
            tree_item = QTreeWidgetItem([name, display_size, display_time, path])
            self.tree.addTopLevelItem(tree_item)
        
        self.current_loaded = end_idx

    # ========== Search handling ==========
    def on_query_changed(self):
        self.search_timer.start(DEBOUNCE_DELAY)

    def on_dir_changed(self):
        self.search_timer.start(DEBOUNCE_DELAY)

    def start_search(self):
        query = self.edit_query.text().strip()
        directory = self.edit_dir.text().strip()
        if not query:
            self.tree.clear()
            self.lbl_items_found.setText("0 items found")
            return

        if self.search_worker is not None and self.search_worker.isRunning():
            self.search_worker.stop()
            self.search_worker.wait()

        self.ignore_no_results = False
        self.search_worker = SearchWorker(
            query, directory,
            self.chk_file_name.isChecked(),
            self.chk_match_case.isChecked(),
            self.chk_full_match.isChecked()
        )
        self.search_worker.progress_signal.connect(self.update_progress)
        self.search_worker.result_signal.connect(self.update_tree)
        self.search_worker.error_signal.connect(self.show_error)
        self.search_worker.start()

        # Only update history if enabled
        if self.history_enabled and query and query not in self.query_history:
            self.query_history.insert(0, query)
            if len(self.query_history) > 100:
                self.query_history.pop()
            cfg = read_config()
            cfg["query_history"] = self.query_history
            write_config(cfg)
            self.query_completer.model().setStringList(self.query_history)

    def update_progress(self, value):
        self.progress.setValue(value)

    def update_tree(self, files_info):
        self.tree.clear()
        self.all_file_data = files_info
        self.current_loaded = 0
        filtered_files = self.apply_filters_and_sorting(self.all_file_data)
        self.file_data = filtered_files
        
        if not filtered_files:
            if not self.ignore_no_results:
                self.show_info("Info", "No results found.")
            self.lbl_items_found.setText("0 items found")
            return
        
        self.lbl_items_found.setText(f"{len(filtered_files)} items found")

        if getattr(self, 'sort_column', -1) != -1:
            self.sort_data()
        else:
            self.load_more_items()

    def show_error(self, msg):
        self.show_critical("Error", msg)

    # ========== Filtering and sorting ==========
    def reapply_filter(self):
        if not self.all_file_data:
            return
        filtered_files = self.apply_filters_and_sorting(self.all_file_data)
        self.file_data = filtered_files
        self.tree.clear()
        self.current_loaded = 0

        if getattr(self, 'sort_column', -1) != -1:
            self.sort_data()
        else:
            self.load_more_items()

        self.lbl_items_found.setText(f"{len(filtered_files)} items found")

    def apply_filters_and_sorting(self, files_info):
        filtered = files_info[:]
        try:
            min_size = int(self.edit_min_size.text()) if self.edit_min_size.text() else None
        except ValueError:
            min_size = None
        try:
            max_size = int(self.edit_max_size.text()) if self.edit_max_size.text() else None
        except ValueError:
            max_size = None

        if min_size is not None:
            filtered = [item for item in filtered if item[1] >= min_size]
        if max_size is not None:
            filtered = [item for item in filtered if item[1] <= max_size]

        ext_text = self.edit_extension.text().strip()
        if ext_text:
            exts = []
            for part in ext_text.split(";"):
                part = part.strip()
                if part and not part.startswith("."):
                    part = "." + part
                if part:
                    exts.append(part.lower())
            if exts:
                filtered = [item for item in filtered if any(item[0].lower().endswith(e) for e in exts)]

        return filtered

    def on_header_clicked(self, column):
        if getattr(self, 'sort_column', -1) == column:
            self.sort_order = (Qt.SortOrder.DescendingOrder
                               if self.sort_order == Qt.SortOrder.AscendingOrder
                               else Qt.SortOrder.AscendingOrder)
        else:
            self.sort_column = column
            self.sort_order = Qt.SortOrder.AscendingOrder
        self.tree.header().setSortIndicator(column, self.sort_order)
        self.sort_data()
        write_config({
            "sort_column": self.sort_column,
            "sort_order": 1 if self.sort_order == Qt.SortOrder.DescendingOrder else 0
        })

    def sort_data(self):
        if not self.file_data or self.sort_column == -1:
            return

        def get_sort_key(item):
            if self.sort_column == 0:
                return item[0].lower()
            elif self.sort_column == 1:
                return float(item[1])
            elif self.sort_column == 2:
                return float(item[2])
            else:
                return item[3].lower()

        self.file_data.sort(
            key=get_sort_key,
            reverse=(self.sort_order == Qt.SortOrder.DescendingOrder)
        )
        self.tree.clear()
        self.current_loaded = 0
        self.load_more_items()

    # ========== Context menu logic ==========
    def show_context_menu(self, pos):
        selected_items = self.tree.selectedItems()
        if not selected_items:
            return
        if len(selected_items) == 1:
            self.tree.setCurrentItem(selected_items[0])
            self.single_context_menu.exec(self.tree.viewport().mapToGlobal(pos))
        else:
            self.multi_context_menu.exec(self.tree.viewport().mapToGlobal(pos))

    def get_selected_file(self):
        item = self.tree.currentItem()
        if item:
            return item.text(3)
        return None

    def get_selected_files(self):
        return [item.text(3) for item in self.tree.selectedItems()]

    # ========== File operations ==========
    def open_with_default_app(self):
        path = self.get_selected_file()
        if not path:
            return
        try:
            process = subprocess.Popen(["open", path], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            _, stderr = process.communicate()
            if process.returncode != 0:
                error_msg = stderr.decode('utf-8').strip()
                self.show_critical("Error", f"Could not open file: {error_msg}")
                reply = self.show_question(
                    "Open with Text Editor?",
                    "Would you like to open this file with TextEdit instead?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    subprocess.Popen(["open", "-a", "TextEdit", path])
        except Exception as e:
            self.show_critical("Error", f"Error opening file: {str(e)}")

    def open_multiple_files(self):
        for path in self.get_selected_files():
            try:
                subprocess.Popen(["open", path])
            except Exception as e:
                self.show_critical("Error", f"Could not open file {path}: {str(e)}")

    def delete_file(self):
        path = self.get_selected_file()
        if not path:
            return
        reply = self.show_question(
            "Delete",
            f"Are you sure you want to delete '{path}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                os.remove(path)
                index = self.tree.indexOfTopLevelItem(self.tree.currentItem())
                self.tree.takeTopLevelItem(index)
                self.show_info("Deleted", f"File '{path}' deleted.")
            except Exception as e:
                self.show_critical("Error", str(e))

    def delete_multiple_files(self):
        files = self.get_selected_files()
        if not files:
            return
        reply = self.show_question(
            "Delete Multiple Files",
            f"Are you sure you want to delete {len(files)} files?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            error_files = []
            for path in files:
                try:
                    os.remove(path)
                except Exception as e:
                    error_files.append(f"{path}: {str(e)}")
            for item in self.tree.selectedItems():
                index = self.tree.indexOfTopLevelItem(item)
                self.tree.takeTopLevelItem(index)
            if error_files:
                self.show_warning(
                    "Deletion Errors",
                    "Some files could not be deleted:\n" + "\n".join(error_files)
                )
            else:
                self.show_info("Success", f"Successfully deleted {len(files)} files.")

    def copy_file(self):
        path = self.get_selected_file()
        if not path:
            return
        dest = QFileDialog.getExistingDirectory(self, "Select Destination Directory")
        if dest:
            try:
                shutil.copy2(path, dest)
                self.show_info("Copied", f"File '{path}' copied to '{dest}'.")
            except Exception as e:
                self.show_critical("Error", str(e))

    def copy_multiple_files(self):
        files = self.get_selected_files()
        if not files:
            return
        dest = QFileDialog.getExistingDirectory(self, "Select Destination Directory")
        if not dest:
            return
        error_files = []
        success_count = 0
        for path in files:
            try:
                shutil.copy2(path, dest)
                success_count += 1
            except Exception as e:
                error_files.append(f"{path}: {str(e)}")
        if error_files:
            self.show_warning(
                "Copy Errors",
                f"Copied {success_count} files.\nErrors occurred with:\n" + "\n".join(error_files)
            )
        else:
            self.show_info("Success", f"Successfully copied {success_count} files to {dest}")

    def move_file(self):
        path = self.get_selected_file()
        if not path:
            return
        dest = QFileDialog.getExistingDirectory(self, "Select Destination Directory")
        if dest:
            try:
                shutil.move(path, dest)
                index = self.tree.indexOfTopLevelItem(self.tree.currentItem())
                self.tree.takeTopLevelItem(index)
                self.show_info("Moved", f"File '{path}' moved to '{dest}'.")
            except Exception as e:
                self.show_critical("Error", str(e))

    def move_multiple_files(self):
        files = self.get_selected_files()
        if not files:
            return
        dest = QFileDialog.getExistingDirectory(self, "Select Destination Directory")
        if not dest:
            return
        error_files = []
        success_count = 0
        for path in files:
            try:
                shutil.move(path, dest)
                success_count += 1
                for item in self.tree.selectedItems():
                    if item.text(3) == path:
                        index = self.tree.indexOfTopLevelItem(item)
                        self.tree.takeTopLevelItem(index)
            except Exception as e:
                error_files.append(f"{path}: {str(e)}")
        if error_files:
            self.show_warning(
                "Move Errors",
                f"Moved {success_count} files.\nErrors occurred with:\n" + "\n".join(error_files)
            )
        else:
            self.show_info("Success", f"Successfully moved {success_count} files to {dest}")

    def rename_file(self):
        path = self.get_selected_file()
        if not path:
            return
        directory = os.path.dirname(path)
        old_name = os.path.basename(path)
        new_name, ok = QInputDialog.getText(self, "Rename File", f"Enter new name for {old_name}:")
        if ok and new_name:
            new_full_path = os.path.join(directory, new_name)
            try:
                os.rename(path, new_full_path)
                current_item = self.tree.currentItem()
                current_item.setText(0, new_name)
                current_item.setText(3, new_full_path)
                self.show_info("Success", "File renamed successfully.")
            except Exception as e:
                self.show_critical("Error", f"Could not rename file: {str(e)}")

    def batch_rename_files(self):
        files = self.get_selected_files()
        if not files:
            return
        prefix, ok_prefix = QInputDialog.getText(self, "Batch Rename", "Enter prefix (optional):")
        if not ok_prefix:
            return
        suffix, ok_suffix = QInputDialog.getText(self, "Batch Rename", "Enter suffix (optional):")
        if not ok_suffix:
            return

        error_files = []
        success_count = 0
        selected_items = self.tree.selectedItems()

        for item in selected_items:
            old_path = item.text(3)
            old_name = os.path.basename(old_path)
            directory = os.path.dirname(old_path)
            base_name, ext = os.path.splitext(old_name)
            new_name = f"{prefix}{base_name}{suffix}{ext}"
            new_full_path = os.path.join(directory, new_name)
            try:
                os.rename(old_path, new_full_path)
                success_count += 1
                item.setText(0, new_name)
                item.setText(3, new_full_path)
            except Exception as e:
                error_files.append(f"{old_path} -> {new_full_path}: {str(e)}")

        if error_files:
            self.show_warning(
                "Batch Rename Errors",
                f"Renamed {success_count} files.\nErrors:\n" + "\n".join(error_files)
            )
        else:
            self.show_info("Success", f"Successfully renamed {success_count} files.")

    # ========== Copy path to clipboard ==========
    def copy_full_path(self):
        path = self.get_selected_file()
        if not path:
            return
        QApplication.clipboard().setText(path)
        self.show_info("Copied", "Full path copied to clipboard.")

    def copy_path_only(self):
        path = self.get_selected_file()
        if not path:
            return
        directory = os.path.dirname(path)
        QApplication.clipboard().setText(directory)
        self.show_info("Copied", "Directory path copied to clipboard.")

    def copy_file_name_only(self):
        path = self.get_selected_file()
        if not path:
            return
        filename = os.path.basename(path)
        QApplication.clipboard().setText(filename)
        self.show_info("Copied", "File name copied to clipboard.")

    # ========== Export to CSV ==========
    def export_to_csv(self):
        if not self.file_data:
            self.show_warning("Warning", "No data to export.")
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Export to CSV", "", "CSV Files (*.csv);;All Files (*)")
        if not file_path:
            return
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Name', 'Size', 'Modification Time', 'Path'])
                for item in self.file_data:
                    writer.writerow(item)
            self.show_info("Success", f"Results exported to {file_path}")
        except Exception as e:
            self.show_critical("Error", str(e))

    # ========== Miscellaneous ==========
    def open_in_finder(self):
        path = self.get_selected_file()
        if not path:
            return
        try:
            subprocess.Popen(["open", "-R", path])
        except Exception as e:
            self.show_critical("Error", f"Could not open Finder: {e}")

    def select_directory(self):
        current = os.path.expanduser(self.edit_dir.text())
        directory = QFileDialog.getExistingDirectory(self, "Select Directory", current)
        if directory:
            self.edit_dir.setText(directory)
            self.start_search()

    def toggle_preview(self, checked):
        self.preview_container.setVisible(checked)
    
    def set_non_dark_mode(self):
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #ffffff, stop: 1 #e0e0e0
                );
                color: #000000;
                font-family: "Helvetica Neue", sans-serif;
                font-size: 11pt;
            }
            QLabel, QTreeWidget, QPlainTextEdit, QCheckBox {
                color: #000000;
                background: transparent;
            }
            QPushButton {
                background-color: #e0e0e0;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
                color: #000000;
            }
            QPushButton:hover {
                background-color: #d0d0d0;
            }
            QLineEdit {
                border: 1px solid #c0c0c0;
                padding: 4px;
                border-radius: 4px;
                background: #ffffff;
                color: #000000;
            }
            QLineEdit:focus {
                border: 1px solid #007acc;
            }
            QSplitter::handle {
                background-color: #d0d0d0;
            }
            QSplitter::handle:hover {
                background-color: #c0c0c0;
            }
            QMenuBar {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #ffffff, stop: 1 #f0f0f0
                );
                color: #000000;
            }
            QMenuBar::item {
                background-color: transparent;
                color: #000000;
            }
            QMenuBar::item:selected {
                background-color: #e0e0e0;
            }
            QMenu {
                background-color: #ffffff;
                color: #000000;
                border: 1px solid #c0c0c0;
            }
            QMenu::item:selected {
                background-color: #e0e0e0;
            }
            QMessageBox {
                background-color: #ffffff;
                color: #000000;
            }
            QMessageBox QLabel {
                color: #000000;
                background-color: transparent;
            }
            QMessageBox QPushButton {
                background-color: #e0e0e0;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                color: #000000;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #d0d0d0;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                color: #000000;
                padding: 4px;
                border: none;
                border-right: 1px solid #c0c0c0;
                border-bottom: 1px solid #c0c0c0;
            }
            QHeaderView::section:hover {
                background-color: #e0e0e0;
            }
            QHeaderView::section:checked {
                background-color: #e0e0e0;
            }
        """)
    
    def set_dark_mode(self):
        self.setStyleSheet("""
            QMainWindow {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #2b2b2b, stop: 1 #3c3f41
                );
                color: #f0f0f0;
                font-family: "Helvetica Neue", sans-serif;
                font-size: 11pt;
            }
            QLabel, QTreeWidget, QPlainTextEdit , QCheckBox{
                color: #f0f0f0;
                background: transparent;
            }
            QPushButton {
                background-color: #5a5a5a;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
                color: #f0f0f0;
            }
            QPushButton:hover {
                background-color: #707070;
            }
            QLineEdit {
                border: 1px solid #808080;
                padding: 4px;
                border-radius: 4px;
                background: #3c3f41;
                color: #f0f0f0;
            }
            QLineEdit:focus {
                border: 1px solid #007acc;
            }
            QSplitter::handle {
                background-color: #424242;
            }
            QSplitter::handle:hover {
                background-color: #606060;
            }
            QMenuBar {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 1,
                    stop: 0 #2b2b2b, stop: 1 #3c3f41
                );
                color: #f0f0f0;
            }
            QMenuBar::item {
                background-color: transparent;
                color: #f0f0f0;
            }
            QMenuBar::item:selected {
                background-color: #606060;
            }
            QMenu {
                background-color: #3c3f41;
                color: #f0f0f0;
            }
            QMenu::item:selected {
                background-color: #606060;
            }
            QMessageBox {
                background-color: #2b2b2b;
                color: #f0f0f0;
            }
            QMessageBox QLabel {
                color: #f0f0f0;
                background-color: transparent;
            }
            QMessageBox QPushButton {
                background-color: #5a5a5a;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                color: #f0f0f0;
                min-width: 80px;
            }
            QMessageBox QPushButton:hover {
                background-color: #707070;
            }
            QHeaderView::section {
                background-color: #3c3f41;
                color: #f0f0f0;
                padding: 4px;
                border: none;
                border-right: 1px solid #606060;
            }
            QHeaderView::section:hover {
                background-color: #505050;
            }
            QHeaderView::section:checked {
                background-color: #505050;
            }
        """)

    def toggle_dark_mode(self, checked):
        if (checked):
            self.set_dark_mode()
        else:
            self.set_non_dark_mode()
        cfg = read_config()
        cfg["dark_mode"] = checked
        write_config(cfg)
        self.dark_mode = checked
        
    def toggle_history(self, checked):
        self.history_enabled = checked
        cfg = read_config()
        cfg["history_enabled"] = checked
        write_config(cfg)
        
    def show_about_dialog(self):
        about_text = """
<h2>Everything by mdfind</h2>
<p>A powerful file search tool for macOS that leverages the Spotlight engine.</p>
<p><b>Version:</b> 1.0.0</p>
<p><b>Author:</b> Apple Dragon</p>
"""
        QMessageBox.about(self, "About Everything by mdfind", about_text)

    def clear_history(self):
        reply = self.show_question(
            "Clear History",
            "Are you sure you want to clear your search history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.query_history = []
            cfg = read_config()
            cfg["query_history"] = self.query_history
            write_config(cfg)
            self.query_completer.model().setStringList(self.query_history)
            self.show_info("History Cleared", "Search history cleared.")

    def show_info(self, title, message):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(message)
        msg.exec()

    def show_warning(self, title, message):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(message)
        msg.exec()

    def show_critical(self, title, message):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText(message)
        msg.exec()

    def show_question(self, title, message, buttons):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText(message)
        msg.setStandardButtons(buttons)
        return msg.exec()

    def closeEvent(self, event):
        config = read_config()
        config["window_size"] = {"width": self.width(), "height": self.height()}
        write_config(config)
        super().closeEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MdfindApp()
    window.show()
    sys.exit(app.exec())
