# UniControl Frontend Dockerfile
# ==============================
# Multi-stage build: Build Vue.js app, then serve with Nginx

# ================================
# Stage 1: Build
# ================================
FROM node:20-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --legacy-peer-deps

# Copy source code
COPY . .

# Build production version
# Use relative /api/v1 so requests go through nginx proxy (same-origin, no CORS)
ARG VITE_API_URL=/api/v1
ARG VITE_APP_NAME=UniControl
ENV VITE_API_URL=$VITE_API_URL
ENV VITE_APP_NAME=$VITE_APP_NAME

RUN npm run build

# ================================
# Stage 2: Production with Nginx
# ================================
FROM nginx:alpine

# Copy built files
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD wget -qO- http://localhost/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
