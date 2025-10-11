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
FROM python:3.11-slim

WORKDIR /app

# Install only the necessary RUNTIME system dependencies.
# 'supervisor' for process management, 'libpq5' for the PostgreSQL client,
# and 'netcat-openbsd' for the database readiness check.
RUN apt-get update && apt-get install -y --no-install-recommends supervisor libpq5 netcat-openbsd && rm -rf /var/lib/apt/lists/*

# Create a non-root user for security best practices
RUN addgroup --system app && adduser --system --group app

# Copy the pre-installed Python packages from the builder stage into the final image.
COPY --from=builder /usr/src/app/packages /usr/local/lib/python3.11/site-packages

# Copy the entire application source code from the build context
COPY . /app

# Copy the supervisord configuration file to its required location
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Set correct ownership for the application directory
RUN chown -R app:app /app

# Switch to the non-root user
USER app

# The command to execute when the container starts.
# This starts the supervisord daemon, which in turn starts our Uvicorn and Celery processes.
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]
