import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog, QMessageBox
import json

class FileMoverGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("File Mover Configuration")
        self.layout = QVBoxLayout()

        self.flat_dir_label = QLabel("Flat Directory: Not Set")
        self.dated_dir_label = QLabel("Dated Directory: Not Set")
        self.source_dir_label = QLabel("Source Directory: Not Set")

        self.layout.addWidget(self.source_dir_label)
        self.layout.addWidget(self.flat_dir_label)
        self.layout.addWidget(self.dated_dir_label)

        self.set_source_button = QPushButton("Set Source Directory")
        self.set_flat_button = QPushButton("Set Flat Directory")
        self.set_dated_button = QPushButton("Set Dated Directory")
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

    def set_source_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Source Directory")
        if dir_path:
            self.source_dir_label.setText(f"Source Directory: {dir_path}")
            self.config['source_dir'] = dir_path

    def set_flat_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Flat Directory")
        if dir_path:
            self.flat_dir_label.setText(f"Flat Directory: {dir_path}")
            self.config['flat_dir'] = dir_path

    def set_dated_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Dated Directory")
        if dir_path:
            self.dated_dir_label.setText(f"Dated Directory: {dir_path}")
            self.config['dated_dir'] = dir_path

    def save_config(self):
        if all(key in self.config for key in ['source_dir', 'flat_dir', 'dated_dir']):
            with open("file_mover_config.json", "w") as config_file:
                json.dump(self.config, config_file)
            QMessageBox.information(self, "Saved", "Configuration saved! Daemon will start.")
        else:
            QMessageBox.warning(self, "Incomplete", "Please set all directories.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FileMoverGUI()
    window.show()
    sys.exit(app.exec_())