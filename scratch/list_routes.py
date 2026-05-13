import sys
import os

# Add the backend directory to sys.path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from backend.app.main import app

for route in app.routes:
    print(f"Path: {route.path}, Name: {route.name}")
