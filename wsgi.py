"""
WSGI entry point for the duplicate log finder application.
This file is used by Gunicorn to serve the Flask application.
"""

from api import app

if __name__ == "__main__":
    app.run()