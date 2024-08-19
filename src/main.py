import os
import json
import requests
from urllib.parse import urlparse
import logging
from tqdm import tqdm

# Set up log directory and file
log_dir = 'logs'  # Replace with your desired log directory
log_file = 'url_check.log'
os.makedirs(log_dir, exist_ok=True)  # Create log directory if it doesn't exist
log_path = os.path.join(log_dir, log_file)

# Set up logging to overwrite the log file on each run
logging.basicConfig(filename=log_path, level=logging.WARN, 
                    format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')


def check_url(url, file_path):
    # Skip URLs that end with .csv or .zip
    if url.endswith(('.csv', '.zip')):
        logging.info(f"Skipping URL (ends with .csv or .zip) in file {file_path}: {url}")
        return

    try:
        response = requests.head(url, allow_redirects=True, timeout=10)
        if response.status_code == 200:
            logging.info(f"URL is working in file {file_path}: {url}")
        else:
            logging.warning(f"URL might be broken, status code {response.status_code} in file {file_path}: {url}")
    except requests.RequestException as e:
        logging.error(f"Error checking URL in file {file_path}: {url} - {e}")

def find_and_check_urls(data, file_path):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "data" and isinstance(value, str):
                parsed_url = urlparse(value)
                if parsed_url.scheme and parsed_url.netloc:
                    check_url(value, file_path)
                else:
                    logging.error(f"Invalid URL format in 'data' in file {file_path}: {value}")
            else:
                find_and_check_urls(value, file_path)  # Recursive call for nested dictionaries
    elif isinstance(data, list):
        for item in data:
            find_and_check_urls(item, file_path)  # Recursive call for lists

def process_json_file(file_path):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        logging.error(f"Failed to load JSON file {file_path} - {e}")
        return

    find_and_check_urls(data, file_path)

def process_all_json_files(root_directory):
    # Gather all JSON files
    json_files = []
    for dirpath, _, filenames in os.walk(root_directory):
        for filename in filenames:
            if filename.endswith('.json'):
                file_path = os.path.join(dirpath, filename)
                json_files.append(file_path)

    # Process JSON files with progress bar
    for file_path in tqdm(json_files, desc='Processing JSON files', unit='file'):
        logging.info(f"Processing file: {file_path}")
        process_json_file(file_path)

if __name__ == "__main__":
    root_directory = './test'  # Replace with your root directory path
    process_all_json_files(root_directory)
