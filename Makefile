.PHONY: install install-backend install-frontend dev dev-backend dev-frontend stop clean migrate generate-types setup logs

# Install all dependencies
install: install-backend install-frontend

install-backend:
	@echo "Installing backend dependencies..."
	cd backend && poetry install

install-frontend:
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Run migrations
migrate:
	@echo "Running database migrations..."
	cd backend && poetry run alembic upgrade head

# Generate OpenAPI schema and frontend types
generate-types:
	@echo "Generating OpenAPI schema..."
	cd backend && poetry run python scripts/generate_openapi.py
	@echo "Generating frontend types..."
	cd frontend && npm run generate-types

# Start both frontend and backend in development mode
dev:
	@echo "Starting development servers..."
	@make -j 2 dev-backend dev-frontend

dev-backend:
	@echo "Starting backend server..."
	cd backend && poetry run uvicorn app.main:app --reload --port 8000

dev-frontend:
	@echo "Starting frontend server..."
	cd frontend && npm run dev

# Stop all running servers
stop:
	@echo "Stopping all servers..."
	@pkill -f "uvicorn" || true
	@pkill -f "nuxt" || true

# Clean up
clean:
	@echo "Cleaning up..."
	rm -rf backend/__pycache__ backend/.pytest_cache backend/*.db
	rm -rf frontend/.nuxt frontend/.output frontend/node_modules
	rm -rf backend/.venv

# Create initial migration
create-migration:
	@echo "Creating initial migration..."
	cd backend && poetry run alembic revision --autogenerate -m "Initial migration"

# First time setup
setup: install create-migration migrate generate-types
	@echo "Setup complete! Run 'make dev' to start the development servers."

# Show combined logs
logs:
	@echo "Showing last 50 combined frontend and backend logs..."
	@cd backend && poetry run python scripts/show_logs.py

# Help
help:
	@echo "Available commands:"
	@echo "  make install         - Install all dependencies"
	@echo "  make setup           - First time setup (install + create migration + migrate + generate types)"
	@echo "  make dev             - Start both frontend and backend servers"
	@echo "  make dev-backend     - Start only the backend server"
	@echo "  make dev-frontend    - Start only the frontend server"
	@echo "  make migrate         - Run database migrations"
	@echo "  make generate-types  - Generate OpenAPI schema and frontend types"
	@echo "  make create-migration - Create a new database migration"
	@echo "  make logs            - Show last 50 combined frontend and backend logs"
	@echo "  make stop            - Stop all running servers"
	@echo "  make clean           - Clean up generated files"
	@echo "  make help            - Show this help message"