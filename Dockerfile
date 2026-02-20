# ---------- Stage 1: Build frontend ----------
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

COPY frontend/package*.json ./
RUN npm install

COPY frontend .
RUN npm run build


# ---------- Stage 2: Build backend ----------
FROM python:3.11

WORKDIR /app

# Install backend dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn uvicorn

# Copy backend code
COPY backend ./backend

# Copy built frontend output
COPY --from=frontend-builder /app/frontend/.next ./frontend/.next
COPY --from=frontend-builder /app/frontend/public ./frontend/public

EXPOSE 8000

# IMPORTANT FIX HERE ↓↓↓
CMD ["sh", "-c", "gunicorn -k uvicorn.workers.UvicornWorker backend.app.main:app --bind 0.0.0.0:$PORT"]
