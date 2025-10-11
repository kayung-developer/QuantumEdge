# --- Stage 1: Build Stage ---
# This stage's only purpose is to gather and install all Python dependencies.
FROM python:3.11-slim as builder

WORKDIR /usr/src/app

# Set environment variables for a clean and efficient build
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR=off

# Install system-level build dependencies, including git for installing from git repos if needed
RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev git

# Copy the requirements file to leverage Docker's layer caching
COPY requirements.txt .

# Install all Python packages into a dedicated target directory.
# This single, unified command allows pip's dependency resolver to create a consistent
# set of packages, using the PyTorch CPU index as a priority.
RUN pip install \
    --target=/usr/src/app/packages \
    --index-url https://download.pytorch.org/whl/cpu \
    --extra-index-url https://pypi.org/simple \
    -r requirements.txt

# --- Stage 2: Final Production Stage ---
# This stage builds the final, minimal image for deployment.

# --- Stage 2: Final Production Stage ---
FROM python:3.11-slim

WORKDIR /app

# Install only the necessary runtime dependencies.
# We REMOVED netcat-openbsd as it's no longer needed.
RUN apt-get update && apt-get install -y --no-install-recommends supervisor libpq5 && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN addgroup --system app && adduser --system --group app

# Copy pre-installed Python packages from the builder stage
COPY --from=builder /usr/src/app/packages /usr/local/lib/python3.11/site-packages

# Copy the application source code
COPY . /app

# Copy the supervisord configuration file
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# --- NEW: Make our wait script executable ---
RUN chmod +x /app/scripts/wait_for_postgres.py

# Change ownership
RUN chown -R app:app /app

# Switch to the non-root user
USER app

# Command to start supervisord
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
