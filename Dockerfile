# Use a lightweight Python version
FROM python:3.10-slim

# 1. Install system dependencies (Poppler is required for PDF handling)
RUN apt-get update && \
    apt-get install -y poppler-utils && \
    rm -rf /var/lib/apt/lists/*

# 2. Set work directory
WORKDIR /app

# 3. Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the code
COPY . .

# 5. Run the app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]