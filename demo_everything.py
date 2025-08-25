#!/usr/bin/env python3
import sys
import os
import json
import subprocess
import time
import csv
import shutil
import zipfile
import glob
import random

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QCheckBox, QPushButton, QTreeWidget, QTreeWidgetItem, QProgressBar, QMenu,
    QFileDialog, QMessageBox, QGroupBox, QInputDialog, QPlainTextEdit, QSplitter, QStackedWidget, QCompleter,
    QSlider, QToolButton, QStyle, QGraphicsDropShadowEffect, QTabWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QUrl, QMimeData, QPropertyAnimation, QEasingCurve
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtGui import QPixmap, QMovie, QPainter, QFont, QColor
from PyQt6.QtSvg import QSvgRenderer

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

# Beautiful ToolTip class for showing confirmation messages
class BeautifulToolTip(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(280, 80)
        
        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 15, 20, 15)
        
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }
        """)
        
        layout.addWidget(self.label)
        self.setLayout(layout)
        
        # Set up style
        self.setup_style()
        
    def setup_style(self):
        """Setup light theme style"""
        self.setStyleSheet("""
            BeautifulToolTip {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                           stop: 0 #4CAF50, stop: 1 #45a049);
                border-radius: 8px;
                border: 2px solid #43A047;
            }
        """)
        
    def setup_dark_style(self):
        """Setup dark theme style"""
        self.setStyleSheet("""
            BeautifulToolTip {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                           stop: 0 #2E7D32, stop: 1 #1B5E20);
                border-radius: 8px;
                border: 2px solid #388E3C;
            }
        """)
        
    def show_message(self, text, relative_widget=None, duration=3000):
        """Show tooltip with message for specified duration"""
        self.label.setText(text)
        
        if relative_widget:
            # Position relative to the widget
            global_pos = relative_widget.mapToGlobal(relative_widget.rect().center())
            self.move(global_pos.x() - self.width() // 2, global_pos.y() - self.height() - 10)
        
        self.show()
        self.raise_()
        
        # Auto-hide after duration
        QTimer.singleShot(duration, self.hide)

# Mock SearchWorker that simulates file search for demonstration
class MockSearchWorker(QThread):
    """Mock search worker for demonstration purposes"""
    progress_signal = pyqtSignal(int)
    result_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)
    
    def __init__(self, query, directory, search_by_file_name, match_case, full_match, extra_clause=None, is_bookmark=False):
        super().__init__()
        self.query = query
        self.directory = directory or os.path.expanduser("~")
        self.search_by_file_name = search_by_file_name
        self.match_case = match_case
        self.full_match = full_match
        self.extra_clause = extra_clause
        self.is_bookmark = is_bookmark
        self._is_running = True

    def run(self):
        """Simulate file search with mock data"""
        files_info = []
        
        # Generate some mock file data for demonstration
        demo_files = [
            "/home/user/Documents/report.pdf",
            "/home/user/Pictures/vacation.jpg",
            "/home/user/Downloads/music.mp3",
            "/home/user/Videos/presentation.mp4",
            "/home/user/Documents/spreadsheet.xlsx",
            "/home/user/Pictures/screenshot.png",
            "/home/user/Downloads/archive.zip",
            "/home/user/Documents/notes.txt",
            "/home/user/Pictures/photo.jpeg",
            "/home/user/Downloads/software.dmg",
        ]
        
        # Filter based on query if provided
        if self.query:
            if self.search_by_file_name:
                demo_files = [f for f in demo_files if self.query.lower() in os.path.basename(f).lower()]
            else:
                # For content search, just return some files as if they contain the query
                demo_files = demo_files[:5]
        
        # Simulate progressive loading
        for i, path in enumerate(demo_files):
            if not self._is_running:
                break
                
            # Create mock file info
            size = random.randint(1024, 10 * 1024 * 1024)  # Random size between 1KB and 10MB
            mod_time = time.time() - random.randint(0, 365 * 24 * 3600)  # Random time in past year
            
            files_info.append({
                'name': os.path.basename(path),
                'size': size,
                'modified': mod_time,
                'path': path
            })
            
            # Emit progress
            progress = int((i + 1) / len(demo_files) * 100)
            self.progress_signal.emit(progress)
            
            # Small delay to simulate real search
            time.sleep(0.1)
        
        self.result_signal.emit(files_info)

    def stop(self):
        self._is_running = False

# Main application class
class DemoMdfindApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_search_worker = None
        self.dark_mode = False
        self.tooltip = BeautifulToolTip()
        
        # File extension categories
        self.image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.heic', '.svg']
        self.video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
        self.audio_extensions = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']
        
        self.init_ui()
        self.load_config()
        
    def init_ui(self):
        self.setWindowTitle("Everything by mdfind (Demo)")
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        main_layout.addWidget(self.tab_widget)
        
        # Create first tab
        self.create_new_tab()
        
        # Add new tab button
        new_tab_btn = QPushButton("+")
        new_tab_btn.setFixedSize(30, 30)
        new_tab_btn.clicked.connect(self.create_new_tab)
        self.tab_widget.setCornerWidget(new_tab_btn)
        
        # Create splitter for main content and preview
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - search and results
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        
        # Search controls
        search_group = QGroupBox("Search Options")
        search_layout = QVBoxLayout(search_group)
        
        # Query input
        query_layout = QHBoxLayout()
        query_layout.addWidget(QLabel("Query:"))
        self.query_input = QLineEdit()
        self.query_input.setPlaceholderText("Enter search query...")
        self.query_input.textChanged.connect(self.on_query_changed)
        query_layout.addWidget(self.query_input)
        search_layout.addLayout(query_layout)
        
        # Search options
        options_layout = QHBoxLayout()
        self.search_by_filename = QCheckBox("Search by filename")
        self.search_by_filename.setChecked(True)
        self.match_case = QCheckBox("Match case")
        self.full_match = QCheckBox("Full match")
        
        options_layout.addWidget(self.search_by_filename)
        options_layout.addWidget(self.match_case)
        options_layout.addWidget(self.full_match)
        options_layout.addStretch()
        search_layout.addLayout(options_layout)
        
        # Directory selection
        dir_layout = QHBoxLayout()
        dir_layout.addWidget(QLabel("Directory:"))
        self.dir_input = QLineEdit()
        self.dir_input.setPlaceholderText("Optional: limit search to directory")
        dir_layout.addWidget(self.dir_input)
        
        browse_btn = QPushButton("Browse")
        browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(browse_btn)
        search_layout.addLayout(dir_layout)
        
        # Quick search buttons
        quick_layout = QHBoxLayout()
        quick_buttons = [
            ("Large Files", "kMDItemFSSize > 52428800"),
            ("Videos", "kMDItemContentType == 'public.movie'"),
            ("Images", "kMDItemContentType == 'public.image'"),
            ("Audio", "kMDItemContentType == 'public.audio'"),
        ]
        
        for text, query in quick_buttons:
            btn = QPushButton(text)
            btn.clicked.connect(lambda checked, q=query: self.quick_search(q))
            quick_layout.addWidget(btn)
        
        search_layout.addLayout(quick_layout)
        left_layout.addWidget(search_group)
        
        # Progress bar
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        left_layout.addWidget(self.progress)
        
        # Results tree
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Name", "Size", "Modified", "Path"])
        self.tree.itemSelectionChanged.connect(self.on_tree_selection_changed)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        left_layout.addWidget(self.tree)
        
        # Status label
        self.status_label = QLabel("Ready")
        left_layout.addWidget(self.status_label)
        
        # Export button
        export_btn = QPushButton("Export to CSV")
        export_btn.clicked.connect(self.export_to_csv)
        left_layout.addWidget(export_btn)
        
        splitter.addWidget(left_container)
        
        # Right side - preview
        self.preview_container = QWidget()
        preview_layout = QVBoxLayout(self.preview_container)
        
        # Preview header
        header_layout = QHBoxLayout()
        preview_title = QLabel("<b>Preview</b>")
        header_layout.addWidget(preview_title)
        header_layout.addStretch()
        
        # Theme toggle button
        theme_btn = QPushButton("🌙")
        theme_btn.setFixedSize(30, 30)
        theme_btn.clicked.connect(self.toggle_theme)
        header_layout.addWidget(theme_btn)
        
        # Hide preview button
        hide_btn = QPushButton("✕")
        hide_btn.setFixedSize(30, 30)
        hide_btn.clicked.connect(self.toggle_preview)
        header_layout.addWidget(hide_btn)
        
        preview_layout.addLayout(header_layout)
        
        # Preview stack
        self.preview_stack = QStackedWidget()
        
        # Text preview
        self.text_preview = QPlainTextEdit()
        self.text_preview.setReadOnly(True)
        self.preview_stack.addWidget(self.text_preview)
        
        # Image preview
        self.image_label = QLabel()
        self.image_label.setFixedSize(400, 300)
        self.image_label.setScaledContents(True)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 1px solid gray;")
        self.preview_stack.addWidget(self.image_label)
        
        preview_layout.addWidget(self.preview_stack)
        
        # File info
        self.file_info = QPlainTextEdit()
        self.file_info.setReadOnly(True)
        self.file_info.setMaximumHeight(150)
        preview_layout.addWidget(self.file_info)
        
        splitter.addWidget(self.preview_container)
        splitter.setSizes([800, 400])
        
        main_layout.addWidget(splitter)
        
        # Create context menu
        self.create_context_menu()
        
        # Apply initial theme
        self.apply_theme()
        
    def create_new_tab(self):
        """Create a new search tab"""
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        
        # For now, just add the main tree to this tab
        # In a full implementation, each tab would have its own tree
        tab_name = f"Search {self.tab_widget.count() + 1}"
        self.tab_widget.addTab(tab_widget, tab_name)
        self.tab_widget.setCurrentWidget(tab_widget)
        
    def close_tab(self, index):
        """Close a tab"""
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        
    def create_context_menu(self):
        """Create context menu for file operations"""
        self.context_menu = QMenu(self)
        
        # File operations
        self.context_menu.addAction("Open", self.open_file)
        self.context_menu.addAction("Show in Finder", self.show_in_finder)
        self.context_menu.addSeparator()
        
        # Copy operations
        copy_menu = self.context_menu.addMenu("Copy")
        copy_menu.addAction("Copy Full Path", self.copy_full_path)
        copy_menu.addAction("Copy Directory Path", self.copy_directory_path)
        copy_menu.addAction("Copy Filename", self.copy_filename)
        
        self.context_menu.addSeparator()
        self.context_menu.addAction("Export Selected", self.export_selected)
        
    def show_context_menu(self, pos):
        """Show context menu at position"""
        if self.tree.itemAt(pos):
            self.context_menu.exec(self.tree.mapToGlobal(pos))
        
    def browse_directory(self):
        """Browse for directory"""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory")
        if directory:
            self.dir_input.setText(directory)
            
    def quick_search(self, query):
        """Perform quick search with predefined query"""
        self.query_input.setText("")  # Clear text search
        self.start_search(extra_clause=query)
        
    def on_query_changed(self):
        """Handle query text change with debouncing"""
        if hasattr(self, 'search_timer'):
            self.search_timer.stop()
        
        self.search_timer = QTimer()
        self.search_timer.timeout.connect(self.start_search)
        self.search_timer.setSingleShot(True)
        self.search_timer.start(DEBOUNCE_DELAY)
        
    def start_search(self, extra_clause=None):
        """Start file search"""
        if self.current_search_worker:
            self.current_search_worker.stop()
            self.current_search_worker.wait()
            
        query = self.query_input.text().strip()
        directory = self.dir_input.text().strip()
        
        if not query and not extra_clause:
            self.tree.clear()
            self.status_label.setText("Enter search query")
            return
            
        self.progress.setVisible(True)
        self.progress.setValue(0)
        self.status_label.setText("Searching...")
        
        self.current_search_worker = MockSearchWorker(
            query=query,
            directory=directory,
            search_by_file_name=self.search_by_filename.isChecked(),
            match_case=self.match_case.isChecked(),
            full_match=self.full_match.isChecked(),
            extra_clause=extra_clause
        )
        
        self.current_search_worker.progress_signal.connect(self.update_progress)
        self.current_search_worker.result_signal.connect(self.update_results)
        self.current_search_worker.error_signal.connect(self.show_error)
        
        self.current_search_worker.start()
        
    def update_progress(self, value):
        """Update progress bar"""
        self.progress.setValue(value)
        
    def update_results(self, files_info):
        """Update results tree with search results"""
        self.tree.clear()
        self.progress.setVisible(False)
        
        if not files_info:
            self.status_label.setText("No results found")
            return
            
        self.status_label.setText(f"Found {len(files_info)} items")
        
        for file_info in files_info:
            item = QTreeWidgetItem()
            item.setText(0, file_info['name'])
            item.setText(1, self.format_file_size(file_info['size']))
            item.setText(2, time.strftime('%Y-%m-%d %H:%M', time.localtime(file_info['modified'])))
            item.setText(3, file_info['path'])
            self.tree.addTopLevelItem(item)
            
        # Auto-resize columns
        for i in range(4):
            self.tree.resizeColumnToContents(i)
            
    def format_file_size(self, size):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
        
    def show_error(self, error_msg):
        """Show error message"""
        self.progress.setVisible(False)
        self.status_label.setText(f"Error: {error_msg}")
        QMessageBox.critical(self, "Search Error", error_msg)
        
    def on_tree_selection_changed(self):
        """Handle tree selection change for preview"""
        selected_items = self.tree.selectedItems()
        if not selected_items:
            self.text_preview.setPlainText("")
            self.file_info.setPlainText("")
            return
            
        item = selected_items[0]
        file_path = item.text(3)
        
        # Show file info
        file_name = item.text(0)
        file_size = item.text(1)
        file_modified = item.text(2)
        
        info_text = f"Name: {file_name}\\n"
        info_text += f"Size: {file_size}\\n"
        info_text += f"Modified: {file_modified}\\n"
        info_text += f"Path: {file_path}\\n"
        
        self.file_info.setPlainText(info_text)
        
        # Show preview based on file type
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext in self.image_extensions:
            self.show_image_preview(file_path)
        else:
            self.show_text_preview(file_path)
            
    def show_text_preview(self, file_path):
        """Show text preview"""
        self.preview_stack.setCurrentIndex(0)
        
        # For demo, show some sample text
        sample_text = f"Text preview for: {os.path.basename(file_path)}\\n\\n"
        sample_text += "This is a demo application showcasing the UI features\\n"
        sample_text += "of Everything by mdfind.\\n\\n"
        sample_text += "In the real application, this would show:\\n"
        sample_text += "- Actual file contents for text files\\n"
        sample_text += "- Image previews for image files\\n"
        sample_text += "- Video playback for video files\\n"
        sample_text += "- Audio playback for audio files\\n"
        
        self.text_preview.setPlainText(sample_text)
        
    def show_image_preview(self, file_path):
        """Show image preview"""
        self.preview_stack.setCurrentIndex(1)
        
        # For demo, show a placeholder
        pixmap = QPixmap(400, 300)
        pixmap.fill(QColor(240, 240, 240))
        
        painter = QPainter(pixmap)
        painter.setPen(QColor(100, 100, 100))
        painter.setFont(QFont("Arial", 16))
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, 
                        f"Image Preview\\n{os.path.basename(file_path)}")
        painter.end()
        
        self.image_label.setPixmap(pixmap)
        
    def toggle_theme(self):
        """Toggle between light and dark theme"""
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        
    def apply_theme(self):
        """Apply current theme"""
        if self.dark_mode:
            # Dark theme
            self.setStyleSheet("""
                QMainWindow { background-color: #2b2b2b; color: #ffffff; }
                QWidget { background-color: #2b2b2b; color: #ffffff; }
                QLineEdit { background-color: #404040; border: 1px solid #606060; padding: 4px; }
                QTreeWidget { background-color: #404040; alternate-background-color: #484848; }
                QPushButton { background-color: #505050; border: 1px solid #707070; padding: 6px; }
                QPushButton:hover { background-color: #606060; }
                QGroupBox { font-weight: bold; }
                QTabWidget::pane { border: 1px solid #606060; }
                QTabBar::tab { background-color: #505050; padding: 8px; }
                QTabBar::tab:selected { background-color: #707070; }
            """)
            self.tooltip.setup_dark_style()
        else:
            # Light theme
            self.setStyleSheet("")
            self.tooltip.setup_style()
            
    def toggle_preview(self):
        """Toggle preview panel visibility"""
        self.preview_container.setVisible(not self.preview_container.isVisible())
        
    # File operation methods (for demo purposes)
    def open_file(self):
        """Open selected file"""
        selected_items = self.tree.selectedItems()
        if selected_items:
            file_path = selected_items[0].text(3)
            self.show_tooltip(f"✅ Would open: {os.path.basename(file_path)}")
            
    def show_in_finder(self):
        """Show file in finder"""
        selected_items = self.tree.selectedItems()
        if selected_items:
            file_path = selected_items[0].text(3)
            self.show_tooltip(f"✅ Would show in finder: {os.path.basename(file_path)}")
            
    def copy_full_path(self):
        """Copy full path to clipboard"""
        selected_items = self.tree.selectedItems()
        if selected_items:
            file_path = selected_items[0].text(3)
            QApplication.clipboard().setText(file_path)
            self.show_tooltip("✅ Full path copied!")
            
    def copy_directory_path(self):
        """Copy directory path to clipboard"""
        selected_items = self.tree.selectedItems()
        if selected_items:
            file_path = selected_items[0].text(3)
            directory = os.path.dirname(file_path)
            QApplication.clipboard().setText(directory)
            self.show_tooltip("✅ Directory path copied!")
            
    def copy_filename(self):
        """Copy filename to clipboard"""
        selected_items = self.tree.selectedItems()
        if selected_items:
            file_path = selected_items[0].text(3)
            filename = os.path.basename(file_path)
            QApplication.clipboard().setText(filename)
            self.show_tooltip("✅ Filename copied!")
            
    def export_to_csv(self):
        """Export all results to CSV"""
        if self.tree.topLevelItemCount() == 0:
            QMessageBox.information(self, "Export", "No data to export")
            return
            
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Export to CSV", "search_results.csv", "CSV files (*.csv)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(['Name', 'Size', 'Modified', 'Path'])
                    
                    for i in range(self.tree.topLevelItemCount()):
                        item = self.tree.topLevelItem(i)
                        writer.writerow([
                            item.text(0),
                            item.text(1),
                            item.text(2),
                            item.text(3)
                        ])
                        
                self.show_tooltip(f"✅ Exported to {os.path.basename(file_path)}")
            except Exception as e:
                QMessageBox.critical(self, "Export Error", str(e))
                
    def export_selected(self):
        """Export selected items to CSV"""
        selected_items = self.tree.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Export", "No items selected")
            return
            
        self.show_tooltip(f"✅ Would export {len(selected_items)} selected items")
        
    def show_tooltip(self, message):
        """Show beautiful tooltip"""
        if self.dark_mode:
            self.tooltip.setup_dark_style()
        else:
            self.tooltip.setup_style()
            
        self.tooltip.show_message(message, self.tree, 2000)
        
    def load_config(self):
        """Load configuration"""
        config = read_config()
        self.dark_mode = config.get('dark_mode', False)
        self.apply_theme()
        
        # Restore window geometry
        if 'geometry' in config:
            self.restoreGeometry(config['geometry'])
            
    def save_config(self):
        """Save configuration"""
        config = {
            'dark_mode': self.dark_mode,
            'geometry': self.saveGeometry().data().hex()
        }
        write_config(config)
        
    def closeEvent(self, event):
        """Handle application close"""
        self.save_config()
        if self.current_search_worker:
            self.current_search_worker.stop()
            self.current_search_worker.wait()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Everything by mdfind (Demo)")
    
    window = DemoMdfindApp()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()