import sys
import os
import subprocess
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QFileDialog, QMessageBox, QListWidget, QHBoxLayout, QInputDialog,
    QSystemTrayIcon, QMenu 
)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QTimer

class FileMoverGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Super Staging Config")
        self.setWindowIcon(QIcon("super.ico"))
        self.resize(550, 660)
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        x = (screen_geometry.width() - 500) // 2
        y = (screen_geometry.height() - 500) // 2
        self.move(x, y)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        self.layout = QVBoxLayout()

        self.source_dir_label = QLabel("Super Staging Path: Not Set")
        self.flat_dir_label = QLabel("Staging Path: Not Set")
        self.dated_dir_label = QLabel("PDF Archive Path: Not Set")
        self.layout.addWidget(self.source_dir_label)
        self.layout.addWidget(self.flat_dir_label)
        self.layout.addWidget(self.dated_dir_label)

        self.set_source_button = QPushButton("Set Super Staging Path")
        self.set_flat_button = QPushButton("Set Staging Path")
        self.set_dated_button = QPushButton("Set PDF Archive Path")
        self.layout.addWidget(self.set_source_button)
        self.layout.addWidget(self.set_flat_button)
        self.layout.addWidget(self.set_dated_button)

        self.move_times_label = QLabel("Move Times:")
        self.move_times_list = QListWidget()
        self.add_time_button = QPushButton("Add Move Time")
        self.remove_time_button = QPushButton("Remove Selected Time")
        self.layout.addWidget(self.move_times_label)
        self.layout.addWidget(self.move_times_list)

        time_buttons_layout = QHBoxLayout()
        time_buttons_layout.addWidget(self.add_time_button)
        time_buttons_layout.addWidget(self.remove_time_button)
        self.layout.addLayout(time_buttons_layout)

        self.save_button = QPushButton("Save and Start Daemon")
        self.layout.addWidget(self.save_button)
        self.setLayout(self.layout)

        # Connect buttons 
        self.set_source_button.clicked.connect(self.set_source_dir)
        self.set_flat_button.clicked.connect(self.set_flat_dir)
        self.set_dated_button.clicked.connect(self.set_dated_dir)
        self.add_time_button.clicked.connect(self.add_time)
        self.remove_time_button.clicked.connect(self.remove_selected_time)
        self.save_button.clicked.connect(self.save_config)

        # Load config file
        self.config = {}
        self.load_config()

        # System tray setup
        self.tray_icon = QSystemTrayIcon(QIcon("super.ico"), self)
        tray_menu = QMenu()
        show_action = QAction("Show", self)
        quit_action = QAction("Quit", self)
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(show_action)
        tray_menu.addAction(quit_action)
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()

    def load_config(self):
        config_path = "file_mover_config.json"
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as config_file:
                    self.config = json.load(config_file)
                self.update_labels()
                QMessageBox.information(self, "Configuration Loaded", "Existing configuration loaded successfully.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to load configuration: {e}")
        else:
            QMessageBox.information(self, "No Configuration", "No existing configuration found.")

    def update_labels(self):
        self.source_dir_label.setText(f"Super Staging Path: {self.config.get('source_dir', 'Not Set')}")
        self.flat_dir_label.setText(f"Staging Path: {self.config.get('flat_dir', 'Not Set')}")
        self.dated_dir_label.setText(f"PDF Archive Path: {self.config.get('dated_dir', 'Not Set')}")
        self.move_times_list.clear()
        for time in self.config.get('move_times', []):
            self.move_times_list.addItem(time)

    def set_source_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Super Staging Path")
        if dir_path:
            self.source_dir_label.setText(f"Super Staging Path: {dir_path}")
            self.config['source_dir'] = dir_path

    def set_flat_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Staging Path")
        if dir_path:
            self.flat_dir_label.setText(f"Staging Path: {dir_path}")
            self.config['flat_dir'] = dir_path

    def set_dated_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select PDF Archive Path")
        if dir_path:
            self.dated_dir_label.setText(f"PDF Archive Path: {dir_path}")
            self.config['dated_dir'] = dir_path

    def add_time(self):
        time, ok = QInputDialog.getText(self, "Add Time", "Enter time (HH:MM AM/PM):")
        if ok and time:
            self.move_times_list.addItem(time)

    def remove_selected_time(self):
        selected_item = self.move_times_list.currentItem()
        if selected_item:
            self.move_times_list.takeItem(self.move_times_list.row(selected_item))

    def save_config(self):
        self.config['move_times'] = [self.move_times_list.item(i).text() for i in range(self.move_times_list.count())]
        if all(key in self.config for key in ['source_dir', 'flat_dir', 'dated_dir']):
            try:
                with open("file_mover_config.json", "w") as config_file:
                    json.dump(self.config, config_file)
                self.daemon_process = subprocess.Popen(["python", "daemon.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                QMessageBox.information(self, "Saved", "Configuration saved! Daemon has been started.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save configuration or start daemon: {e}")
        else:
            QMessageBox.warning(self, "Incomplete", "Please set all directories.")

    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "Super Staging Config",
            "Application minimized to tray.",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show()

    def quit_application(self):
        if hasattr(self, 'daemon_process'):
            self.daemon_process.terminate()
        self.tray_icon.hide()
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = FileMoverGUI()
    window.show()
    sys.exit(app.exec())
