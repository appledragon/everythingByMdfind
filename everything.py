# Copyright 2025 Apple Dragon
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import sys
import os
import json
import subprocess
import time
import csv
import shutil
import zipfile

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
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        
        # Create label
        self.label = QLabel()
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        font = QFont()
        font.setPointSize(16)
        font.setBold(True)
        font.setWeight(QFont.Weight.ExtraBold)
        self.label.setFont(font)
        
        # Add text shadow effect to label
        label_shadow = QGraphicsDropShadowEffect()
        label_shadow.setBlurRadius(8)
        label_shadow.setOffset(2, 2)
        label_shadow.setColor(QColor(0, 0, 0, 180))
        self.label.setGraphicsEffect(label_shadow)
        
        layout.addWidget(self.label)
        
        # Set up style
        self.setup_style()
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 6)
        shadow.setColor(QColor(0, 0, 0, 200))
        self.setGraphicsEffect(shadow)
        
        # Animation
        self.opacity_animation = QPropertyAnimation(self, b"windowOpacity")
        self.opacity_animation.setDuration(200)
        self.opacity_animation.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        # Auto-hide timer
        self.hide_timer = QTimer()
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self.fade_out)
        
    def setup_style(self):
        self.setStyleSheet("""
            BeautifulToolTip {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(76, 175, 80, 200),
                    stop: 1 rgba(56, 142, 60, 200));
                border-radius: 15px;
                border: 3px solid rgba(255, 255, 255, 120);
            }
            QLabel {
                color: white;
                font-weight: bold;
                font-size: 16px;
                background: transparent;
                border: none;
                padding: 2px;
            }
        """)
    
    def setup_dark_style(self):
        self.setStyleSheet("""
            BeautifulToolTip {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 rgba(33, 150, 243, 180),
                    stop: 1 rgba(25, 118, 210, 180));
                border-radius: 15px;
                border: 3px solid rgba(255, 255, 255, 150);
            }
            QLabel {
                color: white;
                font-weight: bold;
                font-size: 16px;
                background: transparent;
                border: none;
                padding: 2px;
            }
        """)
    
    def show_message(self, message, parent_widget, duration=2000):
        # Stop any existing animations and timers first
        self.hide_timer.stop()
        self.opacity_animation.stop()
        
        # Safely disconnect any existing signal connections to prevent conflicts
        try:
            self.opacity_animation.finished.disconnect()
        except TypeError:
            # No connections exist, which is fine
            pass
        
        self.label.setText(message)
        
        # Position relative to parent widget
        if parent_widget:
            parent_rect = parent_widget.geometry()
            parent_center = parent_widget.mapToGlobal(parent_rect.center())
            
            # Position tooltip above the center of parent widget
            tooltip_x = parent_center.x() - self.width() // 2
            tooltip_y = parent_center.y() - parent_rect.height() // 2 - self.height() - 20
            
            # Ensure tooltip stays within screen bounds
            screen = QApplication.primaryScreen().geometry()
            if tooltip_x < 10:
                tooltip_x = 10
            elif tooltip_x + self.width() > screen.width() - 10:
                tooltip_x = screen.width() - self.width() - 10
            
            if tooltip_y < 10:
                tooltip_y = parent_center.y() + parent_rect.height() // 2 + 20
            
            self.move(tooltip_x, tooltip_y)
        
        # Show with fade-in animation
        self.setWindowOpacity(0.0)
        self.show()
        self.raise_()
        
        self.opacity_animation.setStartValue(0.0)
        self.opacity_animation.setEndValue(1.0)
        self.opacity_animation.start()
        
        # Auto-hide after duration
        self.hide_timer.start(duration)
    
    def fade_out(self):
        # Stop the hide timer to prevent conflicts
        self.hide_timer.stop()
        
        self.opacity_animation.setStartValue(1.0)
        self.opacity_animation.setEndValue(0.0)
        
        # Connect the finished signal only when we need it
        self.opacity_animation.finished.connect(self.hide_and_cleanup)
        self.opacity_animation.start()
    
    def hide_and_cleanup(self):
        """Hide the tooltip and clean up signal connections"""
        # Safely disconnect all signals to prevent conflicts
        try:
            self.opacity_animation.finished.disconnect()
        except TypeError:
            # No connections exist, which is fine
            pass
        self.hide()
        # Reset opacity for next time
        self.setWindowOpacity(1.0)


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


# Class to manage individual search tabs
class SearchTab:
    """Manages the data and widgets for a single search tab"""
    def __init__(self, query="", directory="", file_name_search=True, match_case=False, full_match=False, min_size="", max_size="", extensions=""):
        # Search parameters
        self.query = query
        self.directory = directory
        self.file_name_search = file_name_search
        self.match_case = match_case
        self.full_match = full_match
        self.min_size = min_size
        self.max_size = max_size
        self.extensions = extensions
        
        # Search results data
        self.all_file_data = []
        self.file_data = []
        self.current_loaded = 0
        self.items_found_count = 0  # Store the number of items found for this tab
        
        # Create the tree widget for this tab
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
        
        # Sort settings
        self.sort_column = -1
        self.sort_order = Qt.SortOrder.AscendingOrder
        
        # Search worker thread
        self.search_worker = None


# Thread class to run mdfind in the background.
# Reads results line by line based on search parameters and sends them to the main thread.
class SearchWorker(QThread):
    """Thread class to run mdfind in the background.
    Reads results line by line based on search parameters and sends them to the main thread."""
    progress_signal = pyqtSignal(int)
    result_signal = pyqtSignal(list)
    error_signal = pyqtSignal(str)
    
    def __init__(self, query, directory, search_by_file_name, match_case, full_match, extra_clause=None, is_bookmark=False):
        super().__init__()
        self.query = query
        self.directory = directory
        self.search_by_file_name = search_by_file_name
        self.match_case = match_case
        self.full_match = full_match
        self.extra_clause = extra_clause
        self.is_bookmark = is_bookmark
        self._is_running = True
        self.process = None

    def run(self):
        files_info = []
        idx = 0
        cmd = ["mdfind"]

        # If it's a bookmark search, use only the extra clause
        if self.is_bookmark and self.extra_clause is not None:
            query_str = self.extra_clause
        else:
            # Normal search behavior as before
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


class MediaPlayerManager:
    """Manages media playback functionality shared between embedded and standalone players"""
    
    def __init__(self, parent=None):
        self.parent = parent
        self.audio_output = QAudioOutput()
        self.media_player = QMediaPlayer()
        self.audio_output.setVolume(0.7)  # Default 70%
        self.video_extensions = set()
        self.audio_extensions = set()
        self.current_media_path = None
        self.slider_dragging = False
        self.was_playing = False
        
    def setup_extensions(self, video_ext, audio_ext):
        """Set up the video and audio extensions"""
        self.video_extensions = video_ext
        self.audio_extensions = audio_ext
    
    def set_video_output(self, video_widget):
        """Set the video output widget"""
        self.media_player.setVideoOutput(video_widget)
        self.media_player.setAudioOutput(self.audio_output)
    
    def play_media(self, path, is_audio=False):
        """Play a media file"""
        self.current_media_path = path
        self.media_player.setSource(QUrl.fromLocalFile(path))
        self.media_player.play()
        return True
    
    def stop(self):
        """Stop media playback"""
        self.media_player.stop()
        self.current_media_path = None
    
    def pause(self):
        """Pause media playback"""
        self.media_player.pause()
    
    def toggle_play_pause(self):
        """Toggle between play and pause states"""
        if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
            self.media_player.pause()
            return False
        else:
            self.media_player.play()
            return True
    
    def set_position(self, position):
        """Set the playback position"""
        self.media_player.setPosition(position)
    
    def get_position(self):
        """Get the current playback position"""
        return self.media_player.position()
    
    def get_duration(self):
        """Get the media duration"""
        return self.media_player.duration()
    
    def set_volume(self, volume_percent):
        """Set volume as a percentage (0-100)"""
        self.audio_output.setVolume(volume_percent / 100.0)
    
    def toggle_mute(self):
        """Toggle audio mute state"""
        current_mute = self.audio_output.isMuted()
        self.audio_output.setMuted(not current_mute)
        return not current_mute
    
    def is_muted(self):
        """Check if audio is muted"""
        return self.audio_output.isMuted()
    
    def get_volume(self):
        """Get current volume as percentage (0-100)"""
        return int(self.audio_output.volume() * 100)
    
    def on_slider_pressed(self):
        """Handle slider press event"""
        self.slider_dragging = True
        self.was_playing = self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState
        if self.was_playing:
            self.media_player.pause()
    
    def on_slider_released(self):
        """Handle slider release event"""
        self.slider_dragging = False
        if self.was_playing:
            self.media_player.play()
    
    def is_audio_file(self, path):
        """Check if file is an audio file based on extension"""
        _, ext = os.path.splitext(path)
        return ext.lower() in self.audio_extensions
    
    def is_video_file(self, path):
        """Check if file is a video file based on extension"""
        _, ext = os.path.splitext(path)
        return ext.lower() in self.video_extensions
    
    def is_media_file(self, path):
        """Check if file is either audio or video"""
        return self.is_audio_file(path) or self.is_video_file(path)
    
    def connect_signals(self, position_callback, duration_callback, state_callback):
        """Connect signal handlers for the media player"""
        self.media_player.positionChanged.connect(position_callback)
        self.media_player.durationChanged.connect(duration_callback)
        self.media_player.playbackStateChanged.connect(state_callback)


