# Use Python base image and install Node.js
FROM python:3.11-slim

# Install Node.js
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Build frontend first
COPY frontend/package*.json ./frontend/
WORKDIR /app/frontend
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Setup backend
WORKDIR /app
COPY backend/pyproject.toml backend/poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-dev

COPY backend/ ./

# Expose port
EXPOSE 8000

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]