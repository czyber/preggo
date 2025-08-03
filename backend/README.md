# Backend - FastAPI Boilerplate

This is a FastAPI backend boilerplate with the following features:

## Technologies Used

- **FastAPI**: Modern, fast web framework for building APIs with Python 3.7+
- **SQLModel**: SQL databases in Python, designed for simplicity, compatibility, and robustness
- **Pydantic**: Data validation and settings management using Python type annotations
- **Alembic**: Database migration tool for SQLAlchemy
- **Poetry**: Python dependency management

## Project Structure

```
backend/
├── app/
│   ├── api/
│   │   ├── endpoints/       # API route handlers
│   │   └── __init__.py      # API router configuration
│   ├── core/
│   │   ├── config.py        # Application configuration
│   │   └── __init__.py
│   ├── db/
│   │   ├── session.py       # Database session management
│   │   └── __init__.py
│   ├── models/              # SQLModel database models
│   ├── schemas/             # Pydantic schemas for API
│   ├── services/            # Business logic services
│   ├── main.py              # FastAPI application setup
│   └── __init__.py
├── alembic/                 # Database migrations
├── scripts/                 # Utility scripts
├── pyproject.toml           # Poetry configuration
├── alembic.ini             # Alembic configuration
└── README.md
```

## Quick Start

1. **Install dependencies:**
   ```bash
   poetry install
   ```

2. **Run database migrations:**
   ```bash
   poetry run alembic upgrade head
   ```

3. **Start the development server:**
   ```bash
   poetry run uvicorn app.main:app --reload --port 8000
   ```

4. **Access the API:**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - OpenAPI schema: http://localhost:8000/openapi.json

## Development

### Creating a New Model

1. **Create a SQLModel in `app/models/`:**
   ```python
   from sqlmodel import Field, SQLModel
   
   class YourModel(SQLModel, table=True):
       id: int = Field(primary_key=True)
       name: str
   ```

2. **Create corresponding Pydantic schemas in `app/schemas/`:**
   ```python
   from pydantic import BaseModel
   
   class YourModelCreate(BaseModel):
       name: str
   
   class YourModelRead(BaseModel):
       id: int
       name: str
   ```

3. **Create API endpoints in `app/api/endpoints/`:**
   ```python
   from fastapi import APIRouter
   
   router = APIRouter(prefix="/your-models", tags=["your-models"])
   
   @router.get("/")
   def get_your_models():
       # Implementation
       pass
   ```

4. **Register the router in `app/api/__init__.py`:**
   ```python
   from app.api.endpoints import your_models
   
   api_router.include_router(your_models.router)
   ```

### Database Migrations

1. **Generate a new migration:**
   ```bash
   poetry run alembic revision --autogenerate -m "Add your model"
   ```

2. **Apply migrations:**
   ```bash
   poetry run alembic upgrade head
   ```

### Generate OpenAPI Schema

```bash
poetry run python scripts/generate_openapi.py
```

## Configuration

Configuration is managed through `app/core/config.py` using Pydantic Settings. You can override settings using environment variables or a `.env` file.

## Features

- **Type Safety**: Full type hints with Pydantic and SQLModel
- **Database Migrations**: Automatic schema migrations with Alembic
- **API Documentation**: Auto-generated OpenAPI/Swagger documentation
- **CORS Support**: Configurable CORS middleware
- **Environment Configuration**: Flexible configuration with environment variables