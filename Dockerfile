# DJN Broker - Production Docker Container
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download NLTK data
RUN python -c "import nltk; nltk.download('vader_lexicon')"

# Copy application code
COPY . .

# Create storage directories
RUN mkdir -p storage/learning

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/Berlin

# Run the trading bot
CMD ["python", "schedule_runner.py"]

