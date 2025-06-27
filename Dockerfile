# ✅ Use slim Python base
FROM python:3.10-slim

# ✅ Install system dependencies for file handling
RUN apt-get update && apt-get install -y \
    libreoffice \
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

# ✅ Ensure LibreOffice available in PATH
ENV PATH="/usr/lib/libreoffice/program:${PATH}"

# ✅ Disable bytecode + force flush
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# ✅ Set working directory
WORKDIR /app

# ✅ Copy your full project
COPY . .

# ✅ Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ✅ Expose Streamlit default port
EXPOSE 10000

# ✅ Start the Streamlit app
CMD ["streamlit", "run", "main.py", "--server.port=10000", "--server.address=0.0.0.0"]
