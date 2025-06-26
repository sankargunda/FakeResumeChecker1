# Use Python 3.10.14
FROM python:3.10.14-slim

# Set working directory
WORKDIR /app

# Install required system dependencies (if needed)
RUN apt-get update && apt-get install -y \
    build-essential \
    poppler-utils \
    libmagic1 \
    tesseract-ocr \
    unrtf \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 10000

# Run the app
CMD ["streamlit", "run", "main.py", "--server.port=10000", "--server.enableCORS=false"]
