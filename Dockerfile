# Start with the official Azure App Service base image for Python 3.12
FROM mcr.microsoft.com/appsvc/python:3.12-slim

# Install system dependencies required by titiler/rasterio, especially GDAL
RUN apt-get update && apt-get install -y \
    libgdal-dev \
    gdal-bin \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables for GDAL
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Copy your application's requirements file
COPY requirements.txt /

# Install Python packages, including titiler and its dependencies
# Use --no-binary to ensure rasterio is built correctly
RUN pip install --no-cache-dir -r /requirements.txt --no-binary rasterio

# Copy the rest of your application code into the container
COPY . /home/site/wwwroot

# Set working directory
WORKDIR /home/site/wwwroot

# Start the FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]