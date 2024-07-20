from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware
import os
import uuid
import zipfile
import logging

# Ensure the parent directory is in the sys.path for absolute imports
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import utility functions using absolute imports
from utils import setup_logging, delete_file

# Import the required classes from your module
from Data_extractor_V4 import Web2PDF, Web2Text  # Removed Web2Image import

# Set up logging
setup_logging(logging.INFO)

app = FastAPI()

# To allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define a Pydantic model to validate the input data
class URLList(BaseModel):
    urls: List[str]

# Serve static files (like CSS, JS, images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Set up Jinja2 templates
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/web2pdf")
async def create_pdf(urls: URLList, background_tasks: BackgroundTasks):
    try:
        # Generate a unique output directory for this request
        output_dir = f"outputs/{uuid.uuid4()}"
        os.makedirs(output_dir, exist_ok=True)
        
        # Create PDF files from the provided URLs
        web2pdf = Web2PDF(urls.urls)
        pdf_files = web2pdf.run()

        if not pdf_files:
            raise HTTPException(status_code=500, detail="Failed to generate PDFs")

        # Create a zip file containing all PDF files
        zip_filename = os.path.join(output_dir, "output.zip")
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for pdf_file in pdf_files:
                zipf.write(pdf_file, os.path.basename(pdf_file))

        # Schedule file deletion after response is sent
        background_tasks.add_task(delete_file, zip_filename)

        return FileResponse(zip_filename, media_type='application/zip', filename="output.zip")
    except Exception as e:
        logging.error(f"Error in /web2pdf endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/web2text")
async def extract_text(urls: URLList, background_tasks: BackgroundTasks):
    try:
        # Generate a unique output directory for this request
        output_dir = f"outputs/{uuid.uuid4()}"
        os.makedirs(output_dir, exist_ok=True)

        # Extract text from the provided URLs
        web2text = Web2Text(urls.urls) 
        text_files = web2text.run()

        if not text_files:
            raise HTTPException(status_code=500, detail="Failed to extract text")

        # Create a zip file containing all text files
        zip_filename = os.path.join(output_dir, "output.zip")
        with zipfile.ZipFile(zip_filename, 'w') as zipf:
            for text_file in text_files:
                zipf.write(text_file, os.path.basename(text_file))

        # Schedule file deletion after response is sent
        background_tasks.add_task(delete_file, zip_filename)

        return FileResponse(zip_filename, media_type='application/zip', filename="output.zip")
    except Exception as e:
        logging.error(f"Error in /web2text endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# You can run this FastAPI app using an ASGI server like uvicorn
# Example command: uvicorn main:app --reload