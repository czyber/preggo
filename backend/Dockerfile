# Backend Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy dependency files
COPY pyproject.toml poetry.lock ./

COPY . .

# Install dependencies
RUN poetry config virtualenvs.create false && poetry install

# Expose port (Railway will override this with PORT env var)
EXPOSE 8000

# Start command - use PORT env variable from Railway, fallback to 8000
CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
