#!/usr/bin/env python3
"""
Additional feature demonstration script for Everything by mdfind
This creates screenshots of more advanced features and UI interactions
"""

import sys
import os
import time
from screenshot_demo import DemoMdfindApp
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QPixmap, QPainter, QFont, QColor

class AdvancedDemoApp(DemoMdfindApp):
    def __init__(self):
        super().__init__()
        self.screenshot_count = 0
        
    def demo_context_menu(self):
        """Demonstrate context menu functionality"""
        # Simulate selecting an item and showing context menu
        if self.tree.topLevelItemCount() > 0:
            item = self.tree.topLevelItem(0)
            self.tree.setCurrentItem(item)
            
            # Take screenshot of the interface with selected item
            pixmap = self.grab()
            pixmap.save(f"/home/runner/work/everythingByMdfind/everythingByMdfind/screenshot_selection.png")
            print("Screenshot saved: File selection")
            
    def demo_search_options(self):
        """Demonstrate search options"""
        # Enable different search options
        self.match_case.setChecked(True)
        self.full_match.setChecked(True)
        self.dir_input.setText("/home/user/Documents")
        self.query_input.setText("report")
        
        # Take screenshot
        QTimer.singleShot(1000, lambda: self.save_search_options_screenshot())
        
    def save_search_options_screenshot(self):
        """Save search options screenshot"""
        pixmap = self.grab()
        pixmap.save("/home/runner/work/everythingByMdfind/everythingByMdfind/screenshot_search_options.png")
        print("Screenshot saved: Advanced search options")
        
        # Demo tabs
        QTimer.singleShot(500, lambda: self.demo_tabs())
        
    def demo_tabs(self):
        """Demonstrate tabbed interface"""
        # Create additional tabs
        self.create_new_tab("Video Search")
        self.create_new_tab("Document Search")
        
        # Take screenshot
        pixmap = self.grab()
        pixmap.save("/home/runner/work/everythingByMdfind/everythingByMdfind/screenshot_tabs.png")
        print("Screenshot saved: Multiple tabs")
        
        # Demo preview toggle
        QTimer.singleShot(500, lambda: self.demo_preview_toggle())
        
    def demo_preview_toggle(self):
        """Demonstrate preview panel toggle"""
        # Hide preview panel
        self.toggle_preview()
        
        # Take screenshot
        pixmap = self.grab()
        pixmap.save("/home/runner/work/everythingByMdfind/everythingByMdfind/screenshot_no_preview.png")
        print("Screenshot saved: Interface without preview panel")
        
        # Show preview again
        self.toggle_preview()
        
        # Demo file type searches
        QTimer.singleShot(500, lambda: self.demo_file_type_searches())
        
    def demo_file_type_searches(self):
        """Demonstrate different file type searches"""
        # Search for video files
        self.quick_search("kMDItemContentType == 'public.movie'")
        
        QTimer.singleShot(1500, lambda: self.save_video_search_screenshot())
        
    def save_video_search_screenshot(self):
        """Save video search screenshot"""
        pixmap = self.grab()
        pixmap.save("/home/runner/work/everythingByMdfind/everythingByMdfind/screenshot_video_search.png")
        print("Screenshot saved: Video file search")
        
        # Search for audio files
        self.quick_search("kMDItemContentType == 'public.audio'")
        
        QTimer.singleShot(1500, lambda: self.save_audio_search_screenshot())
        
    def save_audio_search_screenshot(self):
        """Save audio search screenshot"""
        pixmap = self.grab()
        pixmap.save("/home/runner/work/everythingByMdfind/everythingByMdfind/screenshot_audio_search.png")
        print("Screenshot saved: Audio file search")
        
        # Demo preview with file selection
        QTimer.singleShot(500, lambda: self.demo_file_preview())
        
    def demo_file_preview(self):
        """Demonstrate file preview functionality"""
        # Select first item if available
        if self.tree.topLevelItemCount() > 0:
            item = self.tree.topLevelItem(0)
            self.tree.setCurrentItem(item)
            
            # Wait for preview to update
            QTimer.singleShot(500, lambda: self.save_preview_screenshot())
        else:
            self.finish_demo()
            
    def save_preview_screenshot(self):
        """Save preview screenshot"""
        pixmap = self.grab()
        pixmap.save("/home/runner/work/everythingByMdfind/everythingByMdfind/screenshot_preview.png")
        print("Screenshot saved: File preview")
        
        # Finish demo
        QTimer.singleShot(500, lambda: self.finish_demo())
        
    def finish_demo(self):
        """Finish the demonstration"""
        print("All screenshots completed!")
        print("Generated screenshots:")
        print("- screenshot_selection.png: File selection")
        print("- screenshot_search_options.png: Advanced search options")
        print("- screenshot_tabs.png: Multiple tabs interface")
        print("- screenshot_no_preview.png: Interface without preview")
        print("- screenshot_video_search.png: Video file search")
        print("- screenshot_audio_search.png: Audio file search")
        print("- screenshot_preview.png: File preview functionality")
        
        QTimer.singleShot(1000, lambda: QApplication.quit())

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Everything by mdfind - Advanced Demo")
    
    window = AdvancedDemoApp()
    window.show()
    
    # Start the advanced demo sequence after window is shown
    QTimer.singleShot(3000, lambda: window.demo_context_menu())
    QTimer.singleShot(4000, lambda: window.demo_search_options())
    
    return app.exec()

if __name__ == "__main__":
    sys.exit(main())