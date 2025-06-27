# Use official slim Python image
FROM python:3.10-slim

# Install system dependencies for DOC/DOCX/PDF/text extraction
RUN apt-get update && apt-get install -y \
    libreoffice \
    libreoffice-writer \  # ✅ Speeds up DOC conversion
    unoconv \
    tesseract-ocr \
    poppler-utils \
    build-essential \
    python3-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    antiword \
    libmagic1 \
    curl \
    libglib2.0-0 \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# ✅ Add LibreOffice path explicitly for Render
ENV PATH="/usr/lib/libreoffice/program:${PATH}"

# ✅ Disable bytecode + force console flush
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory inside container
WORKDIR /app

# Copy all project files into container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose Streamlit app port
EXPOSE 10000

# Run Streamlit app on Render or local
CMD ["streamlit", "run", "main.py", "--server.port=10000", "--server.address=0.0.0.0"]
