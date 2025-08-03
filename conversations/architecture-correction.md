# Architecture Correction: SQLModel Sessions + Supabase Auth

## Problem Statement

The pregnancy tracking app "preggo" was initially implemented using direct Supabase client manipulation for data operations, which goes against best practices for backend architecture. This created several issues:

- **Tight coupling**: Database operations were tightly coupled to Supabase's client library
- **Limited flexibility**: Hard to switch databases or modify data layer logic
- **Testing difficulties**: Hard to mock database operations for unit testing
- **Poor separation of concerns**: Business logic mixed with database client code
- **SQLModel underutilization**: Not leveraging the power of SQLModel for type safety and ORM features

## Corrected Architecture

### Core Principles

1. **SQLModel for all database operations**: Use proper SQLAlchemy/SQLModel sessions for all data manipulation
2. **Supabase for authentication and storage only**: Limit Supabase to JWT validation and file storage
3. **Service layer pattern**: Implement proper service layers with dependency injection
4. **Separation of concerns**: Clear boundaries between authentication, data access, and business logic

### Architecture Components

#### 1. Database Configuration (`/Users/bernhardczypka/private/preggo/backend/app/db/session.py`)
- **BEFORE**: SQLite configuration with mixed Supabase usage
- **AFTER**: PostgreSQL connection to Supabase database with proper connection pooling
- **Key changes**: 
  - Uses Supabase PostgreSQL connection string
  - Proper pool configuration for production
  - Session management through dependency injection

#### 2. Supabase Configuration (`/Users/bernhardczypka/private/preggo/backend/app/core/supabase.py`)
- **BEFORE**: Full database operations with direct table manipulation
- **AFTER**: Authentication and storage operations only
- **Key changes**:
  - Removed all database CRUD operations
  - Kept JWT token verification
  - Added file storage operations (upload, delete, signed URLs)
  - Clear documentation about limitations

#### 3. Service Layer (`/Users/bernhardczypka/private/preggo/backend/app/services/`)
- **NEW**: Complete service layer implementation with:
  - `BaseService`: Generic CRUD operations for all models
  - `UserService`: User-specific database operations
  - `PregnancyService`: Pregnancy-specific database operations
  - `WeeklyUpdateService`: Weekly update operations
  - Proper dependency injection patterns

#### 4. API Endpoints
- **BEFORE**: Direct Supabase client calls in endpoints
- **AFTER**: Service layer usage with SQLModel sessions
- **Updated files**:
  - `pregnancies.py`: Complete rewrite using pregnancy services
  - `auth.py`: Updated to use user services for profile operations

### How Each Component Works

#### Authentication Flow
1. **Frontend** sends JWT token in Authorization header
2. **Supabase JWT verification** validates the token and extracts user info
3. **Service layer** fetches additional user data from PostgreSQL using SQLModel
4. **Business logic** operates on SQLModel objects with type safety

#### Database Operations Flow
1. **Dependency injection** provides SQLModel session to endpoints
2. **Service layer** receives session and performs operations
3. **SQLModel** handles ORM mapping and type safety
4. **PostgreSQL** (via Supabase) stores the actual data
5. **Session management** handles transactions and cleanup

#### File Storage Flow
1. **Business logic** generates file paths and validates uploads
2. **Supabase Storage** handles actual file storage
3. **Public URLs** are returned for frontend access
4. **Database** stores only file URLs/paths, not file content

### Benefits of This Architecture

1. **Database Agnostic**: Can easily switch from Supabase PostgreSQL to any other PostgreSQL instance
2. **Type Safety**: Full type safety with SQLModel throughout the application
3. **Testability**: Easy to mock services and sessions for unit testing
4. **Maintainability**: Clear separation of concerns makes code easier to maintain
5. **Performance**: Proper connection pooling and session management
6. **Scalability**: Service layer can be easily extended with caching, monitoring, etc.

### Configuration Requirements

#### Environment Variables
```bash
# Database connection (Supabase PostgreSQL)
DATABASE_URL=postgresql://postgres:[password]@db.[project-id].supabase.co:5432/postgres

# Supabase Authentication
SUPABASE_URL=https://[project-id].supabase.co
SUPABASE_ANON_KEY=[anon-key]
SUPABASE_SERVICE_ROLE_KEY=[service-role-key]
SUPABASE_JWT_SECRET=[jwt-secret]
```

#### Database Schema
- All models defined in SQLModel format in `/app/models/`
- Database migrations handled by Alembic
- Schema matches Supabase PostgreSQL database

### Usage Examples

#### Creating a Pregnancy (Before vs After)

**BEFORE (Wrong Way):**
```python
# Direct Supabase client usage
pregnancy_record = {...}
created_pregnancy = await supabase_service.create_pregnancy(pregnancy_record)
```

**AFTER (Correct Way):**
```python
# Service layer with SQLModel session
from app.services import pregnancy_service
from app.db.session import get_session

async def create_pregnancy(
    pregnancy_data: PregnancyCreate,
    session: Session = Depends(get_session)
):
    created_pregnancy = await pregnancy_service.create_pregnancy(session, pregnancy_data)
    return PregnancyResponse.from_orm(created_pregnancy)
```

#### User Authentication (Before vs After)

**BEFORE (Wrong Way):**
```python
# Mixed Supabase client and direct database calls
profile = await supabase_service.get_user_profile(user_id)
```

**AFTER (Correct Way):**
```python
# JWT validation + service layer
user_data = supabase_service.verify_jwt_token(token)  # Auth only
profile = await user_service.get_by_id(session, user_data["sub"])  # Database via service
```

### Migration Checklist

- [x] Update database session configuration for PostgreSQL
- [x] Remove all database operations from Supabase service
- [x] Create comprehensive service layer with BaseService pattern
- [x] Update all API endpoints to use services + sessions
- [x] Ensure JWT token validation works with user_id extraction
- [x] Document the corrected architecture
- [ ] Update frontend to handle any API changes
- [ ] Add proper error handling and logging
- [ ] Implement comprehensive unit tests for services
- [ ] Add integration tests for API endpoints

### Important Notes

1. **User ID Mapping**: JWT tokens contain `sub` field which maps to user IDs in the database
2. **Session Management**: Always use dependency injection for database sessions
3. **Error Handling**: Services handle database errors, endpoints handle HTTP errors
4. **File Storage**: Continue using Supabase Storage for files, but store only URLs in database
5. **Authentication**: Supabase Auth remains the source of truth for authentication

This architecture correction ensures the application follows modern backend patterns while maintaining the benefits of Supabase for authentication and file storage.