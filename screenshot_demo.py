#!/usr/bin/env python3
import sys
import os
import json
import time
import csv
import random

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QCheckBox, QPushButton, QTreeWidget, QTreeWidgetItem, QProgressBar, QMenu,
    QFileDialog, QMessageBox, QGroupBox, QPlainTextEdit, QSplitter, QStackedWidget,
    QTabWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor

class MockSearchWorker(QThread):
    """Mock search worker for demonstration purposes"""
    progress_signal = pyqtSignal(int)
    result_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)
    
    def __init__(self, query, directory, search_by_file_name, match_case, full_match, extra_clause=None, is_bookmark=False):
        super().__init__()
        self.query = query
        self.directory = directory or "/home/user"
        self.search_by_file_name = search_by_file_name
        self.match_case = match_case
        self.full_match = full_match
        self.extra_clause = extra_clause
        self.is_bookmark = is_bookmark
        self._is_running = True

    def run(self):
        """Simulate file search with mock data"""
        files_info = []
        
        # Generate mock file data based on query type
        if self.extra_clause and "FSSize > 52428800" in self.extra_clause:
            # Large files
            demo_files = [
                ("/home/user/Videos/movie.mkv", 2147483648),  # 2GB
                ("/home/user/Downloads/ubuntu.iso", 3221225472),  # 3GB
                ("/home/user/Documents/large_dataset.csv", 104857600),  # 100MB
                ("/home/user/Pictures/raw_photo.cr2", 78643200),  # 75MB
                ("/home/user/Videos/presentation.mp4", 157286400),  # 150MB
            ]
        elif self.extra_clause and "ContentType == 'public.movie'" in self.extra_clause:
            # Video files
            demo_files = [
                ("/home/user/Videos/vacation_2023.mp4", 524288000),
                ("/home/user/Downloads/tutorial.mkv", 314572800),
                ("/home/user/Movies/documentary.avi", 1073741824),
                ("/home/user/Desktop/screen_recording.mov", 209715200),
                ("/home/user/Videos/family_dinner.mp4", 367001600),
            ]
        elif self.extra_clause and "ContentType == 'public.image'" in self.extra_clause:
            # Image files
            demo_files = [
                ("/home/user/Pictures/sunset.jpg", 4194304),
                ("/home/user/Desktop/screenshot.png", 1048576),
                ("/home/user/Downloads/diagram.svg", 262144),
                ("/home/user/Photos/portrait.jpeg", 6291456),
                ("/home/user/Pictures/vacation/beach.jpg", 5242880),
            ]
        elif self.extra_clause and "ContentType == 'public.audio'" in self.extra_clause:
            # Audio files
            demo_files = [
                ("/home/user/Music/favorite_song.mp3", 8388608),
                ("/home/user/Downloads/podcast.m4a", 52428800),
                ("/home/user/Audio/recording.wav", 167772160),
                ("/home/user/Music/Classical/symphony.flac", 31457280),
                ("/home/user/Downloads/audiobook.mp3", 104857600),
            ]
        else:
            # General files
            demo_files = [
                ("/home/user/Documents/report.pdf", 1048576),
                ("/home/user/Pictures/vacation.jpg", 2097152),
                ("/home/user/Downloads/music.mp3", 5242880),
                ("/home/user/Videos/presentation.mp4", 157286400),
                ("/home/user/Documents/spreadsheet.xlsx", 524288),
                ("/home/user/Pictures/screenshot.png", 786432),
                ("/home/user/Downloads/archive.zip", 10485760),
                ("/home/user/Documents/notes.txt", 16384),
                ("/home/user/Pictures/photo.jpeg", 3145728),
                ("/home/user/Downloads/software.dmg", 209715200),
            ]
        
        # Filter based on query if provided
        if self.query:
            if self.search_by_file_name:
                demo_files = [(path, size) for path, size in demo_files 
                             if self.query.lower() in os.path.basename(path).lower()]
            else:
                # For content search, just return some files
                demo_files = demo_files[:5]
        
        # Simulate progressive loading
        for i, (path, size) in enumerate(demo_files):
            if not self._is_running:
                break
                
            # Create mock file info
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
            self.msleep(100)
        
        self.result_signal.emit(files_info)

    def stop(self):
        self._is_running = False

class DemoMdfindApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_search_worker = None
        self.dark_mode = False
        
        # File extension categories
        self.image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.heic', '.svg']
        self.video_extensions = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv', '.webm']
        self.audio_extensions = ['.mp3', '.wav', '.flac', '.aac', '.ogg', '.m4a']
        
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Everything by mdfind - macOS File Search Tool")
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
        self.create_new_tab("Search 1")
        
        # Add new tab button
        new_tab_btn = QPushButton("+")
        new_tab_btn.setFixedSize(30, 30)
        new_tab_btn.clicked.connect(lambda: self.create_new_tab(f"Search {self.tab_widget.count() + 1}"))
        self.tab_widget.setCornerWidget(new_tab_btn)
        
        # Create splitter for main content and preview
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - search and results
        left_container = QWidget()
        left_layout = QVBoxLayout(left_container)
        
        # Search controls
        search_group = QGroupBox("🔍 Search Options")
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
        self.search_by_filename = QCheckBox("🏷️ Search by filename")
        self.search_by_filename.setChecked(True)
        self.match_case = QCheckBox("🔤 Match case")
        self.full_match = QCheckBox("🎯 Full match")
        
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
        
        browse_btn = QPushButton("📁 Browse")
        browse_btn.clicked.connect(self.browse_directory)
        dir_layout.addWidget(browse_btn)
        search_layout.addLayout(dir_layout)
        
        # Quick search buttons
        quick_layout = QHBoxLayout()
        quick_buttons = [
            ("📊 Large Files (>50MB)", "kMDItemFSSize > 52428800"),
            ("🎬 Videos", "kMDItemContentType == 'public.movie'"),
            ("🖼️ Images", "kMDItemContentType == 'public.image'"),
            ("🎵 Audio", "kMDItemContentType == 'public.audio'"),
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
        self.tree.setHeaderLabels(["📄 Name", "📏 Size", "🕒 Modified", "📍 Path"])
        self.tree.itemSelectionChanged.connect(self.on_tree_selection_changed)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.setAlternatingRowColors(True)
        left_layout.addWidget(self.tree)
        
        # Status label
        self.status_label = QLabel("🚀 Ready - Enter a search query or click a quick search button")
        left_layout.addWidget(self.status_label)
        
        # Export button
        export_btn = QPushButton("📤 Export to CSV")
        export_btn.clicked.connect(self.export_to_csv)
        left_layout.addWidget(export_btn)
        
        splitter.addWidget(left_container)
        
        # Right side - preview
        self.preview_container = QWidget()
        preview_layout = QVBoxLayout(self.preview_container)
        
        # Preview header
        header_layout = QHBoxLayout()
        preview_title = QLabel("<b>👁️ Preview Panel</b>")
        header_layout.addWidget(preview_title)
        header_layout.addStretch()
        
        # Theme toggle button
        theme_btn = QPushButton("🌙")
        theme_btn.setFixedSize(30, 30)
        theme_btn.setToolTip("Toggle Dark/Light Mode")
        theme_btn.clicked.connect(self.toggle_theme)
        header_layout.addWidget(theme_btn)
        
        # Hide preview button
        hide_btn = QPushButton("✕")
        hide_btn.setFixedSize(30, 30)
        hide_btn.setToolTip("Hide Preview Panel")
        hide_btn.clicked.connect(self.toggle_preview)
        header_layout.addWidget(hide_btn)
        
        preview_layout.addLayout(header_layout)
        
        # Preview stack
        self.preview_stack = QStackedWidget()
        
        # Text preview
        self.text_preview = QPlainTextEdit()
        self.text_preview.setReadOnly(True)
        self.text_preview.setPlainText("📝 Select a file to see its preview here...\\n\\n✨ Features:\\n• Lightning-fast search using macOS Spotlight\\n• Text file preview with encoding detection\\n• Image preview with scaling\\n• Video/audio playback support\\n• Dark/light mode toggle\\n• Export to CSV\\n• Multiple tabs support")
        self.preview_stack.addWidget(self.text_preview)
        
        # Image preview
        self.image_label = QLabel()
        self.image_label.setFixedSize(400, 300)
        self.image_label.setScaledContents(True)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 2px dashed #cccccc; background-color: #f9f9f9;")
        
        # Create a placeholder image
        placeholder = QPixmap(400, 300)
        placeholder.fill(QColor(249, 249, 249))
        painter = QPainter(placeholder)
        painter.setPen(QColor(100, 100, 100))
        painter.setFont(QFont("Arial", 14))
        painter.drawText(placeholder.rect(), Qt.AlignmentFlag.AlignCenter, 
                        "🖼️ Image Preview\\n\\nSelect an image file\\nto see preview here")
        painter.end()
        self.image_label.setPixmap(placeholder)
        
        self.preview_stack.addWidget(self.image_label)
        
        preview_layout.addWidget(self.preview_stack)
        
        # File info
        self.file_info = QPlainTextEdit()
        self.file_info.setReadOnly(True)
        self.file_info.setMaximumHeight(150)
        self.file_info.setPlainText("📋 File Information\\n\\nSelect a file to see detailed information including:\\n• File size and modification date\\n• Full path location\\n• File type and permissions")
        preview_layout.addWidget(self.file_info)
        
        splitter.addWidget(self.preview_container)
        splitter.setSizes([800, 400])
        
        main_layout.addWidget(splitter)
        
        # Create context menu
        self.create_context_menu()
        
        # Apply initial theme
        self.apply_theme()
        
        # Show some demo data
        QTimer.singleShot(1000, lambda: self.quick_search("kMDItemFSSize > 52428800"))
        
    def create_new_tab(self, name):
        """Create a new search tab"""
        tab_widget = QWidget()
        tab_layout = QVBoxLayout(tab_widget)
        tab_layout.addWidget(QLabel(f"🔍 {name} - Independent search tab"))
        
        self.tab_widget.addTab(tab_widget, name)
        self.tab_widget.setCurrentWidget(tab_widget)
        
    def close_tab(self, index):
        """Close a tab"""
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        
    def create_context_menu(self):
        """Create context menu for file operations"""
        self.context_menu = QMenu(self)
        
        # File operations
        self.context_menu.addAction("🚀 Open", self.open_file)
        self.context_menu.addAction("👁️ Show in Finder", self.show_in_finder)
        self.context_menu.addSeparator()
        
        # Copy operations
        copy_menu = self.context_menu.addMenu("📋 Copy")
        copy_menu.addAction("📍 Copy Full Path", self.copy_full_path)
        copy_menu.addAction("📁 Copy Directory Path", self.copy_directory_path)
        copy_menu.addAction("🏷️ Copy Filename", self.copy_filename)
        
        self.context_menu.addSeparator()
        self.context_menu.addAction("📤 Export Selected", self.export_selected)
        
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
        self.search_timer.start(500)  # 500ms debounce
        
    def start_search(self, extra_clause=None):
        """Start file search"""
        if self.current_search_worker:
            self.current_search_worker.stop()
            self.current_search_worker.wait()
            
        query = self.query_input.text().strip()
        directory = self.dir_input.text().strip()
        
        if not query and not extra_clause:
            return
            
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        if extra_clause and "FSSize > 52428800" in extra_clause:
            self.status_label.setText("🔍 Searching for large files (>50MB)...")
        elif extra_clause and "ContentType == 'public.movie'" in extra_clause:
            self.status_label.setText("🔍 Searching for video files...")
        elif extra_clause and "ContentType == 'public.image'" in extra_clause:
            self.status_label.setText("🔍 Searching for image files...")
        elif extra_clause and "ContentType == 'public.audio'" in extra_clause:
            self.status_label.setText("🔍 Searching for audio files...")
        else:
            self.status_label.setText(f"🔍 Searching for '{query}'...")
        
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
            self.status_label.setText("❌ No results found")
            return
            
        self.status_label.setText(f"✅ Found {len(files_info)} items")
        
        for file_info in files_info:
            item = QTreeWidgetItem()
            
            # Add appropriate icons based on file type
            name = file_info['name']
            ext = os.path.splitext(name)[1].lower()
            
            if ext in self.image_extensions:
                icon = "🖼️ "
            elif ext in self.video_extensions:
                icon = "🎬 "
            elif ext in self.audio_extensions:
                icon = "🎵 "
            elif ext in ['.pdf']:
                icon = "📄 "
            elif ext in ['.zip', '.rar', '.7z']:
                icon = "📦 "
            elif ext in ['.txt', '.md']:
                icon = "📝 "
            else:
                icon = "📄 "
                
            item.setText(0, icon + name)
            item.setText(1, self.format_file_size(file_info['size']))
            item.setText(2, time.strftime('%Y-%m-%d %H:%M', time.localtime(file_info['modified'])))
            item.setText(3, file_info['path'])
            self.tree.addTopLevelItem(item)
            
        # Auto-resize columns
        for i in range(4):
            self.tree.resizeColumnToContents(i)
            
    def format_file_size(self, size):
        """Format file size in human readable format"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
        
    def show_error(self, error_msg):
        """Show error message"""
        self.progress.setVisible(False)
        self.status_label.setText(f"❌ Error: {error_msg}")
        
    def on_tree_selection_changed(self):
        """Handle tree selection change for preview"""
        selected_items = self.tree.selectedItems()
        if not selected_items:
            return
            
        item = selected_items[0]
        file_path = item.text(3)
        file_name = item.text(0).replace("🖼️ ", "").replace("🎬 ", "").replace("🎵 ", "").replace("📄 ", "").replace("📦 ", "").replace("📝 ", "")
        
        # Show file info
        file_size = item.text(1)
        file_modified = item.text(2)
        
        info_text = f"📋 File Information\\n\\n"
        info_text += f"📄 Name: {file_name}\\n"
        info_text += f"📏 Size: {file_size}\\n"
        info_text += f"🕒 Modified: {file_modified}\\n"
        info_text += f"📍 Path: {file_path}\\n\\n"
        info_text += f"🎯 Right-click for more operations"
        
        self.file_info.setPlainText(info_text)
        
        # Show preview based on file type
        _, ext = os.path.splitext(file_path)
        ext = ext.lower()
        
        if ext in self.image_extensions:
            self.show_image_preview(file_name)
        else:
            self.show_text_preview(file_name, ext)
            
    def show_text_preview(self, file_name, ext):
        """Show text preview"""
        self.preview_stack.setCurrentIndex(0)
        
        preview_text = f"📝 Text Preview: {file_name}\\n"
        preview_text += "=" * 50 + "\\n\\n"
        
        if ext == '.pdf':
            preview_text += "📄 PDF Document\\n\\n"
            preview_text += "This is a PDF document preview.\\n"
            preview_text += "The real application would show:\\n"
            preview_text += "• PDF content extraction\\n"
            preview_text += "• Page thumbnails\\n"
            preview_text += "• Text search within PDF\\n"
        elif ext in ['.txt', '.md']:
            preview_text += "📝 Text Document\\n\\n"
            preview_text += "Sample file content would appear here...\\n\\n"
            preview_text += "Features in real application:\\n"
            preview_text += "• Automatic encoding detection\\n"
            preview_text += "• Syntax highlighting for code\\n"
            preview_text += "• Large file handling\\n"
        elif ext in ['.mp4', '.mkv', '.avi']:
            preview_text += "🎬 Video File\\n\\n"
            preview_text += "Video preview and playback controls\\n"
            preview_text += "would be available here.\\n\\n"
            preview_text += "Features:\\n"
            preview_text += "• Video thumbnail preview\\n"
            preview_text += "• Playback controls (play/pause/seek)\\n"
            preview_text += "• Media information display\\n"
        elif ext in ['.mp3', '.wav', '.flac']:
            preview_text += "🎵 Audio File\\n\\n"
            preview_text += "Audio playback controls and\\n"
            preview_text += "waveform visualization would\\n"
            preview_text += "be shown here.\\n\\n"
            preview_text += "Features:\\n"
            preview_text += "• Audio player controls\\n"
            preview_text += "• Metadata display\\n"
            preview_text += "• Waveform visualization\\n"
        else:
            preview_text += f"📄 File Type: {ext.upper() if ext else 'Unknown'}\\n\\n"
            preview_text += "This file type is supported by the\\n"
            preview_text += "Everything by mdfind application.\\n\\n"
            preview_text += "Features for various file types:\\n"
            preview_text += "• Quick Look integration\\n"
            preview_text += "• Custom preview handlers\\n"
            preview_text += "• Metadata extraction\\n"
        
        self.text_preview.setPlainText(preview_text)
        
    def show_image_preview(self, file_name):
        """Show image preview"""
        self.preview_stack.setCurrentIndex(1)
        
        # Create a demo image preview
        pixmap = QPixmap(400, 300)
        pixmap.fill(QColor(240, 245, 255))
        
        painter = QPainter(pixmap)
        painter.setPen(QColor(70, 130, 180))
        painter.setFont(QFont("Arial", 12))
        
        # Draw a mock image preview
        text = f"🖼️ Image Preview\\n\\n{file_name}\\n\\nIn the real application:\\n• Full image display\\n• Zoom and pan controls\\n• EXIF data display\\n• GIF animation support"
        painter.drawText(pixmap.rect(), Qt.AlignmentFlag.AlignCenter, text)
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
                QMainWindow { 
                    background-color: #2b2b2b; 
                    color: #ffffff; 
                }
                QWidget { 
                    background-color: #2b2b2b; 
                    color: #ffffff; 
                }
                QLineEdit { 
                    background-color: #404040; 
                    border: 2px solid #606060; 
                    padding: 6px; 
                    border-radius: 4px;
                }
                QTreeWidget { 
                    background-color: #353535; 
                    alternate-background-color: #404040;
                    gridline-color: #555555;
                }
                QPushButton { 
                    background-color: #505050; 
                    border: 2px solid #707070; 
                    padding: 8px 12px; 
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover { 
                    background-color: #606060; 
                    border-color: #808080;
                }
                QGroupBox { 
                    font-weight: bold; 
                    border: 2px solid #555555;
                    border-radius: 8px;
                    margin-top: 1ex;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
                QTabWidget::pane { 
                    border: 2px solid #606060; 
                    border-radius: 4px;
                }
                QTabBar::tab { 
                    background-color: #505050; 
                    padding: 8px 16px; 
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                QTabBar::tab:selected { 
                    background-color: #707070; 
                }
                QProgressBar {
                    border: 2px solid #555555;
                    border-radius: 5px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    border-radius: 3px;
                }
                QPlainTextEdit {
                    background-color: #353535;
                    border: 2px solid #555555;
                    border-radius: 4px;
                    padding: 8px;
                }
                QLabel {
                    color: #ffffff;
                }
            """)
        else:
            # Light theme
            self.setStyleSheet("""
                QMainWindow { 
                    background-color: #ffffff; 
                    color: #000000; 
                }
                QLineEdit { 
                    border: 2px solid #cccccc; 
                    padding: 6px; 
                    border-radius: 4px;
                    background-color: white;
                }
                QTreeWidget { 
                    gridline-color: #e0e0e0;
                    alternate-background-color: #f5f5f5;
                }
                QPushButton { 
                    background-color: #f0f0f0; 
                    border: 2px solid #cccccc; 
                    padding: 8px 12px; 
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover { 
                    background-color: #e0e0e0; 
                    border-color: #999999;
                }
                QGroupBox { 
                    font-weight: bold; 
                    border: 2px solid #cccccc;
                    border-radius: 8px;
                    margin-top: 1ex;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                }
                QTabWidget::pane { 
                    border: 2px solid #cccccc; 
                    border-radius: 4px;
                }
                QTabBar::tab { 
                    background-color: #f0f0f0; 
                    padding: 8px 16px; 
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                }
                QTabBar::tab:selected { 
                    background-color: #ffffff; 
                }
                QProgressBar {
                    border: 2px solid #cccccc;
                    border-radius: 5px;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    border-radius: 3px;
                }
                QPlainTextEdit {
                    border: 2px solid #cccccc;
                    border-radius: 4px;
                    padding: 8px;
                    background-color: white;
                }
            """)
            
    def toggle_preview(self):
        """Toggle preview panel visibility"""
        self.preview_container.setVisible(not self.preview_container.isVisible())
        
    # File operation methods (demo implementations)
    def open_file(self):
        """Open selected file"""
        selected_items = self.tree.selectedItems()
        if selected_items:
            file_path = selected_items[0].text(3)
            QMessageBox.information(self, "Demo", f"Would open: {os.path.basename(file_path)}")
            
    def show_in_finder(self):
        """Show file in finder"""
        selected_items = self.tree.selectedItems()
        if selected_items:
            file_path = selected_items[0].text(3)
            QMessageBox.information(self, "Demo", f"Would show in Finder: {os.path.basename(file_path)}")
            
    def copy_full_path(self):
        """Copy full path to clipboard"""
        selected_items = self.tree.selectedItems()
        if selected_items:
            file_path = selected_items[0].text(3)
            QApplication.clipboard().setText(file_path)
            QMessageBox.information(self, "Demo", "Full path copied to clipboard!")
            
    def copy_directory_path(self):
        """Copy directory path to clipboard"""
        selected_items = self.tree.selectedItems()
        if selected_items:
            file_path = selected_items[0].text(3)
            directory = os.path.dirname(file_path)
            QApplication.clipboard().setText(directory)
            QMessageBox.information(self, "Demo", "Directory path copied to clipboard!")
            
    def copy_filename(self):
        """Copy filename to clipboard"""
        selected_items = self.tree.selectedItems()
        if selected_items:
            file_path = selected_items[0].text(3)
            filename = os.path.basename(file_path)
            QApplication.clipboard().setText(filename)
            QMessageBox.information(self, "Demo", "Filename copied to clipboard!")
            
    def export_to_csv(self):
        """Export all results to CSV"""
        if self.tree.topLevelItemCount() == 0:
            QMessageBox.information(self, "Export", "No data to export")
            return
            
        QMessageBox.information(self, "Demo", f"Would export {self.tree.topLevelItemCount()} items to CSV")
                
    def export_selected(self):
        """Export selected items to CSV"""
        selected_items = self.tree.selectedItems()
        if not selected_items:
            QMessageBox.information(self, "Export", "No items selected")
            return
            
        QMessageBox.information(self, "Demo", f"Would export {len(selected_items)} selected items to CSV")

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Everything by mdfind")
    
    window = DemoMdfindApp()
    window.show()
    
    # Take screenshots after the window is fully rendered
    QTimer.singleShot(2000, lambda: take_screenshots(window))
    
    return app.exec()

