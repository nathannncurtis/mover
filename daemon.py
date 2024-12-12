import os
import shutil
import json
import time
from datetime import datetime
import logging

logging.basicConfig(
    filename="file_mover.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


class FileMoverHandler:
    def __init__(self, config):
        self.source_dir = config['source_dir']
        self.flat_dir = config['flat_dir']
        self.dated_dir = config['dated_dir']
        self.move_times = [datetime.strptime(t, "%I:%M %p").time() for t in config.get('move_times', [])]
        self.last_moved = None
        logging.info(f"Handler initialized with source_dir: {self.source_dir}, flat_dir: {self.flat_dir}, dated_dir: {self.dated_dir}, move_times: {self.move_times}")

    def is_move_time(self):
        
        # Check if the current time matches any configured move time, ensuring no duplicate triggers.
        
        current_time = datetime.now()
        for move_time in self.move_times:
            move_datetime = datetime.combine(current_time.date(), move_time)
            if abs((move_datetime - current_time).total_seconds()) < 5:  # Within 5 seconds
                if self.last_moved != move_datetime:  # Avoid duplicate triggers
                    return move_datetime
        return None

    def process_directory(self):
        
        # Processes files in the source directory:
        # - Copies files to the flat directory (ignores parent directories).
        # - Copies files to the archive directory, preserving folder structure.
        # - Deletes the original files after successful copying.
        
        logging.info(f"Processing directory: {self.source_dir}")
        for root, _, files in os.walk(self.source_dir):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    # Copy to flat directory
                    shutil.copy(file_path, os.path.join(self.flat_dir, file))
                    logging.info(f"Copied {file_path} to flat directory {self.flat_dir}")

                    # Copy to archive with parent folders
                    archive_path = os.path.join(self.dated_dir, os.path.relpath(root, self.source_dir))
                    os.makedirs(archive_path, exist_ok=True)
                    shutil.copy(file_path, os.path.join(archive_path, file))
                    logging.info(f"Archived {file_path} to {archive_path}")

                    # Delete the original file
                    os.remove(file_path)
                    logging.info(f"Deleted original file {file_path}")

                except Exception as e:
                    logging.error(f"Error processing file {file_path}: {e}")


def start_monitoring():
    
    # Main loop for the file mover daemon. Continuously checks for move times
    # and processes the source directory when a move time is reached.
    
    try:
        with open("file_mover_config.json", "r") as config_file:
            config = json.load(config_file)
    except Exception as e:
        logging.critical(f"Failed to load configuration: {e}")
        return

    source_dir = config.get('source_dir')
    if not source_dir:
        logging.critical("Source directory not set in configuration.")
        return

    handler = FileMoverHandler(config)

    logging.info("Monitoring initialized and running.")

    try:
        while True:
            move_time = handler.is_move_time()
            if move_time:
                logging.info(f"Triggered move at {move_time.strftime('%I:%M %p')}")
                handler.process_directory()
                handler.last_moved = move_time
            time.sleep(1)  # Sleep to prevent excessive CPU usage
    except KeyboardInterrupt:
        logging.info("Monitoring stopped by user.")
        return


if __name__ == "__main__":
    start_monitoring()
