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
    QFileDialog, QMessageBox, QGroupBox, QInputDialog, QPlainTextEdit, QSplitter, QStackedWidget, QCompleter,
    QSlider, QToolButton, QStyle
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer, QUrl, QMimeData
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtGui import QPixmap, QMovie, QPainter, QFont
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


# Custom Slider that responds to direct clicks
class ClickableSlider(QSlider):
    def __init__(self, orientation):
        super().__init__(orientation)
        
    def mousePressEvent(self, event):
        # Calculate the relative position of the click and convert to value
        value = self.minimum() + (self.maximum() - self.minimum()) * event.position().x() / self.width()
        self.setValue(int(value))
        # Emit the sliderMoved signal to update video position
        self.sliderMoved.emit(int(value))
        # Pass the event to the parent class
        super().mousePressEvent(event)

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
    
    def __init__(self, query, directory, search_by_file_name, match_case, full_match, extra_clause=None):
        super().__init__()
        self.query = query
        self.directory = directory
        self.search_by_file_name = search_by_file_name
        self.match_case = match_case
        self.full_match = full_match
        self.extra_clause = extra_clause
        self._is_running = True
        self.process = None

    def run(self):
        files_info = []
        idx = 0
        cmd = ["mdfind"]


        full_match_str = "" if self.full_match else "*"
        case_modifier = "" if self.match_case else "cd"
        if self.search_by_file_name:
            query_str = f'kMDItemFSName == "{full_match_str}{self.query}{full_match_str}"{case_modifier}'
            if self.extra_clause is not None:
                query_str += f" && {self.extra_clause}"
        else:
            if self.query != "":
                query_str = f'kMDItemTextContent == "{full_match_str}{self.query}{full_match_str}"{case_modifier}'
                if self.extra_clause is not None:
                    query_str += f" && {self.extra_clause}"
            else:
                if self.extra_clause is not None:
                    query_str = self.extra_clause
                else:
                    return

                    
        cmd.append(query_str)

        if self.directory:
            dir_expanded = os.path.expanduser(self.directory)
            cmd.extend(["-onlyin", dir_expanded])

        # print(f"Running mdfind with query: {cmd}")
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
                elif path and os.path.isdir(path):
                    # If the path is a directory, add it to the list with size 0
                    mtime = os.path.getmtime(path)
                    files_info.append((os.path.basename(path), 0, mtime, path))
                if idx % 10 == 0:
                    self.progress_signal.emit(min(100, idx % 100))
            self.process.wait()
            self.result_signal.emit(files_info)
        except Exception as e:
            self.error_signal.emit(str(e))
            self.stop()
        finally:
            self.progress_signal.emit(0)

    def stop(self):
        self._is_running = False
        if self.process is not None:
            try:
                self.process.terminate()
            except Exception:
                pass