def take_screenshots(window):
    """Take screenshots of the application"""
    try:
        # Main interface screenshot
        pixmap1 = window.grab()
        pixmap1.save("/home/runner/work/everythingByMdfind/everythingByMdfind/screenshot_main.png")
        print("Screenshot 1 saved: Main interface")
        
        # Click dark mode and take another screenshot
        QTimer.singleShot(500, lambda: take_dark_mode_screenshot(window))
        
    except Exception as e:
        print(f"Error taking screenshot: {e}")

def take_dark_mode_screenshot(window):
    """Take screenshot in dark mode"""
    try:
        # Toggle to dark mode
        window.toggle_theme()
        
        # Wait for theme to apply and take screenshot
        QTimer.singleShot(500, lambda: save_dark_screenshot(window))
        
    except Exception as e:
        print(f"Error with dark mode screenshot: {e}")

def save_dark_screenshot(window):
    """Save dark mode screenshot"""
    try:
        pixmap2 = window.grab()
        pixmap2.save("/home/runner/work/everythingByMdfind/everythingByMdfind/screenshot_dark.png")
        print("Screenshot 2 saved: Dark mode")
        
        # Try clicking some quick search buttons
        QTimer.singleShot(500, lambda: demonstrate_features(window))
        
    except Exception as e:
        print(f"Error saving dark screenshot: {e}")

def demonstrate_features(window):
    """Demonstrate different features"""
    try:
        # Switch back to light mode
        window.toggle_theme()
        
        # Try different quick searches
        QTimer.singleShot(1000, lambda: window.quick_search("kMDItemContentType == 'public.image'"))
        QTimer.singleShot(2000, lambda: take_feature_screenshot(window, "images"))
        
    except Exception as e:
        print(f"Error demonstrating features: {e}")

def take_feature_screenshot(window, feature_name):
    """Take screenshot of specific feature"""
    try:
        pixmap = window.grab()
        pixmap.save(f"/home/runner/work/everythingByMdfind/everythingByMdfind/screenshot_{feature_name}.png")
        print(f"Screenshot saved: {feature_name} search")
        
        # Exit the application after screenshots
        QTimer.singleShot(1000, lambda: QApplication.quit())
        
    except Exception as e:
        print(f"Error taking {feature_name} screenshot: {e}")

if __name__ == "__main__":
    sys.exit(main())