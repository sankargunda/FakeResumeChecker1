FROM python:3.10-slim

RUN apt-get update && apt-get install -y \
    libreoffice \
    libreoffice-writer \
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

ENV PATH="/usr/lib/libreoffice/program:${PATH}"
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app
COPY . .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 10000

CMD ["streamlit", "run", "main.py", "--server.port=10000", "--server.address=0.0.0.0"]
