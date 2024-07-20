import logging
from .utils import setup_logging

# Set up logging for the application
setup_logging(logging.INFO)

# Import the main app instance to make it available at the package level
from .main import app

# You can also include any package-level constants, variables, or initializations here
# For example:
APP_NAME = "My FastAPI Web Extractor"
VERSION = "1.0.0"
