FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -r botuser && chown -R botuser:botuser /app
USER botuser

# Run bot
CMD ["python", "-m", "bot"]
