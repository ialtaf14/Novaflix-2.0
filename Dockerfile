# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Run backend
FROM python:3.12-slim
WORKDIR /app

# Copy backend requirements and install them
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r ./backend/requirements.txt

# Copy backend source files
COPY backend/ ./backend

# Copy static frontend files built in stage 1
COPY --from=frontend-builder /app/frontend/dist ./backend/dist

# Copy other database and static data files
COPY Files/ ./Files
COPY users.json chats.json sessions.json notifications.json activity.json ./

# Cloud Run defines PORT env var. Uvicorn will listen on 8080 by default.
EXPOSE 8080

WORKDIR /app/backend
CMD ["python", "-m", "uvicorn", "main:application", "--host", "0.0.0.0", "--port", "8080"]
