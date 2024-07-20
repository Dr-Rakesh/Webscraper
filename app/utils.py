# -*- coding: utf-8 -*-
"""
Created on Sat Jul 20 21:48:58 2024

@author: RakeshR(DataScientis
"""

import os
import logging
import requests
import uuid
import zipfile
import tempfile
from typing import List, Callable

def setup_logging(log_level: int = logging.INFO) -> None:
    """
    Set up logging with the given log level.
    """
    logging.basicConfig(level=log_level,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

def create_temp_file(content: str, extension: str = ".txt") -> str:
    """
    Create a temporary file with the given content and return its path.
    """
    temp_filename = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}{extension}")
    with open(temp_filename, 'w') as temp_file:
        temp_file.write(content)
    return temp_filename

def download_url_content(url: str) -> str:
    """
    Download and return the content of the given URL as a string.
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Error downloading content from {url}: {e}")
        raise

def zip_files(file_paths: List[str], zip_filename: str) -> str:
    """
    Create a ZIP file containing the given file paths and return its path.
    """
    zip_filepath = os.path.join(tempfile.gettempdir(), zip_filename)
    with zipfile.ZipFile(zip_filepath, 'w') as zipf:
        for file_path in file_paths:
            zipf.write(file_path, os.path.basename(file_path))
    return zip_filepath

def delete_file(file_path: str) -> None:
    """
    Delete the file at the given path.
    """
    try:
        os.remove(file_path)
        logging.info(f"Deleted file: {file_path}")
    except Exception as e:
        logging.error(f"Error deleting file {file_path}: {e}")

def process_urls(urls: List[str], process_func: Callable[[str], str]) -> List[str]:
    """
    Process a list of URLs using the provided process function and return a list of file paths.
    """
    file_paths = []
    for url in urls:
        try:
            content = download_url_content(url)
            file_path = process_func(content)
            file_paths.append(file_path)
        except Exception as e:
            logging.error(f"Error processing URL {url}: {e}")
    return file_paths

# Example process function for creating text files from URL content
def save_as_text(content: str) -> str:
    return create_temp_file(content, extension=".txt")

# Example process function for creating PDFs from URL content (placeholder)
def save_as_pdf(content: str) -> str:
    # This is a placeholder for PDF creation logic
    # You would need to implement the actual logic to convert HTML content to PDF
    return create_temp_file(content, extension=".pdf")