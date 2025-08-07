# Frontend Dockerfile
FROM node:24
# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application code
COPY . .

# Build the application with environment variables
ARG SUPABASE_URL
ARG SUPABASE_ANON_KEY
ENV SUPABASE_URL=$SUPABASE_URL
ENV SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY
RUN npm run build


# Expose port
EXPOSE 3000

# Start command
CMD ["node", ".output/server/index.mjs"]
