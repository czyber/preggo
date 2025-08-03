# Full-Stack Boilerplate

A modern, type-safe full-stack boilerplate with FastAPI backend and Nuxt 3 frontend, featuring automated type generation and seamless API integration.

## Features

### 🚀 Backend (FastAPI)
- **FastAPI** with automatic OpenAPI documentation
- **SQLModel** for type-safe database operations
- **Pydantic** for data validation and serialization
- **Alembic** for database migrations
- **Poetry** for dependency management
- **CORS** support for cross-origin requests

### 🎨 Frontend (Nuxt 3)
- **Nuxt 3** with Vue 3 and TypeScript
- **Pinia** for state management
- **Tailwind CSS** for styling
- **openapi-fetch** for type-safe API calls
- **openapi-typescript** for automatic type generation
- **File-based routing** with automatic code splitting

### 🔧 Developer Experience
- **Automated type generation** from OpenAPI schema
- **Type-safe API client** with full IntelliSense
- **Hot reloading** for both frontend and backend
- **Comprehensive logging system** with centralized log viewing
- **Makefile** for easy development commands
- **Comprehensive documentation** and examples

## Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Poetry (for Python dependency management)

### 1. Installation

```bash
# Clone or create your project
cd your-project-directory

# Install all dependencies
make install
```

### 2. First Time Setup

```bash
# Complete setup (install + create migration + migrate + generate types)
make setup
```

### 3. Development

```bash
# Start both frontend and backend servers
make dev
```

This will start:
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- API Documentation: http://localhost:8000/docs

## Project Structure

```
.
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/   # API route handlers
│   │   │   └── __init__.py  # API router configuration
│   │   ├── core/
│   │   │   ├── config.py    # Application configuration
│   │   │   └── __init__.py
│   │   ├── db/
│   │   │   ├── session.py   # Database session management
│   │   │   └── __init__.py
│   │   ├── models/          # SQLModel database models
│   │   ├── schemas/         # Pydantic schemas for API
│   │   ├── services/        # Business logic services
│   │   └── main.py          # FastAPI application setup
│   ├── alembic/             # Database migrations
│   ├── scripts/             # Utility scripts
│   ├── pyproject.toml       # Poetry configuration
│   └── alembic.ini         # Alembic configuration
├── frontend/                # Nuxt 3 frontend
│   ├── assets/
│   │   └── css/            # Global styles
│   ├── components/          # Vue components
│   ├── composables/         # Vue composables
│   │   └── useApi.ts       # API client composable
│   ├── layouts/             # Nuxt layouts
│   ├── pages/               # File-based routing
│   ├── stores/              # Pinia stores
│   ├── types/
│   │   └── api.ts          # Auto-generated API types
│   ├── nuxt.config.ts       # Nuxt configuration
│   └── package.json         # Dependencies and scripts
├── Makefile                 # Development commands
└── README.md               # This file
```

## Development Commands

### Main Commands
- `make dev` - Start both frontend and backend servers
- `make install` - Install all dependencies
- `make setup` - Complete first-time setup
- `make generate-types` - Generate OpenAPI schema and frontend types
- `make migrate` - Run database migrations
- `make logs` - Show last 50 combined frontend and backend logs
- `make stop` - Stop all running servers
- `make clean` - Clean up generated files

### Individual Commands
- `make dev-backend` - Start only the backend server
- `make dev-frontend` - Start only the frontend server
- `make install-backend` - Install only backend dependencies
- `make install-frontend` - Install only frontend dependencies
- `make create-migration` - Create a new database migration

## Type-Safe API Integration

### 1. Backend Schema Generation

The backend automatically generates OpenAPI schema from your FastAPI models:

```python
# backend/app/models/item.py
from sqlmodel import Field, SQLModel

class Item(SQLModel, table=True):
    id: int = Field(primary_key=True)
    name: str
    description: str | None = None
```

### 2. Frontend Type Generation

Types are automatically generated from the OpenAPI schema:

```bash
make generate-types
```

### 3. Type-Safe API Client

Use the generated types in your frontend code:

```typescript
// frontend/composables/useApi.ts
import type { components } from '~/types/api'

type Item = components['schemas']['ItemRead']

const api = useApi()
const { data, error } = await api.getItems()
// data is fully typed as Item[]
```

