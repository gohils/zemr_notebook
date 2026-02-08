# 🐳 Docker Container Development Workflow Quick Guide

This guide covers the **full container-based software development lifecycle (SDLC)** using Docker — from coding to cleanup — for local development, testing, and production preparation.

---

## 1️⃣ Environment Setup

### Prerequisites
- Install Docker Desktop (Windows/macOS) or Docker Engine (Linux)
- Install Python, Node.js, or other language runtimes for app development
- Install VS Code (or preferred IDE)
- Optional: Docker Compose for multi-container apps

### Verification
```bash
docker --version
docker info
docker ps
```

---

## 2️⃣ Project Structure

Typical structure for a FastAPI app:
```
fastapi-eks/
 ├─ main.py
 ├─ requirements.txt
 ├─ Dockerfile
 └─ tests/
```

---

## 3️⃣ Build & Rebuild Docker Images

```bash
# Build image for the first time
docker build -t <image-name>:<tag> .

# Rebuild image from scratch (ignore cache)
docker build --no-cache -t <image-name>:<tag> .

# Tagging for dev/testing vs production
docker build -t fastapi-eks:dev .
docker build -t fastapi-eks:latest .
```

💡 Tip: Use volume mounts for hot-reload during development:
```bash
docker run -p 8000:80 -v ${PWD}:/app fastapi-eks:dev
```

---

## 4️⃣ Running Containers

```bash
# Run container mapping host port to container port
docker run -p 8000:80 <image-name>

# Detached mode (background)
docker run -d -p 8000:80 <image-name>

# Interactive shell for debugging or tests
docker run -it <image-name> bash
```

### Accessing the App
- Localhost mapping: http://localhost:8000 (maps to container port)
- Inside container: use `0.0.0.0` to bind to all interfaces

---

## 5️⃣ Stopping & Removing Containers

```bash
# Stop a running container
docker stop <container-id>

# Remove a container
docker rm <container-id>

# Stop & remove all containers
docker stop $(docker ps -q); docker rm $(docker ps -a -q)
```

---

## 6️⃣ Managing Images

```bash
# List all images
docker images

# Remove a specific image
docker rmi <image-id>

# Force remove image
docker rmi -f <image-id>

# Remove all unused images
docker image prune -a
```

💡 Tip: Use targeted cleanup for development images:
```powershell
docker ps -a --filter "ancestor=fastapi-eks" -q | ForEach-Object { docker stop $_; docker rm $_ }
docker images "fastapi-eks" -q | ForEach-Object { docker rmi $_ }
```

---

## 7️⃣ Unit Testing & Development Cycle

1. Build image: `docker build -t fastapi-eks:dev .`
2. Run container with volume mount: 
```bash
docker run -p 8000:80 -v ${PWD}:/app fastapi-eks:dev
```
3. Run tests inside container:
```bash
docker exec -it <container-id> pytest
```
4. Stop container after tests: `docker stop <container-id>`
5. Repeat for code changes (rebuild if needed)

---

## 8️⃣ Clean-up & Disk Space Management

```bash
# Remove stopped containers and dangling images
docker system prune -a --volumes

# Stop & remove all FastAPI containers and images
docker ps -a --filter "ancestor=fastapi-eks" -q | ForEach-Object { docker stop $_; docker rm $_ }
docker images "fastapi-eks" -q | ForEach-Object { docker rmi $_ }
```

💡 Tip: Regular cleanup avoids memory bloat and keeps disk usage low.

---

## 9️⃣ Full Development Workflow Summary

1. **Code & Develop** → write FastAPI, Node, or Python code
2. **Build Image** → `docker build -t <image>:dev .`
3. **Run Container** → `docker run -p host:container -v ${PWD}:/app <image>`
4. **Unit Test / Debug** → run tests inside container
5. **Rebuild / Re-run** → rebuild image if code/dependencies change
6. **Push to Registry** → `docker tag` + `docker push` (ECR/Docker Hub)
7. **Cleanup** → stop/remove containers, remove unused images & volumes