# Update StandalonePlayerWindow to use MediaPlayerManager
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
        self.time_label = QLabel("🕒 00:00 / 00:00")
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
        
        # Create the media player manager
        self.player_manager = MediaPlayerManager(self)
        self.player_manager.set_video_output(self.video_widget)
        
        # Connect signals
        self.play_button.clicked.connect(self.toggle_play_pause)
        self.seek_slider.sliderMoved.connect(self.player_manager.set_position)
        self.seek_slider.sliderPressed.connect(self.player_manager.on_slider_pressed)
        self.seek_slider.sliderReleased.connect(self.player_manager.on_slider_released)
        self.volume_button.clicked.connect(self.toggle_mute)
        self.volume_slider.valueChanged.connect(self.player_manager.set_volume)
        
        # Connect media player signals
        self.player_manager.connect_signals(
            self.update_position, 
            self.update_duration,
            self.on_playback_state_changed
        )
        
        self.setCentralWidget(central_widget)
        self.continuous_playback = False
        self.dark_mode = False
        self.current_media_path = None
        
    def setup_extensions(self, video_ext, audio_ext):
        """Set up the video and audio extensions from the parent app"""
        self.player_manager.setup_extensions(video_ext, audio_ext)
        
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
        
        # Use the player manager to play the media
        self.player_manager.play_media(path)
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        
    def toggle_play_pause(self):
        is_playing = self.player_manager.toggle_play_pause()
        icon = QStyle.StandardPixmap.SP_MediaPause if is_playing else QStyle.StandardPixmap.SP_MediaPlay
        self.play_button.setIcon(self.style().standardIcon(icon))
    
    def update_position(self, position):
        try:
            if not self.player_manager.slider_dragging:
                self.seek_slider.setValue(position)
            
            total_duration = self.player_manager.get_duration()
            current_mins = position // 60000
            current_secs = (position % 60000) // 1000
            total_mins = total_duration // 60000
            total_secs = (total_duration % 60000) // 1000
            
            self.time_label.setText(f"🕒 {current_mins:02d}:{current_secs:02d} / {total_mins:02d}:{total_secs:02d}")
        except Exception:
            pass
    
    def update_duration(self, duration):
        self.seek_slider.setRange(0, duration)
        if duration > 0:
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
    
    def toggle_mute(self):
        is_muted = self.player_manager.toggle_mute()
        icon = QStyle.StandardPixmap.SP_MediaVolumeMuted if is_muted else QStyle.StandardPixmap.SP_MediaVolume
        self.volume_button.setIcon(self.style().standardIcon(icon))
        
        if not is_muted:
            self.volume_slider.setValue(self.player_manager.get_volume())
    
    def on_playback_state_changed(self, state):
        if state == QMediaPlayer.PlaybackState.StoppedState:
            if self.continuous_playback and self.player_manager.get_position() > 0:
                # Signal to the main app that we need to play the next media
                self.parent().play_next_in_standalone()
    
    def closeEvent(self, event):
        # Signal the parent to restore the embedded player
        self.parent().restore_embedded_player()
        event.accept()
        
    def get_current_position(self):
        """Get the current position of the media player"""
        return self.player_manager.get_position()
    
    def get_playback_state(self):
        """Get the current playback state (playing/paused)"""
        return self.player_manager.media_player.playbackState()
    
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
        
        # Set window properties for modern appearance
        self.setWindowFlags(self.windowFlags())

        # Define recognizable extensions before initializing extension emoji map
        self.image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp",".heic"}
        self.video_extensions = {".mp4", ".mov", ".avi", ".mkv", ".mpg", ".mpeg"}
        self.audio_extensions = {".mp3", ".wav", ".aac", ".ogg", ".flac", ".m4a", ".wma", ".caf",".aif",".m4r",".au"}

        # ========== Menu Bar ==========
        menubar = self.menuBar()
        help_menu = menubar.addMenu('❓ Help')
        about_action = help_menu.addAction('ℹ️ About')
        about_action.triggered.connect(self.show_about_dialog)
        # Add a "History" menu
        history_menu = menubar.addMenu('📚 History')
        clear_history_action = history_menu.addAction('🧹 Clear History')
        clear_history_action.triggered.connect(self.clear_history)
        enable_history_action = history_menu.addAction("✅ Enable History")
        enable_history_action.setCheckable(True)
        enable_history_action.setChecked(self.history_enabled)
        enable_history_action.triggered.connect(self.toggle_history)

        # Add a "View" menu
        view_menu = menubar.addMenu('👀 View')
        toggle_preview_action = view_menu.addAction('👁️ Toggle Preview')
        toggle_preview_action.setCheckable(True)
        toggle_preview_action.setChecked(self.preview_enabled) # Use the loaded setting instead of hardcoded False
        toggle_preview_action.triggered.connect(self.toggle_preview)
        # Store reference to the toggle_preview_action for later use
        self.toggle_preview_action = toggle_preview_action

        # Add continuous playback action
        continuous_playback_action = view_menu.addAction('🔄 Continuous Playback')
        continuous_playback_action.setCheckable(True)
        continuous_playback_action.setChecked(self.continuous_playback)
        continuous_playback_action.triggered.connect(self.toggle_continuous_playback)
        self.continuous_playback_action = continuous_playback_action
        
        # Added dark mode toggle action in the View menu
        dark_mode_action = view_menu.addAction('🌙 Dark Mode')
        dark_mode_action.setCheckable(True)
        dark_mode_action.setChecked(self.dark_mode)
        dark_mode_action.triggered.connect(self.toggle_dark_mode)
        if self.dark_mode:
            self.set_dark_mode()
        else:
            self.set_non_dark_mode()
        
        # === Bookmarks Menu ===
        bookmarks_menu = menubar.addMenu("🔖 Bookmarks")
        bookmarks_menu.addAction("📏 Large Files", self.bookmark_large_files)
        bookmarks_menu.addAction("🎬 Video Files", self.bookmark_videos)
        bookmarks_menu.addAction("🎵 Audio Files", self.bookmark_audio)
        bookmarks_menu.addAction("🖼️ Images", self.bookmark_images)
        bookmarks_menu.addAction("🗜️ Archives", self.bookmark_archives)
        bookmarks_menu.addAction("📱 Applications", self.bookmark_applications)
        
        self.initialize_extension_emoji_map()
        
        # ======= Main layout: QSplitter, left for search/list and right for preview ===========
        splitter = QSplitter(self)
        splitter.setOrientation(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setObjectName("mainSplitter")
        self.setCentralWidget(splitter)

        # ========== Left side ==========
        left_container = QWidget()
        left_container.setObjectName("leftContainer")
        left_layout = QVBoxLayout(left_container)
        left_layout.setContentsMargins(20, 16, 20, 16)
        left_layout.setSpacing(16)

        # First row: Search Query input and statistics
        form_layout = QHBoxLayout()
        lbl_query = QLabel("🔍 Search Query:")
        lbl_query.setObjectName("queryLabel")
        
        self.edit_query = QLineEdit()
        self.edit_query.setPlaceholderText("Enter search terms...")
        
        self.lbl_items_found = QLabel("📊 0 items found")
        self.lbl_items_found.setObjectName("itemsFoundLabel")
        
        # Add refresh button
        self.btn_refresh = QPushButton("🔄 Refresh")
        self.btn_refresh.setToolTip("Refresh current search")
        self.btn_refresh.setMaximumWidth(120)
        self.btn_refresh.clicked.connect(self.refresh_current_search)

        form_layout.addWidget(lbl_query)
        form_layout.addWidget(self.edit_query, 4)
        form_layout.addWidget(self.lbl_items_found, 1)
        form_layout.addWidget(self.btn_refresh)
        left_layout.addLayout(form_layout)

        # Second row: Directory selection (optional)
        form_layout2 = QHBoxLayout()
        lbl_dir = QLabel("📁 Directory (optional):")
        lbl_dir.setObjectName("directoryLabel")
        
        self.edit_dir = QLineEdit()
        self.edit_dir.setPlaceholderText("Leave empty to search everywhere...")
        
        btn_select_dir = QPushButton("📂 Select Dir")
        btn_select_dir.clicked.connect(self.select_directory)

        form_layout2.addWidget(lbl_dir)
        form_layout2.addWidget(self.edit_dir, 4)
        form_layout2.addWidget(btn_select_dir, 1)
        left_layout.addLayout(form_layout2)

        # Advanced Filters group
        group_advanced = QGroupBox("⚙️ Advanced Filters")
        adv_layout = QHBoxLayout()

        lbl_min_size = QLabel("📏 Min Size (bytes):")
        self.edit_min_size = QLineEdit()
        lbl_max_size = QLabel("📐 Max Size (bytes):")
        self.edit_max_size = QLineEdit()
        lbl_extension = QLabel("📄 File Extension:")
        self.edit_extension = QLineEdit()
        self.edit_extension.setPlaceholderText("pdf;docx;xls")

        self.chk_file_name = QCheckBox("📝 Search by File Name")
        self.chk_file_name.setChecked(True)
        self.chk_file_name.setToolTip("When unchecked: Search in file content and metadata")
        self.chk_match_case = QCheckBox("🔤 Match Case")
        self.chk_full_match = QCheckBox("🎯 Full Match")

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

        # Search results tabs
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.setUsesScrollButtons(True)  # Enable scroll buttons when tabs overflow
        self.tab_widget.setMovable(True)  # Allow dragging tabs to reorder
        

        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        self.tab_widget.currentChanged.connect(self.on_tab_changed)
        
        # Get screen width for tab sizing
        screen = QApplication.primaryScreen()
        screen_width = screen.size().width()
        tab_width = screen_width // 8  # Tab width is 1/8 of screen width
        
        # Set tab style similar to Chrome
        self.tab_width = tab_width
        self.update_tab_style()
        
        # Set elide mode for long titles
        self.tab_widget.setElideMode(Qt.TextElideMode.ElideRight)
        
        # Set up context menu for tabs - on tab bar instead of tab widget
        tab_bar = self.tab_widget.tabBar()
        tab_bar.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        tab_bar.customContextMenuRequested.connect(self.show_tab_context_menu)
        
        # Create tab context menu
        self.tab_context_menu = QMenu(self)
        self.tab_context_menu.addAction("❌ Close", self.close_current_tab)
        self.tab_context_menu.addAction("🚫 Close Others", self.close_other_tabs)
        self.tab_context_menu.addAction("⬅️ Close to the Left", self.close_left_tabs)
        self.tab_context_menu.addAction("➡️ Close to the Right", self.close_right_tabs)
        self.tab_context_menu.addAction("🗑️ Close All", self.close_all_tabs)
        
        left_layout.addWidget(self.tab_widget, stretch=1)
        
        # Dictionary to store SearchTab instances by tab index
        self.search_tabs = {}

        # Progress bar and Export button
        self.progress = QProgressBar()
        self.progress.setMaximum(100)
        left_layout.addWidget(self.progress)

        btn_export = QPushButton("📤 Export to CSV")
        btn_export.clicked.connect(self.export_to_csv)
        left_layout.addWidget(btn_export, alignment=Qt.AlignmentFlag.AlignRight)

        splitter.addWidget(left_container)

        # ========== Right side Preview ==========
        self.preview_container = QWidget()
        self.preview_container.setObjectName("previewContainer")
        preview_layout = QVBoxLayout(self.preview_container)
        preview_layout.setContentsMargins(16, 16, 16, 16)
        preview_layout.setSpacing(12)
        
        # Header layout with Preview title and buttons
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 8)
        
        preview_title = QLabel("🖼️ Preview")
        preview_title.setObjectName("previewTitle")
        header_layout.addWidget(preview_title)
        header_layout.addStretch()
        
        # Add a pop-out button
        popout_button = QPushButton("🔲")  # Square symbol for pop-out
        popout_button.setFixedSize(24, 24)
        popout_button.setToolTip("Open in standalone player")
        popout_button.clicked.connect(self.open_standalone_player)
        popout_button.setObjectName("previewPopoutButton")
        popout_button.setObjectName("previewPopoutButton")
        
        # Add the popout button to the header
        header_layout.addWidget(popout_button)
        
        # Add a more stylish close button to the header
        close_button = QPushButton("✕")  # Using Unicode "Heavy Multiplication X" character
        close_button.setFixedSize(24, 24)  # Keep the square size
        close_button.setToolTip("Close preview panel")
        close_button.clicked.connect(self.close_preview)
        
        # Apply special styling to the close button to make it more elegant
        close_button.setObjectName("previewCloseButton")
        
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
        self.time_label = QLabel("🕒 00:00 / 00:00")
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
        self.default_sort_column = config.get("sort_column", -1)
        self.default_sort_order = Qt.SortOrder(config.get("sort_order", 0))  # 0 = Ascending, 1 = Descending

        self.query_history = config.get("query_history", [])
        self.query_completer = QCompleter(self.query_history)
        self.query_completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.query_completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.query_completer.setMaxVisibleItems(8)  # Show max 8 items in dropdown
        self.query_completer.setFilterMode(Qt.MatchFlag.MatchContains)  # Match anywhere in string
        self.edit_query.setCompleter(self.query_completer)

        # ========== Signal bindings ==========
        self.search_timer = QTimer()
        self.search_timer.setSingleShot(True)
        self.search_timer.timeout.connect(self.start_search)
        self.edit_query.textChanged.connect(self.on_query_changed)
        # connect Enter key press
        self.edit_query.returnPressed.connect(self.on_search_enter)
        self.edit_dir.textChanged.connect(self.on_dir_changed)

        self.chk_file_name.stateChanged.connect(lambda: self.search_timer.start(DEBOUNCE_DELAY))
        self.chk_match_case.stateChanged.connect(lambda: self.search_timer.start(DEBOUNCE_DELAY))
        self.chk_full_match.stateChanged.connect(lambda: self.search_timer.start(DEBOUNCE_DELAY))
        self.edit_min_size.textChanged.connect(self.on_filter_changed)
        self.edit_max_size.textChanged.connect(self.on_filter_changed)
        self.edit_extension.textChanged.connect(self.on_filter_changed)

        self.single_context_menu = QMenu(self)
        self.single_context_menu.addAction("🚀 Open", self.open_with_default_app)
        self.single_context_menu.addAction("🗑️ Delete", self.delete_file)
        self.single_context_menu.addAction("📋 Copy to...", self.copy_file)
        self.single_context_menu.addAction("📦 Move to...", self.move_file)
        self.single_context_menu.addAction("✏️ Rename", self.rename_file)
        self.single_context_menu.addAction("📄 Copy full path with file name", self.copy_full_path)
        self.single_context_menu.addAction("📁 Copy path without file name", self.copy_path_only)
        self.single_context_menu.addAction("📝 Copy file name only", self.copy_file_name_only)
        self.single_context_menu.addSeparator()
        self.single_context_menu.addAction("🗜️ Compress to ZIP", self.compress_file)
        self.single_context_menu.addAction("🔍 Open in Finder", self.open_in_finder)
        self.single_context_menu.addAction("📤 Export to CSV", self.export_to_csv)

        self.multi_context_menu = QMenu(self)
        self.multi_context_menu.addAction("🚀 Open", self.open_multiple_files)
        self.multi_context_menu.addAction("🗑️ Delete", self.delete_multiple_files)
        self.multi_context_menu.addAction("📋 Copy to...", self.copy_multiple_files)
        self.multi_context_menu.addAction("📦 Move to...", self.move_multiple_files)
        self.multi_context_menu.addAction("✏️ Batch Rename", self.batch_rename_files)
        self.multi_context_menu.addSeparator()
        self.multi_context_menu.addAction("🗜️ Compress to ZIP", self.compress_multiple_files)

        self.batch_size = 100

        # Create the standalone player window but don't show it yet
        self.standalone_player = StandalonePlayerWindow(self)
        self.standalone_player_active = False
        
        # Configure standalone player
        self.standalone_player.setup_extensions(self.video_extensions, self.audio_extensions)
        self.standalone_player.set_continuous_playback(self.continuous_playback)
        self.standalone_player.set_dark_mode(self.dark_mode)
        
        # Create the media player manager for embedded player
        self.player_manager = MediaPlayerManager(self)
        
        # Set up media player
        self.audio_output = self.player_manager.audio_output
        self.media_player = self.player_manager.media_player
        self.player_manager.set_video_output(self.video_widget)
        self.player_manager.connect_signals(
            self.update_position,
            self.update_duration,
            self.on_playback_state_changed
        )
        
        # Set up recognized extensions in the player manager
        self.player_manager.setup_extensions(self.video_extensions, self.audio_extensions)
        
        # Initialize beautiful tooltip for copy confirmations
        self.tooltip = BeautifulToolTip(self)

    # ========== Tab Management ==========
    def get_current_tree(self):
        """Get the tree widget of the currently active tab"""
        current_index = self.tab_widget.currentIndex()
        if current_index == -1 or current_index not in self.search_tabs:
            return None
        
        # Safety check: ensure tab and tree are still valid
        tab = self.search_tabs.get(current_index)
        if tab and hasattr(tab, 'tree'):
            try:
                # Test if tree is still valid
                tab.tree.topLevelItemCount()
                return tab.tree
            except RuntimeError:
                # Tree widget is destroyed
                return None
        return None
    
    def get_current_tab(self):
        """Get the SearchTab instance of the currently active tab"""
        current_index = self.tab_widget.currentIndex()
        if current_index == -1 or current_index not in self.search_tabs:
            return None
        return self.search_tabs[current_index]
    
    def create_new_tab(self, query="", directory="", tab_title=""):
        """Create a new search tab"""
        # Create SearchTab instance with current search parameters
        search_tab = SearchTab(
            query=query or self.edit_query.text().strip(),
            directory=directory or self.edit_dir.text().strip(),
            file_name_search=self.chk_file_name.isChecked(),
            match_case=self.chk_match_case.isChecked(),
            full_match=self.chk_full_match.isChecked(),
            min_size=self.edit_min_size.text().strip(),
            max_size=self.edit_max_size.text().strip(),
            extensions=self.edit_extension.text().strip()
        )
        
        # Apply default sort settings
        search_tab.sort_column = self.default_sort_column
        search_tab.sort_order = self.default_sort_order
        if self.default_sort_column != -1:
            search_tab.tree.header().setSortIndicator(self.default_sort_column, self.default_sort_order)
        
        # Connect tree signals
        search_tab.tree.itemSelectionChanged.connect(self.on_tree_selection_changed)
        search_tab.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        search_tab.tree.customContextMenuRequested.connect(self.show_context_menu)
        search_tab.tree.itemDoubleClicked.connect(self.open_with_default_app)
        search_tab.tree.header().setSectionsClickable(True)
        search_tab.tree.header().setSortIndicatorShown(True)
        search_tab.tree.header().sectionClicked.connect(self.on_header_clicked)
        search_tab.tree.verticalScrollBar().valueChanged.connect(self.check_scroll_position)
        
        # Create tab title - use custom title if provided, otherwise use query or default
        if tab_title:
            final_tab_title = tab_title
        elif query:
            final_tab_title = query
        else:
            final_tab_title = "New Search"
        
        # Add tab to widget
        index = self.tab_widget.addTab(search_tab.tree, final_tab_title)
        self.search_tabs[index] = search_tab
        self.tab_widget.setCurrentIndex(index)
        
        # Set custom close button for better visibility
        self.update_tab_close_button(index)
        
        # Update tab widths for all tabs
        self.update_tab_style()
        
        return search_tab
    
    def close_tab(self, index):
        """Close a search tab"""
        if index in self.search_tabs:
            # Stop any running search
            tab = self.search_tabs[index]
            if tab.search_worker and tab.search_worker.isRunning():
                tab.search_worker.stop()
                tab.search_worker.wait()
            
            # Disconnect tree signals to prevent crashes
            try:
                tab.tree.itemSelectionChanged.disconnect()
                tab.tree.customContextMenuRequested.disconnect()
                tab.tree.itemDoubleClicked.disconnect()
                tab.tree.header().sectionClicked.disconnect()
                tab.tree.verticalScrollBar().valueChanged.disconnect()
            except:
                pass  # Ignore if already disconnected
            
            # Remove tab
            del self.search_tabs[index]
            self.tab_widget.removeTab(index)
            
            # Update indices for remaining tabs
            new_tabs = {}
            for i in range(self.tab_widget.count()):
                old_index = None
                for old_i, tab in self.search_tabs.items():
                    if self.tab_widget.widget(i) == tab.tree:
                        old_index = old_i
                        break
                if old_index is not None:
                    new_tabs[i] = self.search_tabs[old_index]
            self.search_tabs = new_tabs
            
            # Update tab widths after closing
            if self.tab_widget.count() > 0:
                self.update_tab_style()
    
    def on_tab_changed(self, index):
        """Handle tab change event"""
        if index >= 0:
            # Get the search tab for this index
            current_tab = self.get_current_tab()
            if current_tab:
                # Temporarily block signals to prevent triggering new searches
                self.edit_query.blockSignals(True)
                self.edit_dir.blockSignals(True)
                self.chk_file_name.blockSignals(True)
                self.chk_match_case.blockSignals(True)
                self.chk_full_match.blockSignals(True)
                self.edit_min_size.blockSignals(True)
                self.edit_max_size.blockSignals(True)
                self.edit_extension.blockSignals(True)
                
                try:
                    # Update the query input field with the tab's query
                    self.edit_query.setText(current_tab.query)
                    
                    # Update the directory input field with the tab's directory
                    self.edit_dir.setText(current_tab.directory)
                    
                    # Update the checkboxes with the tab's search parameters
                    self.chk_file_name.setChecked(current_tab.file_name_search)
                    self.chk_match_case.setChecked(current_tab.match_case)
                    self.chk_full_match.setChecked(current_tab.full_match)
                    
                    # Update the filter fields with the tab's filter parameters
                    self.edit_min_size.setText(current_tab.min_size)
                    self.edit_max_size.setText(current_tab.max_size)
                    self.edit_extension.setText(current_tab.extensions)
                    
                    # Update the items found label with the tab's result count
                    self.lbl_items_found.setText(f"📊 {current_tab.items_found_count} items found")
                finally:
                    # Re-enable signals
                    self.edit_query.blockSignals(False)
                    self.edit_dir.blockSignals(False)
                    self.chk_file_name.blockSignals(False)
                    self.chk_match_case.blockSignals(False)
                    self.chk_full_match.blockSignals(False)
                    self.edit_min_size.blockSignals(False)
                    self.edit_max_size.blockSignals(False)
                    self.edit_extension.blockSignals(False)
            else:
                # No current tab, reset items found label
                self.lbl_items_found.setText("📊 0 items found")
            
            # Update the preview panel based on the new tab's selection
            self.on_tree_selection_changed()
            
            # Update all tab close buttons since current tab changed
            self.update_all_tab_close_buttons()
        else:
            # No tabs available (index < 0), reset items found label
            self.lbl_items_found.setText("📊 0 items found")
    
    def show_tab_context_menu(self, pos):
        """Show context menu for tabs"""
        # Get the tab bar
        tab_bar = self.tab_widget.tabBar()
        
        # Find which tab was clicked
        self.context_menu_tab_index = tab_bar.tabAt(pos)
        
        if self.context_menu_tab_index >= 0:
            # Show the context menu at the cursor position
            global_pos = tab_bar.mapToGlobal(pos)
            self.tab_context_menu.exec(global_pos)
    
    def close_current_tab(self):
        """Close the tab that was right-clicked"""
        if hasattr(self, 'context_menu_tab_index') and self.context_menu_tab_index >= 0:
            self.close_tab(self.context_menu_tab_index)
    
    def close_other_tabs(self):
        """Close all tabs except the one that was right-clicked"""
        if hasattr(self, 'context_menu_tab_index') and self.context_menu_tab_index >= 0:
            # Get all tab indices
            tab_count = self.tab_widget.count()
            tabs_to_close = []
            
            # Collect indices of tabs to close (all except the clicked one)
            for i in range(tab_count):
                if i != self.context_menu_tab_index:
                    tabs_to_close.append(i)
            
            # Close tabs in reverse order to maintain correct indices
            for i in reversed(tabs_to_close):
                self.close_tab(i)
    
    def close_left_tabs(self):
        """Close all tabs to the left of the clicked tab"""
        if hasattr(self, 'context_menu_tab_index') and self.context_menu_tab_index >= 0:
            # Close tabs in reverse order from the clicked tab to the first
            for i in range(self.context_menu_tab_index - 1, -1, -1):
                self.close_tab(i)
    
    def close_right_tabs(self):
        """Close all tabs to the right of the clicked tab"""
        if hasattr(self, 'context_menu_tab_index') and self.context_menu_tab_index >= 0:
            # Get the current tab count
            tab_count = self.tab_widget.count()
            
            # Close tabs in reverse order from the last to the one after clicked tab
            for i in range(tab_count - 1, self.context_menu_tab_index, -1):
                self.close_tab(i)
    
    def close_all_tabs(self):
        """Close all search tabs"""
        tab_count = self.tab_widget.count()
        if tab_count == 0:
            return
        
        reply = self.show_question(
            "Close All Tabs",
            f"Are you sure you want to close all {tab_count} tabs?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            # Close tabs in reverse order to maintain correct indices
            for i in reversed(range(tab_count)):
                self.close_tab(i)

    # ========== Preview logic ==========
    def on_tree_selection_changed(self):
        # if preview is not visible, do nothing
        if not self.preview_container.isVisible():
            return
        
        tree = self.get_current_tree()
        if not tree:
            return
        
        # Safety check: ensure tree widget is still valid
        try:
            selected_items = tree.selectedItems()
        except RuntimeError:
            # Tree widget might be destroyed
            return
            
        if not selected_items or len(selected_items) != 1:
            # For multiple or no selection: stop media playback and clear preview
            self.player_manager.stop()
            self.preview_stack.setCurrentIndex(0)
            self.text_preview.setPlainText("")
            self.media_info.setPlainText("")  # Clear bottom pane
            return

        path = selected_items[0].text(3)
        if not os.path.isfile(path):
            self.player_manager.stop()
            self.preview_stack.setCurrentIndex(0)
            self.text_preview.setPlainText("No preview available.")
            self.media_info.setPlainText("")
            return

        # Stop previous media playback
        self.player_manager.stop()
        
        # If standalone player is active, use it instead
        if self.standalone_player_active:
            self.show_in_standalone_player(path)
            return

        # Display basic file info in the bottom pane
        self.display_file_info(path)

        # Check file extension for preview type
        _, ext = os.path.splitext(path)
        ext = ext.lower()

        if ext in self.image_extensions or ext == ".svg":
            self.display_image_preview(path, ext)
        elif ext in self.video_extensions:
            self.display_video_preview(path)
        elif ext in self.audio_extensions:
            self.display_audio_preview(path)
        else:
            self.display_text_preview(path)

    def display_file_info(self, path):
        """Display basic file information in the info pane"""
        file_stat = os.stat(path)
        size_kb = round(file_stat.st_size / 1024, 2)
        self.media_info.setPlainText(
            f"File: {path}\nSize: {size_kb} KB\nLast Modified: {time.ctime(file_stat.st_mtime)}"
        )
        
    def display_image_preview(self, path, ext):
        """Handle display of image files"""
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
        
    def display_video_preview(self, path):
        """Handle display of video files"""
        # Reset controls before loading new media
        self.seek_slider.setValue(0)
        self.seek_slider.setRange(0, 0)
        self.time_label.setText("🕒 00:00 / 00:00")
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        
        # Make video widget visible for video files
        self.video_widget.setVisible(True)
        self.audio_label.setVisible(False)
        
        # Play the media
        self.player_manager.play_media(path)
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        self.preview_stack.setCurrentIndex(2)
        
    def display_audio_preview(self, path):
        """Handle display of audio files"""
        # Reset controls before loading new audio
        self.seek_slider.setValue(0)
        self.seek_slider.setRange(0, 0)
        self.time_label.setText("🕒 00:00 / 00:00")
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        
        # Hide video, show audio label
        self.video_widget.setVisible(False)
        self.audio_label.setVisible(True)
        
        # Set audio label text
        filename = os.path.basename(path)
        self.audio_label.setText(f"<div style='padding: 20px; border-radius: 10px;'>"
                                f"<div style='font-size: 24pt; color: {'white' if self.dark_mode else 'black'};'>{filename}</div>"
                                f"</div>")
        
        # Play the media
        self.player_manager.play_media(path)
        self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
        self.preview_stack.setCurrentIndex(2)
        
    def display_text_preview(self, path):
        """Handle display of text files"""
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

    # === Video Player Control Methods ===
    def toggle_play_pause(self):
        is_playing = self.player_manager.toggle_play_pause()
        icon = QStyle.StandardPixmap.SP_MediaPause if is_playing else QStyle.StandardPixmap.SP_MediaPlay
        self.play_button.setIcon(self.style().standardIcon(icon))
    
    def set_position(self, position):
        self.player_manager.set_position(position)
    
    def update_position(self, position):
        try:
            if not self.player_manager.slider_dragging:
                self.seek_slider.setValue(position)
            
            # Update time label
            total_duration = self.player_manager.get_duration()
            
            # Convert milliseconds to MM:SS format
            current_mins = position // 60000
            current_secs = (position % 60000) // 1000
            total_mins = total_duration // 60000
            total_secs = (total_duration % 60000) // 1000
            
            self.time_label.setText(f"🕒 {current_mins:02d}:{current_secs:02d} / {total_mins:02d}:{total_secs:02d}")
        except Exception:
            # Silently handle errors during position update to prevent player crashes
            pass
        
    def update_duration(self, duration):
        self.seek_slider.setRange(0, duration)
        
        # Update play button state
        if duration > 0:
            self.play_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))
            self.update_video_info()
    
    def set_volume(self, volume):
        self.player_manager.set_volume(volume)
        
        # Update volume button icon based on volume level
        if volume == 0:
            self.volume_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolumeMuted))
        else:
            self.volume_button.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaVolume))
    
    def toggle_mute(self):
        is_muted = self.player_manager.toggle_mute()
        icon = QStyle.StandardPixmap.SP_MediaVolumeMuted if is_muted else QStyle.StandardPixmap.SP_MediaVolume
        self.volume_button.setIcon(self.style().standardIcon(icon))
        
        if not is_muted:
            self.volume_slider.setValue(self.player_manager.get_volume())
    
    def on_slider_pressed(self):
        self.player_manager.on_slider_pressed()
    
    def on_slider_released(self):
        self.player_manager.on_slider_released()
    
    # ========== Lazy loading ==========
    def check_scroll_position(self):
        tree = self.get_current_tree()
        if not tree:
            return
        scrollbar = tree.verticalScrollBar()
        if scrollbar.value() >= scrollbar.maximum() - 10:
            self.load_more_items()
            
    def initialize_extension_emoji_map(self):
        """Create a mapping of file extensions to emoji icons for better performance"""
        self.extension_emoji_map = {
            # Images
            **{ext: "📷" for ext in self.image_extensions},
            # Videos
            **{ext: "🎬" for ext in self.video_extensions},
            # Audio
            **{ext: "🎵" for ext in self.audio_extensions},
            # Documents
            **{ext: "📚" for ext in ['.pdf', '.epub', '.mobi']},
            **{ext: "📝" for ext in ['.doc', '.docx', '.rtf', '.txt', '.md']},
            # Spreadsheets
            **{ext: "📊" for ext in ['.xls', '.xlsx', '.csv']},
            # Archives
            **{ext: "🗜️" for ext in ['.zip', '.rar', '.tar', '.gz', '.7z']},
            # Code
            **{ext: "💻" for ext in ['.py', '.js', '.html', '.css', '.java', '.cpp', '.c', '.swift']},
            # Config
            **{ext: "⚙️" for ext in ['.json', '.xml', '.yml', '.yaml', '.ini', '.conf']},
        }

    def load_more_items(self, search_tab=None):
        if search_tab is None:
            search_tab = self.get_current_tab()
        if not search_tab:
            return
            
        if not search_tab.file_data or search_tab.current_loaded >= len(search_tab.file_data):
            return
        end_idx = min(search_tab.current_loaded + self.batch_size, len(search_tab.file_data))
        items_to_load = search_tab.file_data[search_tab.current_loaded:end_idx]
        
        for item in items_to_load:
            name, size, mtime, path = item
            display_size = format_size(size)
            display_time = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(mtime))
            
            # emoji based on file type
            if os.path.isdir(path):
                display_name = f"📁 {name}"
            else:
                # Get file extension and add appropriate emoji
                _, ext = os.path.splitext(name.lower())
                display_name = f"{self.extension_emoji_map.get(ext, '📄')} {name}"     
                       
            tree_item = QTreeWidgetItem([display_name, display_size, display_time, path])
            search_tab.tree.addTopLevelItem(tree_item)
        
        search_tab.current_loaded = end_idx
    # ========== Search handling ==========
    def on_query_changed(self):
        self.search_timer.start(DEBOUNCE_DELAY)

    def on_dir_changed(self):
        self.search_timer.start(DEBOUNCE_DELAY)

    def start_search(self, extra_clause=None, is_bookmark=False, tab_title=""):
        query = self.edit_query.text().strip()
        directory = self.edit_dir.text().strip()
        
        # If not bookmark, no query, and no extra clause, don't search
        if not is_bookmark and not query and extra_clause is None:
            return

        # Create a new tab for this search
        search_tab = self.create_new_tab(query, directory, tab_title)
        
        # Stop any existing search in this tab
        if search_tab.search_worker is not None and search_tab.search_worker.isRunning():
            search_tab.search_worker.stop()
            search_tab.search_worker.wait()

        # Create new search worker
        search_tab.search_worker = SearchWorker(
            query, directory,
            self.chk_file_name.isChecked(),
            self.chk_match_case.isChecked(),
            self.chk_full_match.isChecked(),
            extra_clause,  # Pass extra clause if provided
            is_bookmark    # Pass the bookmark flag
        )
        search_tab.search_worker.progress_signal.connect(self.update_progress)
        search_tab.search_worker.result_signal.connect(lambda results: self.update_tree(results, search_tab))
        search_tab.search_worker.error_signal.connect(self.show_error)
        search_tab.search_worker.start()

        # Only update history if enabled and not a bookmark search
        if not is_bookmark and self.history_enabled and query and query not in self.query_history:
            self.query_history.insert(0, query)
            if len(self.query_history) > 100:
                self.query_history.pop()
            cfg = read_config()
            cfg["query_history"] = self.query_history
            write_config(cfg)
            self.query_completer.model().setStringList(self.query_history)

    def refresh_current_search(self):
        """Refresh the current search in the active tab, or create a new tab if none exists"""
        current_tab = self.get_current_tab()
        
        # If no current tab exists, create a new search with current form parameters
        if not current_tab:
            # Use current form values to start a new search
            query = self.edit_query.text().strip()
            
            # If there's no query, don't start a search
            if not query:
                return
                
            # Start a new search which will create a new tab
            self.start_search()
            return
            
        # Get current search parameters from the tab
        query = current_tab.query
        directory = current_tab.directory
        file_name_search = current_tab.file_name_search
        match_case = current_tab.match_case
        full_match = current_tab.full_match
        
        # Stop any existing search in this tab
        if current_tab.search_worker is not None and current_tab.search_worker.isRunning():
            current_tab.search_worker.stop()
            current_tab.search_worker.wait()

        # Create new search worker with the same parameters
        current_tab.search_worker = SearchWorker(
            query, directory,
            file_name_search,
            match_case,
            full_match,
            None,  # No extra clause for refresh
            False  # Not a bookmark search
        )
        current_tab.search_worker.progress_signal.connect(self.update_progress)
        current_tab.search_worker.result_signal.connect(lambda results: self.update_tree(results, current_tab))
        current_tab.search_worker.error_signal.connect(self.show_error)
        current_tab.search_worker.start()

    def update_progress(self, value):
        self.progress.setValue(value)

    def update_tree(self, files_info, search_tab=None):
        if search_tab is None:
            search_tab = self.get_current_tab()
        if not search_tab:
            return
            
        search_tab.tree.clear()
        search_tab.all_file_data = files_info
        search_tab.current_loaded = 0
        filtered_files = self.apply_filters_and_sorting(search_tab.all_file_data)
        search_tab.file_data = filtered_files
        
        # Update the tab's items found count
        search_tab.items_found_count = len(filtered_files)
        
        if not filtered_files:
            self.lbl_items_found.setText("📊 0 items found")
            return
        
        self.lbl_items_found.setText(f"📊 {len(filtered_files)} items found")

        if search_tab.sort_column != -1:
            self.sort_data(search_tab)
        else:
            self.load_more_items(search_tab)

    def show_error(self, msg):
        self.show_critical("❌ Error", msg)

    # ========== Filtering and sorting ==========
    def on_filter_changed(self):
        """Handle changes to filter fields and update current tab attributes"""
        current_tab = self.get_current_tab()
        if current_tab:
            # Update the current tab's filter attributes
            current_tab.min_size = self.edit_min_size.text().strip()
            current_tab.max_size = self.edit_max_size.text().strip()
            current_tab.extensions = self.edit_extension.text().strip()
        
        # Reapply the filter with updated values
        self.reapply_filter()
    
    def reapply_filter(self):
        search_tab = self.get_current_tab()
        if not search_tab or not search_tab.all_file_data:
            return
        filtered_files = self.apply_filters_and_sorting(search_tab.all_file_data)
        search_tab.file_data = filtered_files
        search_tab.tree.clear()
        search_tab.current_loaded = 0
        
        # Update the tab's items found count
        search_tab.items_found_count = len(filtered_files)

        if search_tab.sort_column != -1:
            self.sort_data(search_tab)
        else:
            self.load_more_items(search_tab)

        self.lbl_items_found.setText(f"📊 {len(filtered_files)} items found")

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
        search_tab = self.get_current_tab()
        if not search_tab:
            return
            
        if search_tab.sort_column == column:
            search_tab.sort_order = (Qt.SortOrder.DescendingOrder
                               if search_tab.sort_order == Qt.SortOrder.AscendingOrder
                               else Qt.SortOrder.AscendingOrder)
        else:
            search_tab.sort_column = column
            search_tab.sort_order = Qt.SortOrder.AscendingOrder
        search_tab.tree.header().setSortIndicator(column, search_tab.sort_order)
        self.sort_data(search_tab)

    def sort_data(self, search_tab=None):
        if search_tab is None:
            search_tab = self.get_current_tab()
        if not search_tab:
            return
            
        if not search_tab.file_data or search_tab.sort_column == -1:
            return

        def get_sort_key(item):
            if search_tab.sort_column == 0:
                return item[0].lower()
            elif search_tab.sort_column == 1:
                return float(item[1])
            elif search_tab.sort_column == 2:
                return float(item[2])
            else:
                return item[3].lower()

        search_tab.file_data.sort(
            key=get_sort_key,
            reverse=(search_tab.sort_order == Qt.SortOrder.DescendingOrder)
        )
        search_tab.tree.clear()
        search_tab.current_loaded = 0
        self.load_more_items(search_tab)

    # ========== Context menu logic ==========
    def show_context_menu(self, pos):
        tree = self.get_current_tree()
        if not tree:
            return
        selected_items = tree.selectedItems()
        if not selected_items:
            return
        if len(selected_items) == 1:
            tree.setCurrentItem(selected_items[0])
            self.single_context_menu.exec(tree.viewport().mapToGlobal(pos))
        else:
            self.multi_context_menu.exec(tree.viewport().mapToGlobal(pos))

    def get_selected_file(self):
        tree = self.get_current_tree()
        if not tree:
            return None
        item = tree.currentItem()
        if item:
            return item.text(3)
        return None

    def get_selected_files(self):
        tree = self.get_current_tree()
        if not tree:
            return []
        return [item.text(3) for item in tree.selectedItems()]

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
            "🗑️ Delete",
            f"Are you sure you want to delete '{path}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if os.path.isdir(path):
                    shutil.rmtree(path)  # Delete directory and contents
                else:
                    os.remove(path)  # Delete file
                tree = self.get_current_tree()
                if tree:
                    index = tree.indexOfTopLevelItem(tree.currentItem())
                    tree.takeTopLevelItem(index)
                self.show_info("Deleted", f"File '{path}' deleted.")
            except Exception as e:
                self.show_critical("Error", str(e))

    def delete_multiple_files(self):
        files = self.get_selected_files()
        if not files:
            return
        reply = self.show_question(
            "🗑️ Delete Multiple Files",
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
            tree = self.get_current_tree()
            if tree:
                for item in tree.selectedItems():
                    index = tree.indexOfTopLevelItem(item)
                    tree.takeTopLevelItem(index)
            if error_files:
                self.show_warning(
                    "⚠️ Deletion Errors",
                    "Some files could not be deleted:\n" + "\n".join(error_files)
                )
            else:
                self.show_info("✅ Success", f"Successfully deleted {len(files)} files.")

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
                "⚠️ Copy Errors",
                f"Copied {success_count} files.\nErrors occurred with:\n" + "\n".join(error_files)
            )
        else:
            self.show_info("✅ Success", f"Successfully copied {success_count} files to {dest}")

    def move_file(self):
        path = self.get_selected_file()
        if not path:
            return
        dest = QFileDialog.getExistingDirectory(self, "Select Destination Directory")
        if dest:
            try:
                shutil.move(path, dest)
                tree = self.get_current_tree()
                if tree:
                    index = tree.indexOfTopLevelItem(tree.currentItem())
                    tree.takeTopLevelItem(index)
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
                tree = self.get_current_tree()
                if tree:
                    for item in tree.selectedItems():
                        if item.text(3) == path:
                            index = tree.indexOfTopLevelItem(item)
                            tree.takeTopLevelItem(index)
            except Exception as e:
                error_files.append(f"{path}: {str(e)}")
        if error_files:
            self.show_warning(
                "⚠️ Move Errors",
                f"Moved {success_count} files.\nErrors occurred with:\n" + "\n".join(error_files)
            )
        else:
            self.show_info("✅ Success", f"Successfully moved {success_count} files to {dest}")

    def rename_file(self):
        path = self.get_selected_file()
        if not path:
            return
        directory = os.path.dirname(path)
        old_name = os.path.basename(path)
        new_name, ok = QInputDialog.getText(self, "✏️ Rename File", f"Enter new name for {old_name}:", QLineEdit.EchoMode.Normal, old_name)
        if ok and new_name:
            new_full_path = os.path.join(directory, new_name)
            try:
                os.rename(path, new_full_path)
                tree = self.get_current_tree()
                if tree:
                    current_item = tree.currentItem()
                    if current_item:
                        # Update display name with emoji
                        _, ext = os.path.splitext(new_name.lower())
                        if os.path.isdir(new_full_path):
                            display_name = f"📁 {new_name}"
                        else:
                            display_name = f"{self.extension_emoji_map.get(ext, '📄')} {new_name}"
                        current_item.setText(0, display_name)
                        current_item.setText(3, new_full_path)
                self.show_info("✅ Success", "File renamed successfully.")
            except Exception as e:
                self.show_critical("Error", f"Could not rename file: {str(e)}")

    def batch_rename_files(self):
        files = self.get_selected_files()
        if not files:
            return
        prefix, ok_prefix = QInputDialog.getText(self, "✏️ Batch Rename", "Enter prefix (optional):")
        if not ok_prefix:
            return
        suffix, ok_suffix = QInputDialog.getText(self, "✏️ Batch Rename", "Enter suffix (optional):")
        if not ok_suffix:
            return

        error_files = []
        success_count = 0
        tree = self.get_current_tree()
        if not tree:
            return
        selected_items = tree.selectedItems()

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
                # Update display name with emoji
                if os.path.isdir(new_full_path):
                    display_name = f"📁 {new_name}"
                else:
                    display_name = f"{self.extension_emoji_map.get(ext.lower(), '📄')} {new_name}"
                item.setText(0, display_name)
                item.setText(3, new_full_path)
            except Exception as e:
                error_files.append(f"{old_path} -> {new_full_path}: {str(e)}")

        if error_files:
            self.show_warning(
                "⚠️ Batch Rename Errors",
                f"Renamed {success_count} files.\nErrors:\n" + "\n".join(error_files)
            )
        else:
            self.show_info("✅ Success", f"Successfully renamed {success_count} files.")

    # ========== Compression functions ==========
    def compress_file(self):
        """Compress a single file to ZIP"""
        path = self.get_selected_file()
        if not path:
            return
        
        # Get default ZIP file name
        base_name = os.path.splitext(os.path.basename(path))[0]
        default_zip_name = f"{base_name}.zip"
        
        # Ask user for ZIP file location and name
        zip_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save ZIP file as...", 
            default_zip_name,
            "ZIP Files (*.zip);;All Files (*)"
        )
        
        if not zip_path:
            return
        
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                if os.path.isfile(path):
                    # Add single file
                    zipf.write(path, os.path.basename(path))
                elif os.path.isdir(path):
                    # Add directory and all its contents
                    for root, dirs, files in os.walk(path):
                        for file in files:
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.dirname(path))
                            zipf.write(file_path, arcname)
            
            # Create callback function for opening in Finder
            def open_zip_in_finder():
                subprocess.run(["open", "-R", zip_path], check=True)
            
            self.show_info_dialog_with_action(
                "🗜️ Single File Compression", 
                f"File compressed to: {zip_path}", 
                "🔍 Open in Finder", 
                open_zip_in_finder
            )
            
        except Exception as e:
            self.show_critical("🗜️ Compression Error", f"Failed to compress file: {str(e)}")

    def compress_multiple_files(self):
        """Compress multiple files to ZIP"""
        files = self.get_selected_files()
        if not files:
            return
        
        # Get default ZIP file name
        default_zip_name = f"compressed_files_{len(files)}_items.zip"
        
        # Ask user for ZIP file location and name
        zip_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save ZIP file as...", 
            default_zip_name,
            "ZIP Files (*.zip);;All Files (*)"
        )
        
        if not zip_path:
            return
        
        try:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for path in files:
                    if os.path.isfile(path):
                        # Add file with just its name (no full path structure)
                        zipf.write(path, os.path.basename(path))
                    elif os.path.isdir(path):
                        # Add directory and all its contents
                        dir_name = os.path.basename(path)
                        for root, dirs, files_in_dir in os.walk(path):
                            for file in files_in_dir:
                                file_path = os.path.join(root, file)
                                # Create archive path that preserves directory structure
                                arcname = os.path.join(dir_name, os.path.relpath(file_path, path))
                                zipf.write(file_path, arcname)
            
            # Create callback function for opening in Finder
            def open_zip_in_finder():
                subprocess.run(["open", "-R", zip_path], check=True)
            
            self.show_info_dialog_with_action(
                "🗜️ Multiple Files Compression", 
                f"{len(files)} items compressed to: {zip_path}", 
                "🔍 Open in Finder", 
                open_zip_in_finder
            )
            
        except Exception as e:
            self.show_critical("🗜️ Compression Error", f"Failed to compress files: {str(e)}")

    # ========== Copy path to clipboard ==========
    def show_tooltip(self, message):
        """Show a beautiful tooltip for copy confirmations"""
        # Update tooltip style based on current theme
        if self.dark_mode:
            self.tooltip.setup_dark_style()
        else:
            self.tooltip.setup_style()
        
        # Show tooltip relative to the tree widget with longer duration
        tree = self.get_current_tree()
        if tree:
            self.tooltip.show_message(message, tree, 2000)
    
    def copy_full_path(self):
        path = self.get_selected_file()
        if not path:
            return
        QApplication.clipboard().setText(path)
        self.show_tooltip("✅ Full path copied!")

    def copy_path_only(self):
        path = self.get_selected_file()
        if not path:
            return
        directory = os.path.dirname(path)
        QApplication.clipboard().setText(directory)
        self.show_tooltip("✅ Directory path copied!")

    def copy_file_name_only(self):
        path = self.get_selected_file()
        if not path:
            return
        filename = os.path.basename(path)
        QApplication.clipboard().setText(filename)
        self.show_tooltip("✅ File name copied!")

    # ========== Export to CSV ==========
    def export_to_csv(self):
        search_tab = self.get_current_tab()
        if not search_tab or not search_tab.file_data:
            self.show_warning("⚠️ Warning", "No data to export.")
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Export to CSV", "", "CSV Files (*.csv);;All Files (*)")
        if not file_path:
            return
        try:
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Name', 'Size', 'Modification Time', 'Path'])
                for item in search_tab.file_data:
                    writer.writerow(item)
            self.show_info("✅ Success", f"Results exported to {file_path}")
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
    

    
    def update_tab_close_button(self, index):
        """Update close button appearance for a specific tab"""
        # Get the tab bar
        tab_bar = self.tab_widget.tabBar()
        
        # Get the close button for this tab
        close_button = tab_bar.tabButton(index, tab_bar.ButtonPosition.RightSide)
        if close_button:
            # Set a tooltip
            close_button.setToolTip("Close tab")
            
            # Force the button to show "×" (multiplication sign) for better visibility
            close_button.setText("×")
            
            # No need to set individual styles - they are handled by the main stylesheet
    
    def update_all_tab_close_buttons(self):
        """Update all tab close buttons to show clear X"""
        for i in range(self.tab_widget.count()):
            self.update_tab_close_button(i)
    
    def calculate_tab_width(self):
        """Calculate optimal tab width based on number of tabs"""
        tab_count = self.tab_widget.count()
        if tab_count == 0:
            return min(240, self.tab_width)  # Default to reasonable width
        
        # Get the tab bar width
        tab_bar = self.tab_widget.tabBar()
        available_width = tab_bar.width()
        
        # If tab bar width is not available yet, use window width
        if available_width <= 0:
            available_width = self.width() - 100
        
        # Reserve space for scroll buttons and some margin
        available_width = available_width - 80
        
        # Define min and max tab widths
        min_tab_width = 80
        max_tab_width = 240
        
        # Calculate optimal width
        optimal_width = available_width // tab_count
        
        # Clamp to min/max values
        if optimal_width < min_tab_width:
            return min_tab_width
        elif optimal_width > max_tab_width:
            return max_tab_width
        else:
            return optimal_width
    
    def update_tab_style(self):
        """Update tab widget style based on current theme"""
        # Calculate dynamic tab width
        dynamic_tab_width = self.calculate_tab_width()
        if self.dark_mode:
            # Dark mode style with blue indicator for selected tab
            self.tab_widget.setStyleSheet(f"""
                QTabWidget::pane {{
                    border: 1px solid #555555;
                    background: #2b2b2b;
                }}
                QTabBar {{
                    alignment: left;
                }}
                QTabBar::tab {{
                    background: #3c3f41;
                    border: 1px solid #555555;
                    border-bottom: none;
                    border-top: 2px solid transparent;
                    padding: 6px 12px 8px 12px;
                    margin-right: 2px;
                    min-width: {dynamic_tab_width}px;
                    max-width: {dynamic_tab_width}px;
                    color: #f0f0f0;
                }}
                QTabBar::tab:selected {{
                    background: #2b2b2b;
                    border-color: #555555;
                    border-top: 2px solid #007acc;
                }}
                QTabBar::tab:hover {{
                    background: #4a4a4a;
                    border-top: 2px solid #4a9eff;
                }}
                QTabBar::tab:hover:selected {{
                    border-top: 2px solid #007acc;
                }}
            """)
        else:
            # Light mode style with blue indicator for selected tab
            self.tab_widget.setStyleSheet(f"""
                QTabWidget::pane {{
                    border: 1px solid #cccccc;
                    background: white;
                }}
                QTabBar {{
                    alignment: left;
                }}
                QTabBar::tab {{
                    background: #f0f0f0;
                    border: 1px solid #cccccc;
                    border-bottom: none;
                    border-top: 3px solid transparent;
                    padding: 6px 12px 8px 12px;
                    margin-right: 2px;
                    min-width: {dynamic_tab_width}px;
                    max-width: {dynamic_tab_width}px;
                    color: #000000;
                }}
                QTabBar::tab:selected {{
                    background: white;
                    border-color: #cccccc;
                    border-top: 3px solid #007acc;
                }}
                QTabBar::tab:hover {{
                    background: #e0e0e0;
                    border-top: 3px solid #4a9eff;
                }}
                QTabBar::tab:hover:selected {{
                    border-top: 3px solid #007acc;
                }}
            """)
        
        # Update all existing tab close buttons to show clear "X"
        self.update_all_tab_close_buttons()
    
    def set_non_dark_mode(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #ffffff;
                color: #24292f;
                font-family: "Segoe UI", "SF Pro Display", system-ui, sans-serif;
                font-size: 13px;
            }
            QWidget {
                background-color: #ffffff;
                color: #24292f;
            }
            QLabel, QCheckBox {
                color: #24292f;
                background: transparent;
                font-size: 13px;
                font-weight: 400;
            }
            QGroupBox {
                color: #24292f;
                border: 1px solid #d1d9e0;
                border-radius: 8px;
                margin: 12px 0px;
                padding-top: 16px;
                font-weight: 600;
                background-color: rgba(0, 0, 0, 0.02);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                background: #ffffff;
                color: #24292f;
            }
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2ea043, stop: 1 #238636);
                border: 1px solid #1a7f37;
                border-radius: 6px;
                padding: 10px 18px;
                color: white;
                font-weight: 600;
                min-height: 22px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2c974b, stop: 1 #1f883d);
                border-color: #1a7f37;
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #238636, stop: 1 #196c2e);
            }
            QPushButton:disabled {
                background-color: #f6f8fa;
                color: #8c959f;
                border-color: #d1d9e0;
            }
            QLineEdit {
                border: 2px solid #d1d9e0;
                padding: 8px 12px;
                border-radius: 6px;
                background-color: #ffffff;
                color: #24292f;
                selection-background-color: #0969da;
                font-size: 13px;
                min-height: 18px;
            }
            QLineEdit:focus {
                border: 2px solid #0969da;
                background-color: #ffffff;
            }
            QLineEdit:hover {
                border-color: #8c959f;
            }
            QPlainTextEdit {
                background-color: #f6f8fa;
                color: #24292f;
                border: 1px solid #d1d9e0;
                border-radius: 6px;
                selection-background-color: #0969da;
                padding: 8px;
                font-family: "Cascadia Code", "Fira Code", "Consolas", monospace;
                line-height: 1.4;
            }
            QTreeWidget {
                background-color: #ffffff;
                color: #24292f;
                border: 1px solid #d1d9e0;
                outline: 0;
                selection-background-color: #dbeafe;
                alternate-background-color: #f6f8fa;
                border-radius: 6px;
                gridline-color: #eaeef2;
            }
            QTreeWidget::item {
                padding: 6px 8px;
                border: none;
                border-bottom: 1px solid rgba(0, 0, 0, 0.05);
            }
            QTreeWidget::item:hover {
                background-color: #f6f8fa;
            }
            QTreeWidget::item:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #dbeafe, stop: 1 #bfdbfe);
                color: #1e40af;
                border-radius: 3px;
            }
            QHeaderView::section {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f6f8fa, stop: 1 #eaeef2);
                color: #24292f;
                border: none;
                border-right: 1px solid #d1d9e0;
                padding: 8px 12px;
                font-weight: 600;
                font-size: 12px;
            }
            QHeaderView::section:hover {
                background-color: #eaeef2;
            }
            QSplitter::handle {
                background-color: #eaeef2;
                margin: 2px;
                border-radius: 2px;
            }
            QSplitter::handle:hover {
                background-color: #0969da;
            }
            QSplitter::handle:horizontal {
                width: 6px;
            }
            QSplitter::handle:vertical {
                height: 6px;
            }
            QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 6px;
                padding: 8px;
                color: #24292f;
                min-width: 20px;
                min-height: 20px;
            }
            QToolButton:hover {
                background-color: rgba(0, 0, 0, 0.1);
                border-color: #d1d9e0;
            }
            QToolButton:pressed {
                background-color: #dbeafe;
            }
            QSlider::groove:horizontal {
                border: none;
                height: 6px;
                background-color: #d1d9e0;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #0969da, stop: 1 #0550ae);
                border: 1px solid #0969da;
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #1f7bd3, stop: 1 #1366d9);
            }
            QSlider::add-page:horizontal {
                background-color: #d1d9e0;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #0969da, stop: 1 #0550ae);
                border-radius: 3px;
            }
            QProgressBar {
                background-color: #d1d9e0;
                border: none;
                border-radius: 4px;
                text-align: center;
                color: #24292f;
                height: 10px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #0969da, stop: 1 #0550ae);
                border-radius: 4px;
            }
            QMenuBar {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #f6f8fa, stop: 1 #eaeef2);
                color: #24292f;
                border-bottom: 1px solid #d1d9e0;
                padding: 2px;
            }
            QMenuBar::item {
                background: transparent;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: rgba(0, 0, 0, 0.1);
            }
            QMenu {
                background-color: #ffffff;
                color: #24292f;
                border: 1px solid #d1d9e0;
                border-radius: 6px;
                padding: 4px 0;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 4px;
                margin: 2px 6px;
            }
            QMenu::item:selected {
                background-color: #dbeafe;
            }
            QMenu::separator {
                height: 1px;
                background-color: #d1d9e0;
                margin: 4px 8px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #d1d9e0;
                border-radius: 3px;
                background-color: #ffffff;
            }
            QCheckBox::indicator:hover {
                border-color: #0969da;
            }
            QCheckBox::indicator:checked {
                background-color: #0969da;
                border-color: #0969da;
            }
            #queryLabel, #directoryLabel {
                font-weight: 600;
                color: #24292f;
                padding: 4px 0;
            }
            #itemsFoundLabel {
                color: #656d76;
                font-size: 12px;
                font-weight: 500;
                padding: 4px 8px;
                background-color: rgba(0, 0, 0, 0.05);
                border-radius: 4px;
            }
            #previewTitle {
                font-size: 16px;
                font-weight: 700;
                color: #24292f;
                padding: 8px 0;
                border-bottom: 2px solid #0969da;
                margin-bottom: 8px;
            }
            #leftContainer {
                background-color: #ffffff;
                border-right: 1px solid #d1d9e0;
            }
            #previewContainer {
                background-color: #f6f8fa;
                border-left: 1px solid #d1d9e0;
            }
            #mainSplitter {
                background-color: #ffffff;
            }
            #mainSplitter::handle {
                background-color: #f6f8fa;
                border: 1px solid #d1d9e0;
                margin: 4px;
                border-radius: 3px;
            }
            #mainSplitter::handle:hover {
                background-color: #0969da;
            }
            #mainSplitter::handle:horizontal {
                width: 8px;
            }
            QListView {
                background-color: #ffffff;
                color: #24292f;
                border: 1px solid #d1d9e0;
                border-radius: 6px;
                padding: 4px;
                selection-background-color: #dbeafe;
                outline: 0;
            }
            QListView::item {
                padding: 8px 12px;
                border: none;
                border-radius: 4px;
                margin: 2px;
            }
            QListView::item:hover {
                background-color: #f6f8fa;
            }
            QListView::item:selected {
                background-color: #dbeafe;
                color: #1e40af;
            }
            QScrollBar:vertical {
                background-color: #f6f8fa;
                width: 14px;
                margin: 0;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background-color: #d1d9e0;
                border-radius: 7px;
                min-height: 20px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #8c959f;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                background-color: #f6f8fa;
                height: 14px;
                margin: 0;
                border-radius: 7px;
            }
            QScrollBar::handle:horizontal {
                background-color: #d1d9e0;
                border-radius: 7px;
                min-width: 20px;
                margin: 2px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #8c959f;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            QToolTip {
                background-color: #ffffff;
                color: #24292f;
                border: 1px solid #d1d9e0;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 12px;
            }
            #previewPopoutButton {
                background-color: rgba(0, 0, 0, 0.05);
                border: 1px solid #d1d9e0;
                border-radius: 4px;
                color: #24292f;
                font-size: 14px;
                font-weight: bold;
            }
            #previewPopoutButton:hover {
                background-color: #0969da;
                border-color: #0969da;
                color: white;
            }
            #previewPopoutButton:pressed {
                background-color: #0550ae;
            }
            #previewCloseButton {
                background-color: rgba(0, 0, 0, 0.05);
                border: 1px solid #d1d9e0;
                border-radius: 4px;
                color: #24292f;
                font-size: 14px;
                font-weight: bold;
            }
            #previewCloseButton:hover {
                background-color: #d73a49;
                border-color: #d73a49;
                color: white;
            }
            #previewCloseButton:pressed {
                background-color: #b31d28;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
                background: white;
            }
            QTabBar {
                alignment: left;
            }
            QTabBar::tab {
                background: #f0f0f0;
                border: 1px solid #cccccc;
                border-bottom: none;
                border-top: 3px solid transparent;
                padding: 6px 12px 8px 12px;
                margin-right: 2px;
                min-width: 120px;
                max-width: 200px;
                color: #000000;
            }
            QTabBar::tab:selected {
                background: white;
                border-color: #cccccc;
                border-top: 3px solid #007acc;
            }
            QTabBar::tab:hover {
                background: #e0e0e0;
                border-top: 3px solid #4a9eff;
            }
            QTabBar::tab:hover:selected {
                border-top: 3px solid #007acc;
            }
            QTabBar QToolButton {
                background: rgba(0, 0, 0, 0.1);
                border: 1px solid #d1d9e0;
                border-radius: 4px;
                color: #24292f;
                font-size: 16px;
                font-weight: bold;
                min-width: 18px;
                min-height: 18px;
                max-width: 18px;
                max-height: 18px;
                margin: 2px;
            }
            QTabBar QToolButton:hover {
                background: rgba(220, 53, 69, 0.2);
                color: #dc3545;
                border: 1px solid #dc3545;
            }
            QTabBar QToolButton:pressed {
                background: rgba(220, 53, 69, 0.3);
                color: #dc3545;
            }
        """)
        
        # Update tab widget style and close buttons if tab_widget exists
        if hasattr(self, 'tab_widget'):
            self.update_tab_style()
    
    def set_dark_mode(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #181818;
                color: #d4d4d4;
                font-family: "Segoe UI", "SF Pro Display", system-ui, sans-serif;
                font-size: 13px;
            }
            QWidget {
                background-color: #181818;
                color: #d4d4d4;
            }
            QLabel, QCheckBox {
                color: #d4d4d4;
                background: transparent;
                font-size: 13px;
                font-weight: 400;
            }
            QGroupBox {
                color: #e1e4e8;
                border: 1px solid #404040;
                border-radius: 8px;
                margin: 12px 0px;
                padding-top: 16px;
                font-weight: 600;
                background-color: rgba(255, 255, 255, 0.02);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 12px;
                padding: 0 8px 0 8px;
                background: #181818;
                color: #e1e4e8;
            }
            QPushButton {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #0e4775, stop: 1 #0a3d66);
                border: 1px solid #1177bb;
                border-radius: 6px;
                padding: 10px 18px;
                color: white;
                font-weight: 600;
                min-height: 22px;
                font-size: 13px;
            }
            QPushButton:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #1177bb, stop: 1 #0e639c);
                border-color: #2196f3;
            }
            QPushButton:pressed {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #083d5c, stop: 1 #062d43);
            }
            QPushButton:disabled {
                background-color: #404040;
                color: #858585;
                border-color: #5a5a5a;
            }
            QLineEdit {
                border: 2px solid #404040;
                padding: 8px 12px;
                border-radius: 6px;
                background-color: #252526;
                color: #d4d4d4;
                selection-background-color: #264f78;
                font-size: 13px;
                min-height: 18px;
            }
            QLineEdit:focus {
                border: 2px solid #007fd4;
                background-color: #1e1e1e;
            }
            QLineEdit:hover {
                border-color: #505050;
            }
            QPlainTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #404040;
                border-radius: 6px;
                selection-background-color: #264f78;
                padding: 8px;
                font-family: "Cascadia Code", "Fira Code", "Consolas", monospace;
                line-height: 1.4;
            }
            QTreeWidget {
                background-color: #252526;
                color: #d4d4d4;
                border: 1px solid #404040;
                outline: 0;
                selection-background-color: #264f78;
                alternate-background-color: #2a2d2e;
                border-radius: 6px;
                gridline-color: #404040;
            }
            QTreeWidget::item {
                padding: 6px 8px;
                border: none;
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            }
            QTreeWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.08);
            }
            QTreeWidget::item:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #264f78, stop: 1 #1e3a5f);
                color: white;
                border-radius: 3px;
            }
            QHeaderView::section {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #3c3c3c, stop: 1 #323233);
                color: #e1e4e8;
                border: none;
                border-right: 1px solid #404040;
                padding: 8px 12px;
                font-weight: 600;
                font-size: 12px;
            }
            QHeaderView::section:hover {
                background-color: #404040;
            }
            QSplitter::handle {
                background-color: #323233;
                margin: 2px;
                border-radius: 2px;
            }
            QSplitter::handle:hover {
                background-color: #007fd4;
            }
            QSplitter::handle:horizontal {
                width: 6px;
            }
            QSplitter::handle:vertical {
                height: 6px;
            }
            QToolButton {
                background-color: transparent;
                border: 1px solid transparent;
                border-radius: 6px;
                padding: 8px;
                color: #d4d4d4;
                min-width: 20px;
                min-height: 20px;
            }
            QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
                border-color: #505050;
            }
            QToolButton:pressed {
                background-color: #264f78;
            }
            QSlider::groove:horizontal {
                border: none;
                height: 6px;
                background-color: #404040;
                border-radius: 3px;
            }
            QSlider::handle:horizontal {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #007fd4, stop: 1 #005a9e);
                border: 1px solid #007fd4;
                width: 18px;
                margin: -6px 0;
                border-radius: 9px;
            }
            QSlider::handle:horizontal:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #2196f3, stop: 1 #1976d2);
            }
            QSlider::add-page:horizontal {
                background-color: #404040;
                border-radius: 3px;
            }
            QSlider::sub-page:horizontal {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #007fd4, stop: 1 #005a9e);
                border-radius: 3px;
            }
            QProgressBar {
                background-color: #404040;
                border: none;
                border-radius: 4px;
                text-align: center;
                color: #d4d4d4;
                height: 10px;
            }
            QProgressBar::chunk {
                background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #007fd4, stop: 1 #005a9e);
                border-radius: 4px;
            }
            QMenuBar {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #323233, stop: 1 #2d2d30);
                color: #d4d4d4;
                border-bottom: 1px solid #404040;
                padding: 2px;
            }
            QMenuBar::item {
                background: transparent;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QMenuBar::item:selected {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QMenu {
                background-color: #2d2d30;
                color: #d4d4d4;
                border: 1px solid #404040;
                border-radius: 6px;
                padding: 4px 0;
            }
            QMenu::item {
                padding: 8px 20px;
                border-radius: 4px;
                margin: 2px 6px;
            }
            QMenu::item:selected {
                background-color: #264f78;
            }
            QMenu::separator {
                height: 1px;
                background-color: #404040;
                margin: 4px 8px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 2px solid #404040;
                border-radius: 3px;
                background-color: #252526;
            }
            QCheckBox::indicator:hover {
                border-color: #007fd4;
            }
            QCheckBox::indicator:checked {
                background-color: #007fd4;
                border-color: #007fd4;
            }
            #queryLabel, #directoryLabel {
                font-weight: 600;
                color: #e1e4e8;
                padding: 4px 0;
            }
            #itemsFoundLabel {
                color: #8b949e;
                font-size: 12px;
                font-weight: 500;
                padding: 4px 8px;
                background-color: rgba(255, 255, 255, 0.05);
                border-radius: 4px;
            }
            #previewTitle {
                font-size: 16px;
                font-weight: 700;
                color: #e1e4e8;
                padding: 8px 0;
                border-bottom: 2px solid #007fd4;
                margin-bottom: 8px;
            }
            #leftContainer {
                background-color: #181818;
                border-right: 1px solid #323233;
            }
            #previewContainer {
                background-color: #1e1e1e;
                border-left: 1px solid #323233;
            }
            #mainSplitter {
                background-color: #181818;
            }
            #mainSplitter::handle {
                background-color: #323233;
                border: 1px solid #404040;
                margin: 4px;
                border-radius: 3px;
            }
            #mainSplitter::handle:hover {
                background-color: #007fd4;
            }
            #mainSplitter::handle:horizontal {
                width: 8px;
            }
            QListView {
                background-color: #2d2d30;
                color: #d4d4d4;
                border: 1px solid #404040;
                border-radius: 6px;
                padding: 4px;
                selection-background-color: #264f78;
                outline: 0;
            }
            QListView::item {
                padding: 8px 12px;
                border: none;
                border-radius: 4px;
                margin: 2px;
            }
            QListView::item:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QListView::item:selected {
                background-color: #264f78;
                color: white;
            }
            QScrollBar:vertical {
                background-color: #2d2d30;
                width: 14px;
                margin: 0;
                border-radius: 7px;
            }
            QScrollBar::handle:vertical {
                background-color: #555555;
                border-radius: 7px;
                min-height: 20px;
                margin: 2px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #666666;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
            }
            QScrollBar:horizontal {
                background-color: #2d2d30;
                height: 14px;
                margin: 0;
                border-radius: 7px;
            }
            QScrollBar::handle:horizontal {
                background-color: #555555;
                border-radius: 7px;
                min-width: 20px;
                margin: 2px;
            }
            QScrollBar::handle:horizontal:hover {
                background-color: #666666;
            }
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
            }
            QToolTip {
                background-color: #2d2d30;
                color: #d4d4d4;
                border: 1px solid #404040;
                border-radius: 4px;
                padding: 6px 8px;
                font-size: 12px;
            }
            #previewPopoutButton {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid #404040;
                border-radius: 4px;
                color: #d4d4d4;
                font-size: 14px;
                font-weight: bold;
            }
            #previewPopoutButton:hover {
                background-color: #007fd4;
                border-color: #007fd4;
                color: white;
            }
            #previewPopoutButton:pressed {
                background-color: #005a9e;
            }
            #previewCloseButton {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid #404040;
                border-radius: 4px;
                color: #d4d4d4;
                font-size: 14px;
                font-weight: bold;
            }
            #previewCloseButton:hover {
                background-color: #e81123;
                border-color: #e81123;
                color: white;
            }
            #previewCloseButton:pressed {
                background-color: #c50e1f;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background: #2b2b2b;
            }
            QTabBar {
                alignment: left;
            }
            QTabBar::tab {
                background: #3c3f41;
                border: 1px solid #555555;
                border-bottom: none;
                border-top: 2px solid transparent;
                padding: 6px 12px 8px 12px;
                margin-right: 2px;
                min-width: 120px;
                max-width: 200px;
                color: #f0f0f0;
            }
            QTabBar::tab:selected {
                background: #2b2b2b;
                border-color: #555555;
                border-top: 2px solid #007acc;
            }
            QTabBar::tab:hover {
                background: #4a4a4a;
                border-top: 2px solid #4a9eff;
            }
            QTabBar::tab:hover:selected {
                border-top: 2px solid #007acc;
            }
            QTabBar QToolButton {
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid #555555;
                border-radius: 4px;
                color: #cccccc;
                font-size: 16px;
                font-weight: bold;
                min-width: 18px;
                min-height: 18px;
                max-width: 18px;
                max-height: 18px;
                margin: 2px;
            }
            QTabBar QToolButton:hover {
                background: rgba(220, 53, 69, 0.2);
                color: #ff6b6b;
                border: 1px solid #ff6b6b;
            }
            QTabBar QToolButton:pressed {
                background: rgba(220, 53, 69, 0.3);
                color: #ff6b6b;
            }
        """)
        
        # Update tab widget style and close buttons if tab_widget exists
        if hasattr(self, 'tab_widget'):
            self.update_tab_style()

    def toggle_dark_mode(self, checked):
        self.dark_mode = checked
        if checked:
            self.set_dark_mode()
        else:
            self.set_non_dark_mode()
            
        # Update tab widget style (for dynamic width calculation)
        self.update_tab_style()
            
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
<p><b>Version:</b> 1.3.5</p>
<p><b>Author:</b> Apple Dragon</p>
"""
        QMessageBox.about(self, "About Everything by mdfind", about_text)

    def clear_history(self):
        reply = self.show_question(
            "🧹 Clear History",
            "Are you sure you want to clear your search history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.query_history = []
            cfg = read_config()
            cfg["query_history"] = self.query_history
            write_config(cfg)
            self.query_completer.model().setStringList(self.query_history)
            self.show_info("🧹 History Cleared", "Search history cleared.")

    def apply_dialog_dark_mode(self, dialog):
        """Apply modern styling to dialog boxes based on current theme"""
        if self.dark_mode:
            dialog.setStyleSheet("""
                QDialog, QMessageBox {
                    background-color: #2d2d30;
                    color: #d4d4d4;
                    border: 1px solid #404040;
                    border-radius: 8px;
                }
                QLabel {
                    color: #d4d4d4;
                    font-size: 13px;
                    padding: 8px;
                }
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #0e4775, stop: 1 #0a3d66);
                    border: 1px solid #1177bb;
                    border-radius: 6px;
                    padding: 10px 20px;
                    color: white;
                    font-weight: 600;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #1177bb, stop: 1 #0e639c);
                    border-color: #2196f3;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #083d5c, stop: 1 #062d43);
                }
            """)
        else:
            dialog.setStyleSheet("""
                QDialog, QMessageBox {
                    background-color: #ffffff;
                    color: #24292f;
                    border: 1px solid #d1d9e0;
                    border-radius: 8px;
                }
                QLabel {
                    color: #24292f;
                    font-size: 13px;
                    padding: 8px;
                }
                QPushButton {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #2ea043, stop: 1 #238636);
                    border: 1px solid #1a7f37;
                    border-radius: 6px;
                    padding: 10px 20px;
                    color: white;
                    font-weight: 600;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #2c974b, stop: 1 #1f883d);
                    border-color: #1a7f37;
                }
                QPushButton:pressed {
                    background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                        stop: 0 #238636, stop: 1 #196c2e);
                }
            """)

    def show_info_dialog_with_action(self, title, message, action_button_text="Action", action_callback=None):
        """Show a custom dialog with OK and an optional action button"""
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setText(message)
        
        # Add custom buttons
        ok_button = msg.addButton("OK", QMessageBox.ButtonRole.AcceptRole)
        action_button = None
        
        if action_callback is not None:
            action_button = msg.addButton(action_button_text, QMessageBox.ButtonRole.ActionRole)
        
        # Apply dark mode styling
        self.apply_dialog_dark_mode(msg)
        
        # Execute dialog and handle response
        msg.exec()
        
        # Check which button was clicked and execute callback if provided
        if action_button and msg.clickedButton() == action_button and action_callback:
            try:
                action_callback()
            except Exception as e:
                self.show_critical("Error", f"Action failed: {str(e)}")

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

    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        # Update tab widths when window is resized
        if hasattr(self, 'tab_widget') and self.tab_widget.count() > 0:
            self.update_tab_style()
    
    def closeEvent(self, event):
        # Clean up all tabs to prevent crashes
        for index in list(self.search_tabs.keys()):
            self.close_tab(index)
        
        # Stop media player
        if hasattr(self, 'player_manager'):
            self.player_manager.stop()
        
        config = read_config()
        config["window_size"] = {"width": self.width(), "height": self.height()}
        write_config(config)
        super().closeEvent(event)
    
    # === Updated bookmark methods ===
    def bookmark_large_files(self):
        clause = 'kMDItemFSSize >= 52428800'
        self.start_search(extra_clause=clause, is_bookmark=True, tab_title="Large Files")

    def bookmark_videos(self):
        clause = 'kMDItemContentTypeTree = "public.movie"'
        self.start_search(extra_clause=clause, is_bookmark=True, tab_title="Video Files")

    def bookmark_audio(self):
        clause = 'kMDItemContentTypeTree = "public.audio"'
        self.start_search(extra_clause=clause, is_bookmark=True, tab_title="Audio Files")

    def bookmark_images(self):
        clause = 'kMDItemContentTypeTree = "public.image"'
        self.start_search(extra_clause=clause, is_bookmark=True, tab_title="Images")

    def bookmark_archives(self):
        clause = 'kMDItemContentTypeTree = "public.archive"'
        self.start_search(extra_clause=clause, is_bookmark=True, tab_title="Archives")

    def bookmark_applications(self):
        clause = 'kMDItemContentType == "com.apple.application-bundle"'
        self.start_search(extra_clause=clause, is_bookmark=True, tab_title="Applications")

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
        tree = self.get_current_tree()
        if not tree:
            return
            
        item_count = tree.topLevelItemCount()
        if item_count == 0:
            return

        # Find the currently selected item
        current_index = -1
        selected_items = tree.selectedItems()
        if selected_items:
            current_item = selected_items[0]
            for i in range(item_count):
                if tree.topLevelItem(i) == current_item:
                    current_index = i
                    break

        # Find the next media file
        next_index = current_index + 1
        while next_index < item_count:
            next_item = tree.topLevelItem(next_index)
            path = next_item.text(3)
            _, ext = os.path.splitext(path)
            ext = ext.lower()
            
            if ext in self.video_extensions or ext in self.audio_extensions:
                # Select the item in the tree
                tree.setCurrentItem(next_item)
                tree.scrollToItem(next_item)
                
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
            
        tree = self.get_current_tree()
        if not tree:
            return
            
        selected_items = tree.selectedItems()
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
        tree = self.get_current_tree()
        if tree:
            selected_items = tree.selectedItems()
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
        tree = self.get_current_tree()
        if not tree:
            return
            
        item_count = tree.topLevelItemCount()
        if item_count == 0:
            return

        # Find the currently selected item
        current_index = -1
        selected_items = tree.selectedItems()
        if selected_items:
            current_item = selected_items[0]
            for i in range(item_count):
                if tree.topLevelItem(i) == current_item:
                    current_index = i
                    break

        # Find the next media file
        next_index = current_index + 1
        while next_index < item_count:
            next_item = tree.topLevelItem(next_index)
            path = next_item.text(3)
            _, ext = os.path.splitext(path)
            ext = ext.lower()
            
            if ext in self.video_extensions or ext in self.audio_extensions:
                # Select the item in the tree
                tree.setCurrentItem(next_item)
                tree.scrollToItem(next_item)
                
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
    
    def update_video_info(self):
        """Update the media info panel with video metadata"""
        if not hasattr(self.media_player, 'videoSink') or not self.media_player.videoSink():
            return
            
        size = self.media_player.videoSink().videoSize()
        duration_secs = self.media_player.duration() // 1000
        
        # Skip if resolution is invalid
        if size.width() <= 0 or size.height() <= 0:
            return
            
        self.media_info.appendPlainText(
            f"\nResolution: {size.width()} x {size.height()}\n"
            f"Duration: {duration_secs} seconds"
        )

    def on_search_enter(self):
        """Handle Enter key press in the search query field"""
        query = self.edit_query.text().strip()
        if query:  # Only search if the query isn't just whitespace
            # Cancel any pending search timer
            self.search_timer.stop()
            # Execute search immediately
            self.start_search()
            
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
