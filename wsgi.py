"""WSGI entry point for gunicorn."""
import sys
import os

# Add library directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'library'))

from app import app

if __name__ == '__main__':
    app.run()
