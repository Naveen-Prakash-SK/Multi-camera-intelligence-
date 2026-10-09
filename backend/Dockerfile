FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    ffmpeg \
    libsm6 \
    libxext6 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency management
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# Copy dependency files (Assuming pyproject.toml is moved to /backend if needed, 
# or we use requirements.txt. We'll use uv sync if pyproject is copied)
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
ENV UV_NATIVE_TLS=1
ENV UV_SYSTEM_CERTS=1
ENV UV_HTTP_TIMEOUT=1200
ENV UV_CONCURRENT_DOWNLOADS=4
RUN --mount=type=cache,target=/root/.cache/uv \
    for i in 1 2 3 4 5; do \
      echo "Attempt $i..." && uv sync && break || \
      echo "Attempt $i failed, retrying in 10s..." && sleep 10; \
    done

# Copy the rest of the application code
COPY . .

# Expose API port
EXPOSE 8000

# Run the FastAPI app via uvicorn
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
