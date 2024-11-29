import time
import os
import shutil
import json
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class FileMoverHandler(FileSystemEventHandler):
    def __init__(self, config):
        self.flat_dir = config['flat_dir']
        self.dated_dir = config['dated_dir']

    def on_created(self, event):
        if event.is_directory:
            return
        file_path = event.src_path
        mod_time = os.path.getmtime(file_path)
        year = datetime.fromtimestamp(mod_time).strftime("%Y")
        month = datetime.fromtimestamp(mod_time).strftime("%m_%Y")
        day = datetime.fromtimestamp(mod_time).strftime("%d_%m")
        dated_path = os.path.join(self.dated_dir, year, month, day)
        os.makedirs(dated_path, exist_ok=True)
        shutil.move(file_path, os.path.join(dated_path, os.path.basename(file_path)))

def start_monitoring():
    with open("file_mover_config.json", "r") as config_file:
        config = json.load(config_file)

    source_dir = config['source_dir']
    event_handler = FileMoverHandler(config)
    observer = Observer()
    observer.schedule(event_handler, source_dir, recursive=False)
    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

if __name__ == "__main__":
    start_monitoring()