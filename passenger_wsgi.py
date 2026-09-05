"""
WSGI entry point for production deployment.

This module exposes the Flask application to a WSGI-compatible
production server such as Passenger.
"""

import os
import sys

# Add the project directory to Python's module search path.
sys.path.insert(0, os.path.dirname(__file__))

# Expose the Flask application as the WSGI application.
from app import app as application
