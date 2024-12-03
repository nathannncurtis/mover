import sys
import os
import subprocess
import json
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, 
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt

class FileMoverGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Staging Dropper & Archiver")

        self.resize(550, 500)
        screen_geometry = QApplication.primaryScreen().availableGeometry()
        x = (screen_geometry.width() - 500) // 2
        y = (screen_geometry.height() - 500) // 2
        self.move(x, y)
        self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)

        self.layout = QVBoxLayout()

        self.flat_dir_label = QLabel("Staging Path: Not Set")
        self.dated_dir_label = QLabel("PDF Archive Path: Not Set")
        self.source_dir_label = QLabel("Super Staging Path: Not Set")

        self.layout.addWidget(self.source_dir_label)
        self.layout.addWidget(self.flat_dir_label)
        self.layout.addWidget(self.dated_dir_label)

        self.set_source_button = QPushButton("Set Super Staging Path")
        self.set_flat_button = QPushButton("Set Staging Path")
        self.set_dated_button = QPushButton("Set PDF Archive Path")
        self.save_button = QPushButton("Save and Start Daemon")

        self.set_source_button.clicked.connect(self.set_source_dir)
        self.set_flat_button.clicked.connect(self.set_flat_dir)
        self.set_dated_button.clicked.connect(self.set_dated_dir)
        self.save_button.clicked.connect(self.save_config)

        self.layout.addWidget(self.set_source_button)
        self.layout.addWidget(self.set_flat_button)
        self.layout.addWidget(self.set_dated_button)
        self.layout.addWidget(self.save_button)
        self.setLayout(self.layout)

        self.config = {}

        # Load configuration if it exists
        self.load_config()

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

    def save_config(self):
        if all(key in self.config for key in ['source_dir', 'flat_dir', 'dated_dir']):
            try:
                with open("file_mover_config.json", "w") as config_file:
                    json.dump(self.config, config_file)
                
                # Start the daemon as a separate process
                subprocess.Popen(["python", "daemon.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                QMessageBox.information(self, "Saved", "Configuration saved! Daemon has been started.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save configuration or start daemon: {e}")
        else:
            QMessageBox.warning(self, "Incomplete", "Please set all directories.")

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Apply Fusion theme
    app.setStyle("Fusion")

    window = FileMoverGUI()
    window.show()
    sys.exit(app.exec())
