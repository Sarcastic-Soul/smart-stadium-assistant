import os
import sys

# Add the backend directory to the path so app can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.main import app

# Vercel looks for a handler or application instance named app at this entrypoint
# The app instance imported from app.main is the FastAPI application
