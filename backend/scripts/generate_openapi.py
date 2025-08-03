#!/usr/bin/env python3
"""
Generate OpenAPI schema for the API
"""

import json
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from app.main import app

def generate_openapi_schema():
    """Generate OpenAPI schema and save to file"""
    schema = app.openapi()
    
    # Save to backend directory
    backend_dir = Path(__file__).parent.parent
    schema_path = backend_dir / "openapi.json"
    
    with open(schema_path, 'w') as f:
        json.dump(schema, f, indent=2)
    
    print(f"✅ OpenAPI schema generated at: {schema_path}")
    
    # Also save to frontend directory for convenience
    frontend_dir = backend_dir.parent / "frontend"
    if frontend_dir.exists():
        frontend_schema_path = frontend_dir / "openapi.json"
        
        with open(frontend_schema_path, 'w') as f:
            json.dump(schema, f, indent=2)
        
        print(f"✅ OpenAPI schema copied to: {frontend_schema_path}")

if __name__ == "__main__":
    generate_openapi_schema()