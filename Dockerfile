# Use the official TiTiler container as base - it has everything pre-configured
FROM ghcr.io/developmentseed/titiler:latest

# Copy your application code
COPY . /app

# Set working directory
WORKDIR /app

# Install any additional Python dependencies your app needs
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Start your FastAPI application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]