import os
import time
import base64
import logging
import requests
import tempfile
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fpdf import FPDF
from pydantic import BaseModel
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
import shutil

app = FastAPI()

# Configure logging to write to a file and the console
logging.basicConfig(filename='app.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s')
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(name)s - %(message)s')
console.setFormatter(formatter)
logging.getLogger().addHandler(console)

# Get the directory where the script is located
script_directory = os.path.dirname(os.path.abspath(__file__))
# Create a temporary directory within the script's directory
temp_directory = tempfile.mkdtemp(dir=script_directory)

class Web2PDF:
    def __init__(self, urls):
        self.logger = logging.getLogger("Web2PDF")
        self.urls = [
            f"http://{url.strip()}" if not url.startswith("http") else url.strip()
            for url in urls
        ]
        self.logger.debug(f"Initialized with URLs: {self.urls}")
        self.driver = self._setup_driver()

    def _setup_driver(self):
        self.logger.debug("Setting up Chrome driver")
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        driver = webdriver.Chrome(
            service=ChromeService(ChromeDriverManager().install()), options=chrome_options
        )
        self.logger.debug("Chrome driver setup complete")
        return driver

    def save_page_as_pdf(self, url, base_filename):
        self.logger.debug(f"Saving {url} to PDF as {base_filename}")
        self.driver.get(url)
        time.sleep(5)  # Wait for the page to load

        # Try to dismiss the cookie consent pop-up
        try:
            wait = WebDriverWait(self.driver, 10)
            consent_button = wait.until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Accept')]"))
            )
            consent_button.click()
            self.logger.debug("Dismissed cookie consent pop-up")
        except Exception as e:
            self.logger.warning(f"No cookie consent pop-up found or could not be dismissed: {e}")

        time.sleep(5)  # Additional wait time to ensure pop-up is dismissed

        print_options = {
            "landscape": False,
            "displayHeaderFooter": False,
            "printBackground": True,
            "preferCSSPageSize": True,
        }

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, dir=temp_directory) as temp_file:
            result = self.driver.execute_cdp_cmd("Page.printToPDF", print_options)
            temp_file.write(base64.b64decode(result["data"]))
            self.logger.debug(f"Saved PDF to temporary file: {temp_file.name}")
            return temp_file.name

    def run(self):
        self.logger.debug("Running Web2PDF process")
        pdf_file_paths = []
        for i, url in enumerate(self.urls):
            self.logger.debug(f"Processing URL {i + 1}/{len(self.urls)}: {url}")
            pdf_file_paths.append(self.save_page_as_pdf(url, f"output_{i + 1}"))
        self.driver.quit()
        self.logger.debug("Web2PDF process complete")
        return pdf_file_paths


class Web2Text:
    def __init__(self, urls):
        self.logger = logging.getLogger("Web2Text")
        self.urls = [
            url.strip() if url.startswith("http") else f"http://{url.strip()}"
            for url in urls
        ]
        self.logger.debug(f"Initialized with URLs: {self.urls}")

    def _get_text_from_website(self, url):
        try:
            self.logger.debug(f"Fetching URL: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, "html.parser")
            paragraphs = soup.find_all("p")
            extracted_text = "\n\n".join([p.get_text(strip=True) for p in paragraphs])
            self.logger.debug(f"Successfully extracted text from: {url}")
            return extracted_text
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching URL {url}: {e}")
            return ""

    def _save_text_to_pdf(self, text, filename):
        try:
            self.logger.debug(f"Saving text to PDF: {filename}")
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False, dir=temp_directory) as temp_file:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_auto_page_break(auto=True, margin=15)
                pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 10, text.encode("latin-1", "replace").decode("latin-1"))
                pdf.output(temp_file.name, "F")
                self.logger.debug(f"Saved PDF to temporary file: {temp_file.name}")
                return temp_file.name
        except Exception as e:
            self.logger.error(f"Error saving PDF {filename}: {e}")

    def run(self):
        self.logger.debug("Running Web2Text process")
        pdf_file_paths = []
        for i, url in enumerate(self.urls):
            self.logger.debug(f"Processing URL {i + 1}/{len(self.urls)}: {url}")
            text_data = self._get_text_from_website(url)
            if text_data:
                file_path = self._save_text_to_pdf(text_data, f"scraped_data_{i + 1}.pdf")
                pdf_file_paths.append(file_path)
            else:
                self.logger.warning(f"No text extracted from URL: {url}")
        self.logger.debug("Web2Text process complete")
        return pdf_file_paths


class URLList(BaseModel):
    urls: str


@app.post("/web2pdf")
async def generate_pdf(data: URLList):
    urls = [url.strip() for url in data.urls.split(",")]
    web2pdf = Web2PDF(urls)
    pdf_file_paths = web2pdf.run()
    return JSONResponse(content={"files": pdf_file_paths})


@app.post("/web2text")
async def generate_text_pdf(data: URLList):
    urls = [url.strip() for url in data.urls.split(",")]
    web2text = Web2Text(urls)
    pdf_file_paths = web2text.run()
    return JSONResponse(content={"files": pdf_file_paths})