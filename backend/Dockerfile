
#  3.10-slim chosen for its smaller size and suitability for production
FROM python:3.10-slim 

# Make Python print logs directly and avoid creating .pyc files
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1
    
# Set the working directory for the application
WORKDIR / app 

# Copy requirements first 
# If the dependencies don't change, this layer will not be rebuilt
COPY requirements.txt .


# Upgrade pip and install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code into the container
COPY . . 

# Expose port 8000 for the FastAPI application
EXPOSE 8000

# Start uvicorn server with external access enabled
# 0.0.0.0 allows external access from outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]  
