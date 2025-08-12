## Frontend Dockerfile
#FROM node:24
## Copy package files
#COPY package*.json ./
#
## Install dependencies
#RUN npm ci
#
## Copy application code
#COPY . .
#
## Build the application with environment variables
#ARG SUPABASE_URL
#ARG SUPABASE_ANON_KEY
#ENV SUPABASE_URL=$SUPABASE_URL
#ENV SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY
#RUN npm run build
#
#
## Expose port
#EXPOSE 3000
#
## Start command
#CMD ["node", ".output/server/index.mjs"]


# Use the official Node.js runtime as the base image
FROM node:24-alpine AS base

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json (if available)
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Copy the rest of the application code
COPY . .

# Build the Nuxt application
ARG SUPABASE_URL
ARG SUPABASE_ANON_KEY
ENV SUPABASE_URL=$SUPABASE_URL
ENV SUPABASE_ANON_KEY=$SUPABASE_ANON_KEY
RUN npm run build

# Production stage
FROM node:24-alpine AS production

# Set NODE_ENV to production
ENV NODE_ENV=production

# Create a non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nuxtjs -u 1001

# Set the working directory
WORKDIR /app

# Copy built application from the base stage
COPY --from=base --chown=nuxtjs:nodejs /app/.output ./
COPY --from=base --chown=nuxtjs:nodejs /app/package*.json ./

# Switch to the non-root user
USER nuxtjs

# Expose the port the app runs on
EXPOSE 3000

# Set the default command to run the application
CMD ["node", "server/index.mjs"]