# standalone player window
class StandalonePlayerWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Media Player")
        self.resize(800, 600)  # Default size, user can resize
        
        # Main widget and layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        
        # Video widget
        self.video_widget = QVideoWidget()
        if getattr(QVideoWidget, "setAspectRatioMode", None) is not None:
            self.video_widget.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        
        self.video_widget.installEventFilter(self)
        
        # Audio label for audio files
        self.audio_label = QLabel()
        self.audio_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.audio_label.setWordWrap(True)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.audio_label.setFont(font)
        self.audio_label.setVisible(False)
        
        self.audio_label.installEventFilter(self)
        
        # Media container to hold both video widget and audio label
        media_container = QWidget()
        media_layout = QVBoxLayout(media_container)
        media_layout.setContentsMargins(0, 0, 0, 0)
        media_layout.addWidget(self.video_widget)
        media_layout.addWidget(self.audio_label)
        
        main_layout.addWidget(media_container, 1)
        
        # Controls layout
        controls_layout = QHBoxLayout()
        
        # Play/Pause button
        self.play_button = QToolButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        controls_layout.addWidget(self.play_button)
        
        # Time label
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setMinimumWidth(100)
        controls_layout.addWidget(self.time_label)
        
        # Seek slider
        self.seek_slider = ClickableSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setRange(0, 0)
        controls_layout.addWidget(self.seek_slider, 4)
        
        # Volume button
        self.volume_button = QToolButton()
        self.volume_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))
        controls_layout.addWidget(self.volume_button)
        
        # Volume slider
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)  # Default volume
        self.volume_slider.setMaximumWidth(100)
        controls_layout.addWidget(self.volume_slider)
        
        main_layout.addLayout(controls_layout)
        
        # Media player setup
        self.audio_output = QAudioOutput()
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setAudioOutput(self.audio_output)
        self.audio_output.setVolume(0.7)  # 70% volume
        
        # Connect signals
        self.play_button.clicked.connect(self.toggle_play_pause)
        self.seek_slider.sliderMoved.connect(self.set_position)
        self.seek_slider.sliderPressed.connect(self.on_slider_pressed)
        self.seek_slider.sliderReleased.connect(self.on_slider_released)
        self.volume_button.clicked.connect(self.toggle_mute)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.media_player.positionChanged.connect(self.update_position)
        self.media_player.durationChanged.connect(self.update_duration)
        self.media_player.playbackStateChanged.connect(self.on_playback_state_changed)
        
        self.setCentralWidget(central_widget)
        self.slider_dragging = False
        self.continuous_playback = False
        self.dark_mode = False
        self.current_media_path = None
        self.video_extensions = set()
        self.audio_extensions = set()
        
    def setup_extensions(self, video_ext, audio_ext):
        """Set up the video and audio extensions from the parent app"""
        self.video_extensions = video_ext
        self.audio_extensions = audio_ext
        
    def set_continuous_playback(self, enabled):
        """Set whether continuous playback is enabled"""
        self.continuous_playback = enabled
        
    def set_dark_mode(self, enabled):
        """Set dark mode for the player"""
        self.dark_mode = enabled
        filename = os.path.basename(self.current_media_path) if self.current_media_path else ""
        if filename:
            self.audio_label.setText(f"<div style='padding: 20px; border-radius: 10px;'>"
                                    f"<div style='font-size: 24pt; color: {'white' if enabled else 'black'};'>"
                                    f"{filename}</div></div>")
        
    def play_media(self, path, is_video=True):
        """Play a media file"""
        self.current_media_path = path
        
        # Update UI based on media type
        if is_video:
            self.video_widget.setVisible(True)
            self.audio_label.setVisible(False)
        else:
            self.video_widget.setVisible(False)
            self.audio_label.setVisible(True)
            filename = os.path.basename(path)
            self.audio_label.setText(f"<div style='padding: 20px; border-radius: 10px;'>"
                                    f"<div style='font-size: 24pt; color: {'white' if self.dark_mode else 'black'};'>"
                                    f"{filename}</div></div>")
        
        self.media_player.setSource(QUrl.fromLocalFile(path))
        self.media_player.play()
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        
    def toggle_play_pause(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        else:
            self.media_player.play()
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
    
    def set_position(self, position):
        self.media_player.setPosition(position)
    
    def update_position(self, position):
        try:
            if not self.slider_dragging:
                self.seek_slider.setValue(position)
            
            total_duration = self.media_player.duration()
            current_mins = position // 60000
            current_secs = (position % 60000) // 1000
            total_mins = total_duration // 60000
            total_secs = (total_duration % 60000) // 1000
            
            self.time_label.setText(f"{current_mins:02d}:{current_secs:02d} / {total_mins:02d}:{total_secs:02d}")
        except Exception:
            pass
    
    def update_duration(self, duration):
        self.seek_slider.setRange(0, duration)
        if duration > 0:
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
    
    def set_volume(self, volume):
        self.audio_output.setVolume(volume / 100.0)
        if volume == 0:
            self.volume_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolumeMuted))
        else:
            self.volume_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))
    
    def toggle_mute(self):
        if self.audio_output.isMuted():
            self.audio_output.setMuted(False)
            self.volume_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))
            self.volume_slider.setValue(int(self.audio_output.volume() * 100))
        else:
            self.audio_output.setMuted(True)
            self.volume_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolumeMuted))
    
    def on_slider_pressed(self):
        self.slider_dragging = True
        self.was_playing = self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
        if self.was_playing:
            self.media_player.pause()
    
    def on_slider_released(self):
        self.slider_dragging = False
        if self.was_playing:
            self.media_player.play()
    
    def on_playback_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.StoppedState:
            if self.continuous_playback and self.media_player.position() > 0:
                # Signal to the main app that we need to play the next media
                self.parent().play_next_in_standalone()
    
    def closeEvent(self, event):
        # Signal the parent to restore the embedded player
        self.parent().restore_embedded_player()
        event.accept()
        
    def get_current_position(self):
        """Get the current position of the media player"""
        return self.media_player.position()
    
    def get_playback_state(self):
        """Get the current playback state (playing/paused)"""
        return self.media_player.playbackState()
    
    def eventFilter(self, obj, event):
        if event.type() == event.Type.MouseButtonPress and (obj == self.video_widget or obj == self.audio_label):
            if event.button() == Qt.MouseButton.LeftButton:
                self.toggle_play_pause()
                return True
        return super().eventFilter(obj, event)


