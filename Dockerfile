# Multi-stage build for backend and frontend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

# Backend stage
FROM python:3.11-slim

WORKDIR /app

# Install Poetry
RUN pip install poetry

# Copy backend files
COPY backend/pyproject.toml backend/poetry.lock ./
RUN poetry config virtualenvs.create false && poetry install --no-dev

COPY backend/ ./

# Copy built frontend
COPY --from=frontend-builder /app/frontend/.output ./frontend/.output

# Expose port
EXPOSE 8000

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]