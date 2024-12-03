import os
import shutil
import json
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

# Set up logging
logging.basicConfig(
    filename="file_mover.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

class FileMoverHandler(FileSystemEventHandler):
    def __init__(self, config):
        self.flat_dir = config['flat_dir']
        self.dated_dir = config['dated_dir']
        logging.info(f"Initialized FileMoverHandler with flat_dir: {self.flat_dir}, dated_dir: {self.dated_dir}")

    def process_directory(self, source_dir):
        logging.info(f"Starting to process directory: {source_dir}")
        # Walk through the dated structure in source_dir
        for root, _, files in os.walk(source_dir):
            logging.debug(f"Walking directory: {root}")
            for file in files:
                file_path = os.path.join(root, file)
                logging.debug(f"Found file: {file_path}")
                try:
                    # Copy file (not structure) to the staging directory
                    staging_path = os.path.join(self.flat_dir, file)
                    shutil.copy(file_path, staging_path)
                    logging.info(f"Copied {file_path} to staging directory at {staging_path}")

                    # Copy file with structure to the archive directory
                    relative_path = os.path.relpath(file_path, source_dir)
                    archive_path = os.path.join(self.dated_dir, relative_path)
                    os.makedirs(os.path.dirname(archive_path), exist_ok=True)
                    shutil.copy(file_path, archive_path)
                    logging.info(f"Copied {file_path} to archive directory at {archive_path}")
                except Exception as e:
                    logging.error(f"Error processing file {file_path}: {e}")

    def on_any_event(self, event):
        logging.debug(f"Event detected: {event.event_type} at {event.src_path}")
        if event.event_type in ["created", "modified"]:
            if os.path.isdir(event.src_path):
                logging.info(f"Directory event detected: {event.src_path}")
                self.process_directory(event.src_path)
            else:
                logging.info(f"File event detected: {event.src_path}")

def start_monitoring():
    try:
        with open("file_mover_config.json", "r") as config_file:
            config = json.load(config_file)
        logging.info("Loaded configuration successfully")
    except Exception as e:
        logging.critical(f"Failed to load configuration file: {e}")
        return

    source_dir = config.get('source_dir')
    if not source_dir:
        logging.critical("Source directory not set in configuration. Exiting.")
        return

    handler = FileMoverHandler(config)

    # Process the directory initially
    try:
        logging.info("Starting initial directory processing")
        handler.process_directory(source_dir)
    except Exception as e:
        logging.error(f"Error during initial directory processing: {e}")

    # Set up observer to monitor changes
    observer = Observer()
    observer.schedule(handler, source_dir, recursive=True)
    observer.start()
    logging.info(f"Started monitoring directory: {source_dir}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("KeyboardInterrupt detected. Stopping observer.")
        observer.stop()
    observer.join()
    logging.info("Observer stopped.")

if __name__ == "__main__":
    logging.info("Starting File Mover Daemon")
    start_monitoring()
