# Supabase Setup Guide for Preggo

This guide will walk you through setting up Supabase integration for the pregnancy tracking app "preggo". The setup includes both backend (Python/FastAPI) and frontend (Nuxt.js) configurations.

## Prerequisites

- Supabase account (sign up at https://supabase.com)
- Existing preggo project setup
- Python 3.9+ and Node.js 18+

## Part 1: Supabase Dashboard Setup (Manual Steps)

### 1.1 Create a New Supabase Project

1. Go to https://supabase.com and sign in to your account
2. Click "New Project"
3. Choose your organization
4. Enter project details:
   - **Name**: `preggo` (or your preferred name)
   - **Database Password**: Generate a strong password and save it securely
   - **Region**: Choose the region closest to your users
5. Click "Create new project"
6. Wait for the project to be created (this may take a few minutes)

### 1.2 Get Your Project Credentials

Once your project is ready, navigate to:
**Settings → API**

You'll need these values:
- **Project URL**: `https://your-project-id.supabase.co`
- **Project API Key (anon key)**: `eyJh...` (starts with eyJh)
- **Project API Key (service_role key)**: `eyJh...` (starts with eyJh, different from anon key)

Navigate to:
**Settings → Database**

You'll need:
- **Connection string**: The full PostgreSQL connection string
- **JWT Secret**: Found under "JWT Settings"

### 1.3 Configure Authentication (Optional for now)

Navigate to:
**Authentication → Settings**

Configure your authentication settings as needed for your app.

### 1.4 Database Schema Setup

Navigate to:
**SQL Editor**

We'll set up the initial schema for pregnancy tracking. Run this SQL:

```sql
-- Enable RLS (Row Level Security)
ALTER DEFAULT PRIVILEGES REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;

-- Create profiles table for user data
CREATE TABLE profiles (
  id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
  email TEXT,
  full_name TEXT,
  avatar_url TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create pregnancies table
CREATE TABLE pregnancies (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  user_id UUID REFERENCES profiles(id) ON DELETE CASCADE NOT NULL,
  due_date DATE NOT NULL,
  conception_date DATE,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  is_active BOOLEAN DEFAULT true
);

-- Create pregnancy_logs table for tracking symptoms, appointments, etc.
CREATE TABLE pregnancy_logs (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  pregnancy_id UUID REFERENCES pregnancies(id) ON DELETE CASCADE NOT NULL,
  log_date DATE NOT NULL,
  log_type TEXT NOT NULL, -- 'symptom', 'appointment', 'milestone', 'note'
  title TEXT NOT NULL,
  description TEXT,
  severity INTEGER, -- 1-5 scale for symptoms
  tags TEXT[], -- array of tags
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create pregnancy_measurements table
CREATE TABLE pregnancy_measurements (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  pregnancy_id UUID REFERENCES pregnancies(id) ON DELETE CASCADE NOT NULL,
  measurement_date DATE NOT NULL,
  measurement_type TEXT NOT NULL, -- 'weight', 'blood_pressure', 'baby_size', etc.
  value NUMERIC,
  unit TEXT,
  notes TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on all tables
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE pregnancies ENABLE ROW LEVEL SECURITY;
ALTER TABLE pregnancy_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE pregnancy_measurements ENABLE ROW LEVEL SECURITY;

-- Create RLS policies
-- Profiles: Users can only see and edit their own profile
CREATE POLICY "Users can view their own profile" ON profiles
  FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update their own profile" ON profiles
  FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can insert their own profile" ON profiles
  FOR INSERT WITH CHECK (auth.uid() = id);

-- Pregnancies: Users can only see and edit their own pregnancies
CREATE POLICY "Users can view their own pregnancies" ON pregnancies
  FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can insert their own pregnancies" ON pregnancies
  FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update their own pregnancies" ON pregnancies
  FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete their own pregnancies" ON pregnancies
  FOR DELETE USING (auth.uid() = user_id);

-- Pregnancy logs: Users can only access logs for their own pregnancies
CREATE POLICY "Users can view their own pregnancy logs" ON pregnancy_logs
  FOR SELECT USING (
    auth.uid() IN (
      SELECT user_id FROM pregnancies WHERE id = pregnancy_logs.pregnancy_id
    )
  );

CREATE POLICY "Users can insert their own pregnancy logs" ON pregnancy_logs
  FOR INSERT WITH CHECK (
    auth.uid() IN (
      SELECT user_id FROM pregnancies WHERE id = pregnancy_logs.pregnancy_id
    )
  );

CREATE POLICY "Users can update their own pregnancy logs" ON pregnancy_logs
  FOR UPDATE USING (
    auth.uid() IN (
      SELECT user_id FROM pregnancies WHERE id = pregnancy_logs.pregnancy_id
    )
  );

CREATE POLICY "Users can delete their own pregnancy logs" ON pregnancy_logs
  FOR DELETE USING (
    auth.uid() IN (
      SELECT user_id FROM pregnancies WHERE id = pregnancy_logs.pregnancy_id
    )
  );

-- Pregnancy measurements: Users can only access measurements for their own pregnancies
CREATE POLICY "Users can view their own pregnancy measurements" ON pregnancy_measurements
  FOR SELECT USING (
    auth.uid() IN (
      SELECT user_id FROM pregnancies WHERE id = pregnancy_measurements.pregnancy_id
    )
  );

CREATE POLICY "Users can insert their own pregnancy measurements" ON pregnancy_measurements
  FOR INSERT WITH CHECK (
    auth.uid() IN (
      SELECT user_id FROM pregnancies WHERE id = pregnancy_measurements.pregnancy_id
    )
  );

CREATE POLICY "Users can update their own pregnancy measurements" ON pregnancy_measurements
  FOR UPDATE USING (
    auth.uid() IN (
      SELECT user_id FROM pregnancies WHERE id = pregnancy_measurements.pregnancy_id
    )
  );

CREATE POLICY "Users can delete their own pregnancy measurements" ON pregnancy_measurements
  FOR DELETE USING (
    auth.uid() IN (
      SELECT user_id FROM pregnancies WHERE id = pregnancy_measurements.pregnancy_id
    )
  );

-- Create indexes for better performance
CREATE INDEX idx_pregnancies_user_id ON pregnancies(user_id);
CREATE INDEX idx_pregnancy_logs_pregnancy_id ON pregnancy_logs(pregnancy_id);
CREATE INDEX idx_pregnancy_logs_date ON pregnancy_logs(log_date);
CREATE INDEX idx_pregnancy_measurements_pregnancy_id ON pregnancy_measurements(pregnancy_id);
CREATE INDEX idx_pregnancy_measurements_date ON pregnancy_measurements(measurement_date);

-- Create function to automatically create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.profiles (id, email, full_name, avatar_url)
  VALUES (
    NEW.id,
    NEW.email,
    NEW.raw_user_meta_data->>'full_name',
    NEW.raw_user_meta_data->>'avatar_url'
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger to call the function on user signup
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();
```

## Part 2: Backend Setup (Python/FastAPI)

### 2.1 Install Supabase Dependencies

The Supabase Python client has been added to your backend dependencies. Install it by running:

```bash
cd backend
poetry add supabase
```

### 2.2 Backend Environment Configuration

A `.env` file has been created in your backend directory with the following variables:

```env
# Supabase Configuration
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
SUPABASE_JWT_SECRET=your-jwt-secret-here

# Database Configuration
DATABASE_URL=postgresql://postgres:your-db-password@db.your-project-id.supabase.co:5432/postgres

# Application Configuration
SECRET_KEY=your-secret-key-here
PROJECT_NAME=Preggo API
BACKEND_CORS_ORIGINS=["http://localhost:3000", "https://your-domain.com"]
```

**Replace the placeholder values with your actual Supabase credentials.**

### 2.3 Backend Configuration Update

The backend configuration has been updated to include Supabase settings in `/Users/bernhardczypka/private/preggo/backend/app/core/config.py`.

### 2.4 Supabase Client Setup

A Supabase client module has been created at `/Users/bernhardczypka/private/preggo/backend/app/core/supabase.py` to handle all Supabase interactions.

## Part 3: Frontend Setup (Nuxt.js)

### 3.1 Install Supabase Dependencies

The @nuxtjs/supabase module has been added to your frontend dependencies. Install it by running:

```bash
cd frontend
npm install @nuxtjs/supabase
```

### 3.2 Frontend Environment Configuration

A `.env` file has been created in your frontend directory:

```env
NUXT_PUBLIC_SUPABASE_URL=https://your-project-id.supabase.co
NUXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key-here
NUXT_PUBLIC_API_BASE=http://localhost:8000/api/v1
```

**Replace the placeholder values with your actual Supabase credentials.**

### 3.3 Frontend Configuration Update

The Nuxt configuration has been updated to include the Supabase module and proper runtime configuration.

## Part 4: Development Workflow

### 4.1 Starting the Development Environment

1. Make sure both environment files (backend and frontend) have the correct Supabase credentials
2. Start the development servers:
   ```bash
   make dev
   ```

### 4.2 Testing the Connection

1. Backend: Visit http://localhost:8000/docs to see the API documentation
2. Frontend: Visit http://localhost:3000 to see the application

### 4.3 Database Migrations

Since we're using Supabase, you have two options for database schema management:

1. **Supabase Dashboard (Recommended for initial setup)**: Use the SQL Editor in the Supabase dashboard
2. **Alembic Migrations**: Continue using Alembic for local development and version control

## Part 5: Authentication Integration

### 5.1 Frontend Authentication

With @nuxtjs/supabase, you get automatic authentication composables:

```typescript
// In your Vue components
const supabase = useSupabaseClient()
const user = useSupabaseUser()

// Sign up
const { data, error } = await supabase.auth.signUp({
  email: 'user@example.com',
  password: 'password'
})

// Sign in
const { data, error } = await supabase.auth.signInWithPassword({
  email: 'user@example.com',
  password: 'password'
})

// Sign out
const { error } = await supabase.auth.signOut()
```

### 5.2 Backend Authentication

The backend Supabase client can verify JWT tokens and interact with authenticated users:

```python
from app.core.supabase import supabase

# Verify a user token
def verify_token(token: str):
    user = supabase.auth.get_user(token)
    return user

# Get user data
def get_user_profile(user_id: str):
    response = supabase.table('profiles').select('*').eq('id', user_id).execute()
    return response.data
```

## Part 6: Next Steps

1. **Replace all placeholder values** in the `.env` files with your actual Supabase credentials
2. **Run the SQL schema setup** in your Supabase dashboard
3. **Install the new dependencies** using the commands above
4. **Test the connection** by starting the development servers
5. **Implement authentication flows** in your frontend components
6. **Create API endpoints** that use the Supabase client for data operations

## Part 7: Security Considerations

1. **Never commit `.env` files** to version control
2. **Use Row Level Security (RLS)** policies to protect user data
3. **Validate user permissions** on both frontend and backend
4. **Use the service role key only on the backend** for admin operations
5. **Keep your JWT secret secure** and rotate it periodically

## Part 8: Troubleshooting

### Common Issues

1. **Connection Errors**: Verify your Supabase URL and keys are correct
2. **RLS Policy Errors**: Make sure your RLS policies are properly configured
3. **CORS Issues**: Add your domain to the allowed origins in Supabase settings
4. **Authentication Issues**: Check that your JWT secret matches between backend and Supabase

### Useful Resources

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase Python Client](https://github.com/supabase/supabase-py)
- [@nuxtjs/supabase Documentation](https://supabase.nuxtjs.org/)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)

## Part 9: Development Commands

After setup, you can use these commands:

```bash
# Install all dependencies (including new Supabase ones)
make install

# Start development servers
make dev

# Generate types (after adding new API endpoints)
make generate-types

# View logs
make logs
```

---

This completes the Supabase setup for your pregnancy tracking app. Make sure to follow each step carefully and replace all placeholder values with your actual Supabase credentials.