## Adding New Features

### 1. Add a New Model

1. **Create SQLModel** in `backend/app/models/`:
   ```python
   # backend/app/models/user.py
   from sqlmodel import Field, SQLModel
   
   class User(SQLModel, table=True):
       id: int = Field(primary_key=True)
       email: str = Field(unique=True)
       name: str
   ```

2. **Create Pydantic schemas** in `backend/app/schemas/`:
   ```python
   # backend/app/schemas/user.py
   from pydantic import BaseModel
   
   class UserCreate(BaseModel):
       email: str
       name: str
   
   class UserRead(BaseModel):
       id: int
       email: str
       name: str
   ```

3. **Create API endpoints** in `backend/app/api/endpoints/`:
   ```python
   # backend/app/api/endpoints/users.py
   from fastapi import APIRouter
   from app.schemas.user import UserCreate, UserRead
   
   router = APIRouter(prefix="/users", tags=["users"])
   
   @router.post("/", response_model=UserRead)
   def create_user(user: UserCreate):
       # Implementation
       pass
   ```

4. **Register the router** in `backend/app/api/__init__.py`:
   ```python
   from app.api.endpoints import users
   
   api_router.include_router(users.router)
   ```

5. **Generate migration**:
   ```bash
   make create-migration
   make migrate
   ```

6. **Generate types**:
   ```bash
   make generate-types
   ```

### 2. Add Frontend Store

1. **Create Pinia store** in `frontend/stores/`:
   ```typescript
   // frontend/stores/users.ts
   import { defineStore } from 'pinia'
   import type { components } from '~/types/api'
   
   type User = components['schemas']['UserRead']
   
   export const useUsersStore = defineStore('users', {
     state: () => ({
       users: [] as User[],
       loading: false,
     }),
     
     actions: {
       async fetchUsers() {
         this.loading = true
         const api = useApi()
         const { data } = await api.getUsers()
         this.users = data || []
         this.loading = false
       }
     }
   })
   ```

2. **Create page** in `frontend/pages/`:
   ```vue
   <!-- frontend/pages/users.vue -->
   <template>
     <div>
       <h1>Users</h1>
       <div v-for="user in users" :key="user.id">
         {{ user.name }} ({{ user.email }})
       </div>
     </div>
   </template>
   
   <script setup>
   const store = useUsersStore()
   const { users } = storeToRefs(store)
   
   onMounted(() => {
     store.fetchUsers()
   })
   </script>
   ```

## Environment Configuration

### Backend Configuration

Edit `backend/app/core/config.py` or use environment variables:

```python
class Settings(BaseSettings):
    PROJECT_NAME: str = "Your App Name"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    DATABASE_URL: str = "sqlite:///./app.db"
    SECRET_KEY: str = "your-secret-key-here"
```

### Frontend Configuration

Edit `frontend/nuxt.config.ts` or use environment variables:

```typescript
export default defineNuxtConfig({
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:8000/api/v1'
    }
  }
})
```

## Production Deployment

### Backend

1. **Install dependencies**:
   ```bash
   cd backend && poetry install --only=main
   ```

2. **Run migrations**:
   ```bash
   poetry run alembic upgrade head
   ```

3. **Start with Gunicorn**:
   ```bash
   poetry run gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
   ```

### Frontend

1. **Install dependencies**:
   ```bash
   cd frontend && npm ci
   ```

2. **Build for production**:
   ```bash
   npm run build
   ```

3. **Start production server**:
   ```bash
   npm run preview
   ```

## Troubleshooting

### Common Issues

1. **Types not generated**: Run `make generate-types`
2. **Migration errors**: Check your model changes and run `make create-migration`
3. **CORS errors**: Check `BACKEND_CORS_ORIGINS` in backend config
4. **Port conflicts**: Modify ports in `Makefile` or config files

### Development Tips

1. **Always regenerate types after backend changes**:
   ```bash
   make generate-types
   ```

2. **Use the type-safe API client**:
   ```typescript
   const api = useApi()
   const { data, error } = await api.getItems()
   ```

3. **Check API documentation**: http://localhost:8000/docs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and type checks
5. Submit a pull request

## License

This boilerplate is open source and available under the [MIT License](LICENSE).