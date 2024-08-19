import os
import json
import requests
from urllib.parse import urlparse
import logging
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# Set up log directory and file
log_dir = './out'  # log directory
log_file = 'broken_links.log'
os.makedirs(log_dir, exist_ok=True)  # Create log directory if it doesn't exist
log_path = os.path.join(log_dir, log_file)

# Set up logging to overwrite the log file on each run
logging.basicConfig(filename=log_path, level=logging.WARN, 
                    format='%(asctime)s - %(levelname)s - %(message)s', filemode='w')

CONSOLE_LOGGING =False

# Console Logging
if CONSOLE_LOGGING:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARN)
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    logging.getLogger().addHandler(console_handler)

# Flag for enabling/disabling parallel processing
PARALLEL_PROCESSING = True

def check_url(url, file_path):
    def make_request(url):
        try:
            response = requests.head(url, allow_redirects=True, timeout=10)
            if response.status_code == 200:
                logging.info(f"URL is working in file {file_path}: {url}")
                return True
            else:
                return False
        except requests.RequestException:
            return False

    # Skip URLs that end with .csv, .zip, csv, or zip, regardless of case or dot
    if url.lower().endswith(('csv', 'zip')):
        logging.info(f"Skipping URL (ends with csv or zip) in file {file_path}: {url}")
        return

    # Check if the URL starts with http://
    if url.startswith("http://"):
        https_url = url.replace("http://", "https://", 1)
        logging.info(f"Trying HTTPS version of the URL: {https_url}")

        if make_request(https_url):
            logging.info(f"HTTPS URL succeeded for file {file_path}: {https_url}")
            return
        else:
            logging.warning(f"Both HTTP and HTTPS failed for URL in file {file_path}: {url}")

    else:
        # Check the URL directly (for HTTPS)
        if not make_request(url):
            logging.warning(f"URL might be broken in file {file_path}: {url}")

def find_and_check_urls(data, file_path, results=None):
    if isinstance(data, dict):
        for key, value in data.items():
            if key == "data" and isinstance(value, str):
                parsed_url = urlparse(value)
                if parsed_url.scheme and parsed_url.netloc:
                    if results is not None:
                        results.append((value, file_path))
                    else:
                        check_url(value, file_path)
                else:
                    logging.error(f"Invalid URL format in 'data' in file {file_path}: {value}")
            else:
                find_and_check_urls(value, file_path, results)  # Recursive call for nested dictionaries
    elif isinstance(data, list):
        for item in data:
            find_and_check_urls(item, file_path, results)  # Recursive call for lists

def process_json_file(file_path, results=None):
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        logging.error(f"Failed to load JSON file {file_path} - {e}")
        return

    find_and_check_urls(data, file_path, results)

def process_all_json_files(root_directory, parallel=False):
    # Gather all JSON files
    json_files = []
    for dirpath, _, filenames in os.walk(root_directory):
        for filename in filenames:
            if filename.endswith('.json'):
                file_path = os.path.join(dirpath, filename)
                json_files.append(file_path)

    if parallel:
        # Use parallel processing
        all_urls = []
        for file_path in json_files:
            results = []
            process_json_file(file_path, results)
            all_urls.extend(results)

        # Process URLs with a progress bar
        with ThreadPoolExecutor() as executor:
            future_to_url = {executor.submit(check_url, url, file_path): (url, file_path) for url, file_path in all_urls}
            
            for future in tqdm(as_completed(future_to_url), total=len(future_to_url), desc='Processing URLs'):
                try:
                    future.result()  # This will raise any exceptions caught during execution
                except Exception as e:
                    logging.error(f"Exception during URL processing: {e}")

    else:
        # Sequential processing with progress bar
        for file_path in tqdm(json_files, desc='Processing JSON files', unit='file'):
            logging.info(f"Processing file: {file_path}")
            process_json_file(file_path)

if __name__ == "__main__":
    root_directory = './oa_repo/sources/us/va/'  # Replace with your root directory path
    process_all_json_files(root_directory, parallel=PARALLEL_PROCESSING)
    
    for handler in logging.getLogger().handlers:
        handler.flush()
    
