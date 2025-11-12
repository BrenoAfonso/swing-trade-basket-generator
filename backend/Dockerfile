
# Use slim variant of Python 3.10 for smaller base image and faster deployments
FROM python:3.10-slim AS builder

WORKDIR /build

# Install build dependencies required for compiling Python packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first 
# If the dependencies don't change, this layer will not be rebuilt
COPY requirements.txt .

# Create isolated virtual environment to keep runtime dependencies clean
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt


#STAGE 2 - Runtime
# Use the same Python base image
FROM python:3.10-slim

# Make Python print logs directly and avoid creating .pyc files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/opt/venv/bin:$PATH"
   
# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/output && \
    chown -R appuser:appuser /app

# Set the working directory for the application
WORKDIR /app 

# Copy only the virtual environment from builder
COPY --from=builder --chown=appuser:appuser /opt/venv /opt/venv

# Copy application code
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

# Expose port for the FastAPI application
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/', timeout=5)"

# Start uvicorn server with external access enabled
# 0.0.0.0 allows external access from outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
  
