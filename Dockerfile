# ─────────────────────────────────────────────────────────────
# Backend Dockerfile — Project Synergy
# Runs the FastAPI + Uvicorn server on port 8000
# Works on any local device: macOS (Intel/Apple Silicon), Linux, Windows
# ─────────────────────────────────────────────────────────────

# Step 1: Use official Python 3.11 slim image as the base
# Force linux/amd64 platform — required because ibm_db only has
# pre-built binaries for x86_64 (not ARM/aarch64 Mac Silicon)
FROM --platform=linux/amd64 python:3.11-slim

# Step 2: Install system-level dependencies required by ibm_db
# ibm_db needs C build tools, IBM DB2 client libraries, and curl/tar to download clidriver
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libxml2 \
    curl \
    tar \
    && rm -rf /var/lib/apt/lists/*

# Step 3: Download and install IBM DB2 ODBC CLI driver (clidriver)
# ibm_db Python package requires this to compile and run on any machine.
# This is the official IBM-hosted x86_64 Linux driver — works inside the
# linux/amd64 container regardless of the host OS (macOS, Linux, Windows).
RUN curl -fsSL https://public.dhe.ibm.com/ibmdl/export/pub/software/data/db2/drivers/odbc_cli/linuxx64_odbc_cli.tar.gz \
    -o /tmp/clidriver.tar.gz && \
    mkdir -p /opt/ibm && \
    tar -xzf /tmp/clidriver.tar.gz -C /opt/ibm && \
    rm /tmp/clidriver.tar.gz

# Step 4: Set environment variables so ibm_db can find the clidriver at build and runtime
ENV IBM_DB_HOME=/opt/ibm/clidriver
ENV LD_LIBRARY_PATH=/opt/ibm/clidriver/lib:$LD_LIBRARY_PATH

# Step 5: Set the working directory inside the container
WORKDIR /app

# Step 6: Copy requirements file first (for better layer caching)
# If requirements.txt hasn't changed, Docker/Podman won't re-run pip install
COPY requirements.txt .

# Step 7: Install Python dependencies
# ibm_db will now compile successfully using the clidriver installed above
RUN pip install --no-cache-dir -r requirements.txt

# Step 8: Copy the backend source code folders
# api/      → FastAPI server (main.py)
# scripts/  → Helper modules (data_mapper.py, clone_oracle_schema.py, etc.)
# database/ → Config files and SQL schemas (table_mappings.json, etc.)
COPY api/ ./api/
COPY scripts/ ./scripts/
COPY database/ ./database/

# Step 9: Expose port 8000 (same as local dev — no confusion)
EXPOSE 8000

# Step 10: Start the FastAPI server with Uvicorn
# host 0.0.0.0 → listen on all interfaces so the container is reachable from outside
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]