# frontend/Dockerfile

# --- Stage 1: Build Stage ---
# Use a specific Node.js version for reproducibility
FROM node:18-alpine AS build

# Set the working directory
WORKDIR /app

# Copy package.json and package-lock.json to leverage Docker cache
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Set the API URL for the build
# This environment variable will be baked into the static files.
ARG REACT_APP_API_BASE_URL=/api/v1
ENV REACT_APP_API_BASE_URL=$REACT_APP_API_BASE_URL

# Build the application for production
RUN npm run build

# --- Stage 2: Production Stage ---
# Use a lightweight Nginx image to serve the static files
FROM nginx:1.25-alpine

# Copy the built static files from the build stage to the Nginx html directory
COPY --from=build /app/build /usr/share/nginx/html

# Copy the custom Nginx configuration file
# This will be created next
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80 for Nginx
EXPOSE 80

# The default command for the nginx image is to start the server.
CMD ["nginx", "-g", "daemon off;"]