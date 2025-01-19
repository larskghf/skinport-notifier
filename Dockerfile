FROM python:3.13-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY main.py .
COPY config.py .

# Create non-root user for security
RUN useradd -m botuser && \
    chown -R botuser:botuser /app
USER botuser

# Run Python in unbuffered mode
ENV PYTHONUNBUFFERED=1

CMD ["python", "-u", "main.py"] 