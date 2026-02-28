# ─────────────────────────────────────────────────────────────
# Backend Dockerfile — Project Synergy
# Runs the FastAPI + Uvicorn server on port 8000
# ─────────────────────────────────────────────────────────────

# Step 1: Use official Python 3.11 slim image as the base
# Force linux/amd64 platform — required because ibm_db only has
# pre-built binaries for x86_64 (not ARM/aarch64 Mac Silicon)
FROM --platform=linux/amd64 python:3.11-slim

# Step 2: Install system-level dependencies required by ibm_db
# ibm_db needs C build tools and IBM DB2 client libraries to compile
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libxml2 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Step 3: Set the working directory inside the container
WORKDIR /app

# Step 4: Copy requirements file first (for better layer caching)
# If requirements.txt hasn't changed, Docker won't re-run pip install
COPY requirements.txt .

# Step 5: Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 6: Copy the backend source code folders
# api/      → FastAPI server (main.py)
# scripts/  → Helper modules (data_mapper.py, clone_oracle_schema.py, etc.)
# database/ → Config files and SQL schemas (table_mappings.json, etc.)
COPY api/ ./api/
COPY scripts/ ./scripts/
COPY database/ ./database/

# Step 7: Expose port 8000 (same as local dev — no confusion)
EXPOSE 8000

# Step 8: Start the FastAPI server with Uvicorn
# host 0.0.0.0 → listen on all interfaces so the container is reachable from outside
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]