class MdfindApp(QMainWindow):
    def __init__(self):
        super().__init__()
                    
        # Load dark mode and history settings from config
        config = read_config()
        self.dark_mode = config.get("dark_mode", False)
        self.history_enabled = config.get("history_enabled", True)
        self.preview_enabled = config.get("preview_enabled", False) 
        self.continuous_playback = config.get("continuous_playback", False)
        self.slider_dragging = False  # Initialize slider_dragging attribute
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
        toggle_preview_action.setChecked(self.preview_enabled) # Use the loaded setting instead of hardcoded False
        toggle_preview_action.triggered.connect(self.toggle_preview)
        # Store reference to the toggle_preview_action for later use
        self.toggle_preview_action = toggle_preview_action

        # Add continuous playback action
        continuous_playback_action = view_menu.addAction('Continuous Playback')
        continuous_playback_action.setCheckable(True)
        continuous_playback_action.setChecked(self.continuous_playback)
        continuous_playback_action.triggered.connect(self.toggle_continuous_playback)
        self.continuous_playback_action = continuous_playback_action
        
        # Added dark mode toggle action in the View menu
        dark_mode_action = view_menu.addAction('Dark Mode')
        dark_mode_action.setCheckable(True)
        dark_mode_action.setChecked(self.dark_mode)
        dark_mode_action.triggered.connect(self.toggle_dark_mode)
        if self.dark_mode:
            self.set_dark_mode()
        else:
            self.set_non_dark_mode()
        
        # === Bookmarks Menu ===
        bookmarks_menu = menubar.addMenu("Bookmarks")
        bookmarks_menu.addAction("Large Files", self.bookmark_large_files)
        bookmarks_menu.addAction("Video Files", self.bookmark_videos)
        bookmarks_menu.addAction("Audio Files", self.bookmark_audio)
        bookmarks_menu.addAction("Images", self.bookmark_images)
        bookmarks_menu.addAction("Archives", self.bookmark_archives)
        bookmarks_menu.addAction("Applications", self.bookmark_applications)
        
        # Search thread variables
        self.search_worker = None
        self.all_file_data = []
        self.file_data = []

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
        form_layout.addWidget(self.edit_query, 4)
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
        form_layout2.addWidget(self.edit_dir, 4)
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
        self.edit_extension.setPlaceholderText("pdf;docx;xls")

        self.chk_file_name = QCheckBox("Search by File Name")
        self.chk_file_name.setChecked(True)
        self.chk_match_case = QCheckBox("Match Case")
        self.chk_full_match = QCheckBox("Full Match")

        adv_layout.addWidget(lbl_min_size, 2)
        adv_layout.addWidget(self.edit_min_size, 5)
        adv_layout.addWidget(lbl_max_size, 2)
        adv_layout.addWidget(self.edit_max_size, 5)
        adv_layout.addWidget(lbl_extension, 2)
        adv_layout.addWidget(self.edit_extension, 5)
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
        self.tree.setColumnWidth(2, 130)
        self.tree.setColumnWidth(3, 350)
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
        
        # Header layout with Preview title and buttons
        header_layout = QHBoxLayout()
        preview_title = QLabel("<b>Preview</b>")
        header_layout.addWidget(preview_title)
        header_layout.addStretch()
        
        # Add a pop-out button
        popout_button = QPushButton("□")  # Square symbol for pop-out
        popout_button.setFixedSize(24, 24)
        popout_button.setToolTip("Open in standalone player")
        popout_button.clicked.connect(self.open_standalone_player)
        popout_button.setObjectName("previewPopoutButton")
        popout_button.setStyleSheet("""
            #previewPopoutButton {
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
                background-color: transparent;
            }
            #previewPopoutButton:hover {
                background-color: #4285f4;
                color: white;
            }
        """)
        
        # Add the popout button to the header
        header_layout.addWidget(popout_button)
        
        # Add a more stylish close button to the header
        close_button = QPushButton("✕")  # Using Unicode "Heavy Multiplication X" character
        close_button.setFixedSize(24, 24)  # Keep the square size
        close_button.setToolTip("Close preview panel")
        close_button.clicked.connect(self.close_preview)
        
        # Apply special styling to the close button to make it more elegant
        close_button.setObjectName("previewCloseButton")  # Set object name for styling
        close_button.setStyleSheet("""
            #previewCloseButton {
                border: none;
                border-radius: 12px;
                font-size: 14px;
                font-weight: bold;
                background-color: transparent;
            }
            #previewCloseButton:hover {
                background-color: #d32f2f;
                color: white;
            }
        """)
        
        header_layout.addWidget(close_button)
        
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
        
        # Wrap image_label in a centered container
        image_container = QWidget()
        image_layout = QVBoxLayout(image_container)
        image_layout.setContentsMargins(0, 0, 0, 0)
        image_layout.addWidget(self.image_label, alignment=Qt.AlignmentFlag.AlignCenter)

        # 3) Video/Audio Preview Container
        media_container = QWidget()
        media_layout = QVBoxLayout(media_container)
        media_layout.setContentsMargins(0, 0, 0, 0)
        
        # Video widget
        self.video_widget = QVideoWidget()
        self.video_widget.setFixedSize(500, 400)
        if getattr(QVideoWidget, "setAspectRatioMode", None) is not None:
            self.video_widget.setAspectRatioMode(Qt.AspectRatioMode.KeepAspectRatio)
        
        self.video_widget.installEventFilter(self)
        
        self.audio_label = QLabel()
        self.audio_label.setFixedSize(500, 400)
        self.audio_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.audio_label.setWordWrap(True)

        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        self.audio_label.setFont(font)
        self.audio_label.setVisible(False)
        
        self.audio_label.installEventFilter(self)
        
        media_layout.addWidget(self.video_widget, alignment=Qt.AlignmentFlag.AlignCenter)
        media_layout.addWidget(self.audio_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Set up media player
        self.audio_output = QAudioOutput()
        self.media_player = QMediaPlayer()
        self.media_player.setVideoOutput(self.video_widget)
        self.media_player.setAudioOutput(self.audio_output)
        self.media_player.positionChanged.connect(self.update_position)
        self.media_player.durationChanged.connect(self.update_duration)
        self.media_player.playbackStateChanged.connect(self.on_playback_state_changed)
        
        # Create video controls
        video_controls_layout = QHBoxLayout()
        
        # Play/Pause button
        self.play_button = QToolButton()
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.play_button.clicked.connect(self.toggle_play_pause)
        video_controls_layout.addWidget(self.play_button)
        
        # Current time label
        self.time_label = QLabel("00:00 / 00:00")
        self.time_label.setMinimumWidth(100)
        video_controls_layout.addWidget(self.time_label)
        
        # Seekbar - replace standard QSlider with our ClickableSlider
        self.seek_slider = ClickableSlider(Qt.Orientation.Horizontal)
        self.seek_slider.setRange(0, 0)
        self.seek_slider.sliderMoved.connect(self.set_position)
        self.seek_slider.sliderPressed.connect(self.on_slider_pressed)
        self.seek_slider.sliderReleased.connect(self.on_slider_released)
        video_controls_layout.addWidget(self.seek_slider, 4)  # Give seekbar more space
        
        # Volume button and slider
        self.volume_button = QToolButton()
        self.volume_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))
        self.volume_button.clicked.connect(self.toggle_mute)
        video_controls_layout.addWidget(self.volume_button)
        
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(70)  # Default volume
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.audio_output.setVolume(0.7)  # Set initial volume to 70%
        video_controls_layout.addWidget(self.volume_slider)
        
        # Add all controls to the media layout
        media_layout.addLayout(video_controls_layout)
        
        # Add container to stack instead of self.video_widget directly.
        self.preview_stack.addWidget(self.text_preview)  # index 0
        self.preview_stack.addWidget(image_container)   # index 1
        self.preview_stack.addWidget(media_container)      # index 2

        self.preview_splitter.addWidget(self.preview_stack)

        # Bottom pane: metadata info
        self.media_info = QPlainTextEdit()
        self.media_info.setReadOnly(True)
        self.preview_splitter.addWidget(self.media_info)

        splitter.addWidget(self.preview_container)
        splitter.setSizes([800, 400])  # Initial left-right ratio

        # Make the preview panel invisible by default
        self.preview_container.setVisible(self.preview_enabled) # Use the loaded setting instead of always hidden

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
        self.image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp",".heic"}
        self.video_extensions = {".mp4", ".mov", ".avi", ".mkv", ".mpg", ".mpeg"}
        # Add audio extensions
        self.audio_extensions = {".mp3", ".wav", ".aac", ".ogg", ".flac", ".m4a", ".wma", ".caf",".aif",".m4r",".au"}
    
        # Create the standalone player window but don't show it yet
        self.standalone_player = StandalonePlayerWindow(self)
        self.standalone_player_active = False
        
        # Configure standalone player
        self.standalone_player.setup_extensions(self.video_extensions, self.audio_extensions)
        self.standalone_player.set_continuous_playback(self.continuous_playback)
        self.standalone_player.set_dark_mode(self.dark_mode)

    # ========== Preview logic ==========
    def on_tree_selection_changed(self):
        # if preview is not visible, do nothing
        if not self.preview_container.isVisible():
            return
        
        selected_items = self.tree.selectedItems()
        if not selected_items or len(selected_items) != 1:
            # For multiple or no selection: stop video/audio playback and clear preview
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

        # Stop previous video/audio playback
        self.media_player.stop()
        
        # If standalone player is active, use it instead
        if self.standalone_player_active:
            self.show_in_standalone_player(path)
            return

        # Display basic file info in the bottom pane
        file_stat = os.stat(path)
        size_kb = round(file_stat.st_size / 1024, 2)
        self.media_info.setPlainText(
            f"File: {path}\nSize: {size_kb} KB\nLast Modified: {time.ctime(file_stat.st_mtime)}"
        )

        # Check file extension
        _, ext = os.path.splitext(path)
        ext = ext.lower()

        if ext in self.image_extensions or ext == ".svg":
            # Support for GIF preview added
            if ext == ".gif":
                movie = QMovie(path)
                self.image_label.setMovie(movie)
                movie.start()
                # Show resolution info from the current frame if available
                pix = movie.currentPixmap()
                self.media_info.appendPlainText(
                    f"Resolution: {pix.width()} x {pix.height()}"
                )
            elif ext == ".svg":
                renderer = QSvgRenderer(path)
                default_size = renderer.defaultSize()
                container_size = self.image_label.size()
                ratio = min(container_size.width() / default_size.width(), 
                            container_size.height() / default_size.height())
                new_width = int(default_size.width() * ratio)
                new_height = int(default_size.height() * ratio)
                pixmap = QPixmap(new_width, new_height)
                pixmap.fill(Qt.GlobalColor.transparent)
                painter = QPainter(pixmap)
                renderer.render(painter)
                painter.end()
                self.image_label.setPixmap(pixmap)
                self.media_info.appendPlainText(
                    f"Resolution: {new_width} x {new_height}"
                )
            else:
                pixmap = QPixmap(path)
                # Scale down using KeepAspectRatio if pixmap is larger than image_label
                if (pixmap.width() > self.image_label.width()) or (pixmap.height() > self.image_label.height()):
                    pixmap = pixmap.scaled(
                        self.image_label.size(),
                        Qt.AspectRatioMode.KeepAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                self.image_label.setPixmap(pixmap)
                self.media_info.appendPlainText(
                    f"Resolution: {pixmap.width()} x {pixmap.height()}"
                )
            self.preview_stack.setCurrentIndex(1)
        elif ext in self.video_extensions:
            # Reset controls before loading new media
            self.seek_slider.setValue(0)
            self.seek_slider.setRange(0, 0)
            self.time_label.setText("00:00 / 00:00")
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            
            # Load and play the media
            self.media_player.setSource(QUrl.fromLocalFile(path))
            # Make video widget visible for video files
            self.video_widget.setVisible(True)
            # Hide audio label
            self.audio_label.setVisible(False)
            self.media_player.play()
            self.preview_stack.setCurrentIndex(2)
        elif ext in self.audio_extensions:
            # Reset controls before loading new audio
            self.seek_slider.setValue(0)
            self.seek_slider.setRange(0, 0)
            self.time_label.setText("00:00 / 00:00")
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
            
            self.media_player.setSource(QUrl.fromLocalFile(path))
            self.video_widget.setVisible(False)
            self.audio_label.setVisible(True)
            filename = os.path.basename(path)
            self.audio_label.setText(f"<div style='padding: 20px; border-radius: 10px;'>"
                                    f"<div style='font-size: 24pt; color: {'white' if self.dark_mode else 'black'};'>{filename}</div>"
                                    f"</div>")
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
                self.text_preview.setPlainText("No preview available.")
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
            f"\nResolution: {size.width()} x {size.height()}\n"
            f"Duration: {duration_secs} seconds"
        )

    # === Video Player Control Methods ===
    def toggle_play_pause(self):
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        else:
            self.media_player.play()
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
    
    def is_slider_dragging(self, dragging):
        self.slider_dragging = dragging
    
    def set_position(self, position):
        self.media_player.setPosition(position)
    
    def update_position(self, position):
        try:
            if not self.slider_dragging:
                self.seek_slider.setValue(position)
            
            # Update time label
            total_duration = self.media_player.duration()
            
            # Convert milliseconds to MM:SS format
            current_mins = position // 60000
            current_secs = (position % 60000) // 1000
            total_mins = total_duration // 60000
            total_secs = (total_duration % 60000) // 1000
            
            self.time_label.setText(f"{current_mins:02d}:{current_secs:02d} / {total_mins:02d}:{total_secs:02d}")
        except Exception as e:
            # Silently handle errors during position update to prevent player crashes
            pass
        
    def update_duration(self, duration):
        self.seek_slider.setRange(0, duration)
        
        # Update play button state
        if duration > 0:
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
            self.update_video_info()
    
    def set_volume(self, volume):
        # Convert 0-100 range to 0.0-1.0
        self.audio_output.setVolume(volume / 100.0)
        
        # Update volume button icon based on volume level
        if volume == 0:
            self.volume_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolumeMuted))
        else:
            self.volume_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))
    
    def toggle_mute(self):
        if self.audio_output.isMuted():
            self.audio_output.setMuted(False)
            self.volume_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))
            self.volume_slider.setValue(int(self.audio_output.volume() * 100))
        else:
            self.audio_output.setMuted(True)
            self.volume_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolumeMuted))
    
    def on_slider_pressed(self):
        self.slider_dragging = True
        # Store current playing state
        self.was_playing = self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
        if self.was_playing:
            self.media_player.pause()
    
    def on_slider_released(self):
        self.slider_dragging = False
        # Restore playing state if it was playing before
        if self.was_playing:
            self.media_player.play()
        
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

    def start_search(self, extra_clause=None):
        query = self.edit_query.text().strip()
        directory = self.edit_dir.text().strip()
        if not query and extra_clause is None:
            self.tree.clear()
            self.lbl_items_found.setText("0 items found")
            return

        if self.search_worker is not None and self.search_worker.isRunning():
            self.search_worker.stop()
            self.search_worker.wait()

        self.search_worker = SearchWorker(
            query, directory,
            self.chk_file_name.isChecked(),
            self.chk_match_case.isChecked(),
            self.chk_full_match.isChecked(),
            extra_clause  # Pass extra clause if provided.
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
                if os.path.isdir(path):
                    shutil.rmtree(path)  # Delete directory and contents
                else:
                    os.remove(path)  # Delete file
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
                    if os.path.isdir(path):
                        shutil.rmtree(path)  # Delete directory and contents
                    else:
                        os.remove(path)  # Delete file
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
        new_name, ok = QInputDialog.getText(self, "Rename File", f"Enter new name for {old_name}:", QLineEdit.EchoMode.Normal, old_name)
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
        # Save preview state to config
        self.preview_enabled = checked
        cfg = read_config()
        cfg["preview_enabled"] = checked
        write_config(cfg)
    
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
            QToolButton {
                background-color: #e0e0e0;
                border: 1px solid #c0c0c0;
                border-radius: 4px;
                padding: 4px;
                color: #000000;
            }
            QToolButton:hover {
                background-color: #d0d0d0;
            }
            QSlider::groove:horizontal {
                border: 1px solid #c0c0c0;
                height: 4px;
                background: #e0e0e0;
                margin: 2px 0;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #007acc;
                border: 1px solid #007acc;
                width: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::handle:horizontal:hover {
                background: #0098ff;
            }
            QSlider::add-page:horizontal {
                background: #e0e0e0;
            }
            QSlider::sub-page:horizontal {
                background: #a0c8e8;
            }
        """)
        
        # Update close button style for light mode
        if hasattr(self, 'preview_container'):
            close_btn = self.preview_container.findChild(QPushButton, "previewCloseButton")
            if close_btn:
                close_btn.setStyleSheet("""
                    #previewCloseButton {
                        border: none;
                        border-radius: 12px;
                        font-size: 14px;
                        font-weight: bold;
                        background-color: transparent;
                        color: #555555;
                    }
                    #previewCloseButton:hover {
                        background-color: #d32f2f;
                        color: white;
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
            QToolButton {
                background-color: #5a5a5a;
                border: 1px solid #707070;
                border-radius: 4px;
                padding: 4px;
                color: #f0f0f0;
            }
            QToolButton:hover {
                background-color: #707070;
            }
            QSlider::groove:horizontal {
                border: 1px solid #707070;
                height: 4px;
                background: #5a5a5a;
                margin: 2px 0;
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                background: #007acc;
                border: 1px solid #0098ff;
                width: 12px;
                margin: -4px 0;
                border-radius: 6px;
            }
            QSlider::handle:horizontal:hover {
                background: #0098ff;
            }
            QSlider::add-page:horizontal {
                background: #3c3f41;
            }
            QSlider::sub-page:horizontal {
                background: #145880;
            }
        """)
        
        # Update close button style for dark mode
        if hasattr(self, 'preview_container'):
            close_btn = self.preview_container.findChild(QPushButton, "previewCloseButton")
            if close_btn:
                close_btn.setStyleSheet("""
                    #previewCloseButton {
                        border: none;
                        border-radius: 12px;
                        font-size: 14px;
                        font-weight: bold;
                        background-color: transparent;
                        color: #aaaaaa;
                    }
                    #previewCloseButton:hover {
                        background-color: #c62828;
                        color: white;
                    }
                """)

    def toggle_dark_mode(self, checked):
        if checked:
            self.set_dark_mode()
        else:
            self.set_non_dark_mode()
            
        # Update the standalone player too
        self.standalone_player.set_dark_mode(checked)
        
        # Update the audio label only if there's media currently playing
        if hasattr(self, 'media_player') and self.media_player.source().isValid():
            current_path = self.media_player.source().toLocalFile()
            if current_path:
                filename = os.path.basename(current_path)
                self.audio_label.setText(f"<div style='padding: 20px; border-radius: 10px;'>"
                        f"<div style='font-size: 24pt; color: {'white' if checked else 'black'};'>{filename}</div>"
                        f"</div>")

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
<p><b>Version:</b> 1.2.1</p>
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

    def apply_dialog_dark_mode(self, dialog):
        """Apply dark mode styling to dialog boxes if dark mode is enabled"""
        if self.dark_mode:
            dialog.setStyleSheet("""
                QMessageBox {
                    background-color: #2d2d30;
                    color: #f0f0f0;
                }
                QLabel {
                    color: #f0f0f0;
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
            """)

    def show_info(self, title, message):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(message)
        self.apply_dialog_dark_mode(msg)
        msg.exec()

    def show_warning(self, title, message):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(message)
        self.apply_dialog_dark_mode(msg)
        msg.exec()

    def show_critical(self, title, message):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText(message)
        self.apply_dialog_dark_mode(msg)
        msg.exec()

    def show_question(self, title, message, buttons):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setIcon(QMessageBox.Icon.Question)
        msg.setText(message)
        msg.setStandardButtons(buttons)
        self.apply_dialog_dark_mode(msg)
        return msg.exec()

    def closeEvent(self, event):
        config = read_config()
        config["window_size"] = {"width": self.width(), "height": self.height()}
        write_config(config)
        super().closeEvent(event)
    
    # === Updated bookmark methods ===
    def bookmark_large_files(self):
        clause = 'kMDItemFSSize >= 52428800'
        self.start_search(extra_clause=clause)

    def bookmark_videos(self):
        clause = 'kMDItemContentTypeTree = "public.movie"'
        self.start_search(extra_clause=clause)

    def bookmark_audio(self):
        clause = 'kMDItemContentTypeTree = "public.audio"'
        self.start_search(extra_clause=clause)

    def bookmark_images(self):
        clause = 'kMDItemContentTypeTree = "public.image"'
        self.start_search(extra_clause=clause)

    def bookmark_archives(self):
        clause = 'kMDItemContentTypeTree = "public.archive"'
        self.start_search(extra_clause=clause)

    def bookmark_applications(self):
        clause = 'kMDItemContentType == "com.apple.application-bundle"'
        self.start_search(extra_clause=clause)

    # Close the preview panel
    def close_preview(self):
        # Update the menu action state
        self.toggle_preview_action.setChecked(False)
        
        # Close the standalone player if it's active
        if self.standalone_player_active:
            self.standalone_player.close()
            self.standalone_player_active = False
        
        # Call the existing toggle_preview method with False to hide the panel
        self.toggle_preview(False)

    # toggle continuous playback method
    def toggle_continuous_playback(self, checked):
        self.continuous_playback = checked
        # Update the standalone player too
        self.standalone_player.set_continuous_playback(checked)
        cfg = read_config()
        cfg["continuous_playback"] = checked
        write_config(cfg)

    # media playback state change handler
    def on_playback_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.StoppedState:
            # Check if the media actually finished playing (not stopped manually)
            # and if continuous playback is enabled
            if self.continuous_playback and self.media_player.position() > 0:
                # Media finished playing, play the next one
                self.play_next_media()

    # method to play the next media file
    def play_next_media(self):
        # Get all items in the tree
        item_count = self.tree.topLevelItemCount()
        if item_count == 0:
            return

        # Find the currently selected item
        current_index = -1
        selected_items = self.tree.selectedItems()
        if selected_items:
            current_item = selected_items[0]
            for i in range(item_count):
                if self.tree.topLevelItem(i) == current_item:
                    current_index = i
                    break

        # Find the next media file
        next_index = current_index + 1
        while next_index < item_count:
            next_item = self.tree.topLevelItem(next_index)
            path = next_item.text(3)
            _, ext = os.path.splitext(path)
            ext = ext.lower()
            
            if ext in self.video_extensions or ext in self.audio_extensions:
                # Select the item in the tree
                self.tree.setCurrentItem(next_item)
                self.tree.scrollToItem(next_item)
                
                # Try to play the media
                try:
                    # Make sure preview panel is visible
                    if not self.preview_container.isVisible():
                        self.toggle_preview(True)
                        self.toggle_preview_action.setChecked(True)
                    
                    # Setup for audio or video playback
                    if ext in self.video_extensions:
                        self.video_widget.setVisible(True)
                        self.audio_label.setVisible(False)
                    elif ext in self.audio_extensions:
                        self.video_widget.setVisible(False)
                        self.audio_label.setVisible(True)
                        filename = os.path.basename(path)
                        self.audio_label.setText(f"<div style='padding: 20px; border-radius: 10px;'>"
                                               f"<div style='font-size: 24pt; color: {'white' if self.dark_mode else 'black'};'>{filename}</div>"
                                               f"</div>")
                    
                    # Load and play the media
                    self.media_player.setSource(QUrl.fromLocalFile(path))
                    self.media_player.play()
                    self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
                    self.preview_stack.setCurrentIndex(2)  # Show media player widget
                    return
                except Exception as e:
                    print(f"Failed to play media file: {path}, error: {str(e)}")
                    # If it fails, continue to the next one
            
            next_index += 1

    def open_standalone_player(self):
        """Open the current media in a standalone player window"""
        # If the standalone player is already active, just restore and bring it to front
        if self.standalone_player_active:
            # Restore from minimized state if needed
            self.standalone_player.setWindowState(self.standalone_player.windowState() & ~Qt.WindowState.WindowMinimized)
            self.standalone_player.show()
            self.standalone_player.raise_()
            return
            
        selected_items = self.tree.selectedItems()
        if not selected_items or len(selected_items) != 1:
            return
            
        path = selected_items[0].text(3)
        if not os.path.isfile(path):
            return
            
        _, ext = os.path.splitext(path)
        ext = ext.lower()
        
        if ext not in self.video_extensions and ext not in self.audio_extensions:
            return  # Only open for media files
            
        # Stop the embedded player
        self.media_player.stop()
        
        # Set up and show the standalone player
        is_video = ext in self.video_extensions
        self.standalone_player.play_media(path, is_video)
        self.standalone_player_active = True
        self.standalone_player.show()
        self.standalone_player.raise_()
        
        # Update UI to reflect that media is playing in standalone player
        self.preview_stack.setCurrentIndex(0)  # Switch to text preview
        self.text_preview.setPlainText("Media playing in standalone player window.")
    
    def show_in_standalone_player(self, path):
        """Show the given media path in the standalone player"""
        if not self.standalone_player_active:
            return
            
        _, ext = os.path.splitext(path)
        ext = ext.lower()
        
        if ext in self.video_extensions or ext in self.audio_extensions:
            is_video = ext in self.video_extensions
            self.standalone_player.play_media(path, is_video)
            self.standalone_player.raise_()
            
            # Update UI to reflect that media is playing in standalone player
            self.preview_stack.setCurrentIndex(0)  # Switch to text preview
            self.text_preview.setPlainText("Media playing in standalone player window.")
    
    def restore_embedded_player(self):
        """Called when the standalone player is closed"""
        if not self.standalone_player_active:
            return
            
        self.standalone_player_active = False
        
        # If there's a selected item, show it in the embedded player
        selected_items = self.tree.selectedItems()
        if selected_items and len(selected_items) == 1:
            path = selected_items[0].text(3)
            if os.path.isfile(path):
                # Re-trigger selection change to reload the preview
                self.on_tree_selection_changed()
    
    def play_next_in_standalone(self):
        """Play the next media file in the standalone player"""
        if not self.standalone_player_active:
            return
            
        # Find the next media file just like in play_next_media
        item_count = self.tree.topLevelItemCount()
        if item_count == 0:
            return

        # Find the currently selected item
        current_index = -1
        selected_items = self.tree.selectedItems()
        if selected_items:
            current_item = selected_items[0]
            for i in range(item_count):
                if self.tree.topLevelItem(i) == current_item:
                    current_index = i
                    break

        # Find the next media file
        next_index = current_index + 1
        while next_index < item_count:
            next_item = self.tree.topLevelItem(next_index)
            path = next_item.text(3)
            _, ext = os.path.splitext(path)
            ext = ext.lower()
            
            if ext in self.video_extensions or ext in self.audio_extensions:
                # Select the item in the tree
                self.tree.setCurrentItem(next_item)
                self.tree.scrollToItem(next_item)
                
                # Play in standalone player
                is_video = ext in self.video_extensions
                self.standalone_player.play_media(path, is_video)
                return
            
            next_index += 1
    
    def toggle_continuous_playback(self, checked):
        self.continuous_playback = checked
        # Update the standalone player too
        self.standalone_player.set_continuous_playback(checked)
        cfg = read_config()
        cfg["continuous_playback"] = checked
        write_config(cfg)

    def eventFilter(self, obj, event):
        if event.type() == event.Type.MouseButtonPress and (obj == self.video_widget or obj == self.audio_label):
            if event.button() == Qt.MouseButton.LeftButton:
                self.toggle_play_pause()
                return True
        return super().eventFilter(obj, event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("Everything by mdfind")
    app.setOrganizationName("AppleDragon")
    
    window = MdfindApp()
    window.show()
    
    try:
        sys.exit(app.exec())
    except Exception as e:
        print(f"Application error: {e}")
