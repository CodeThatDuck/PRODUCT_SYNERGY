# ─────────────────────────────────────────────
# Frontend Dockerfile — Project Synergy
# Runs the React + Vite dev server on port 3000
# ─────────────────────────────────────────────

# Step 1: Use official Node.js image as the base
FROM node:20-alpine

# Step 2: Set the working directory inside the container
WORKDIR /app

# Step 3: Copy package files first (for better layer caching)
# If package.json hasn't changed, Docker won't re-run npm install
COPY package.json package-lock.json ./

# Step 4: Install all Node.js dependencies
RUN npm install

# Step 5: Copy the rest of the frontend source code
COPY . .

# Step 6: Expose port 3000 (same as local dev — no confusion)
EXPOSE 3000

# Step 7: Start the Vite dev server
# host 0.0.0.0 is set in vite.config.js so the container is reachable from outside
CMD ["npm", "run", "dev"]