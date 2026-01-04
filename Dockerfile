FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for Playwright (Debian trixie compatible)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    fonts-liberation \
    fonts-unifont \
    libglib2.0-0 \
    libgtk-3-0 \
    libx11-xcb1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers (Chromium only, deps already installed above)
RUN playwright install chromium

# Copy application code
COPY . .

# Make start script executable
RUN chmod +x start.sh

# Default port
ENV PORT=8080

# Run with entrypoint script
ENTRYPOINT ["./start.sh"]
