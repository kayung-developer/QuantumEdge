# --- Stage 1: Build Stage ---
# This stage creates a virtual environment and installs all dependencies into it.
FROM python:3.11-slim as builder

# Set environment variables for a clean and efficient build
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system-level build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev git

# Create and activate a virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy the requirements file
COPY requirements.txt .

# Install all Python packages into the virtual environment.
# This single, unified command is the most robust way to handle dependencies.
RUN pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    --extra-index-url https://pypi.org/simple \
    -r requirements.txt

# --- Stage 2: Final Production Stage ---
# This stage copies the prepared environment and the application code.
FROM python:3.11-slim

WORKDIR /app

# Install only the necessary RUNTIME system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends supervisor libpq5 netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN addgroup --system app && adduser --system --group app

# --- CRITICAL FIX: Copy the entire virtual environment from the builder stage ---
COPY --from=builder /opt/venv /opt/venv

# Copy the application source code
COPY . /app

# Copy the supervisord configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Make the wait script executable
RUN chmod +x /app/scripts/wait_for_postgres.py

# Set the PATH to include the virtual environment's bin directory
ENV PATH="/opt/venv/bin:$PATH"

# Set ownership
RUN chown -R app:app /app

# Switch to the non-root user
USER app

# Command to start supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
