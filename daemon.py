import os
import shutil
import json
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileMoverHandler(FileSystemEventHandler):
    def __init__(self, config):
        self.flat_dir = config['flat_dir']
        self.dated_dir = config['dated_dir']

    def process_directory(self, source_dir):
        # Walk through the dated structure in source_dir
        for root, _, files in os.walk(source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Copy file (not structure) to the staging directory
                shutil.copy(file_path, os.path.join(self.flat_dir, file))

                # Copy file with structure to the archive directory
                relative_path = os.path.relpath(file_path, source_dir)
                archive_path = os.path.join(self.dated_dir, relative_path)
                os.makedirs(os.path.dirname(archive_path), exist_ok=True)
                shutil.copy(file_path, archive_path)

    def on_any_event(self, event):
        if event.event_type in ["created", "modified"]:
            if os.path.isdir(event.src_path):
                self.process_directory(event.src_path)

def start_monitoring():
    with open("file_mover_config.json", "r") as config_file:
        config = json.load(config_file)

    source_dir = config['source_dir']
    handler = FileMoverHandler(config)
    
    # Process the directory initially
    handler.process_directory(source_dir)

    # Set up observer to monitor changes
    observer = Observer()
    observer.schedule(handler, source_dir, recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_monitoring()
