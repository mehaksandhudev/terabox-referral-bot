FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Set up working directory
WORKDIR /app

# Copy dependency requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code
COPY . .

# Set up Hugging Face non-root user permissions
ENV PORT=7860
ENV HOME=/app
RUN chmod -R 777 /app

# Run start script
CMD ["sh", "start.sh"]
