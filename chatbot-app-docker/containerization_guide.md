# 🚀 Converting a FastAPI Backend into a Docker Container

This guide walks through the **step-by-step process** of containerizing a FastAPI backend application and highlights important **best practices (Do’s & Don’ts)**.

---

# 📌 1. Prerequisites

Before starting, ensure:

* Docker is installed
* FastAPI project is working locally
* You can run:

  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port 8000
  ```

---

# 📁 2. Project Structure

Your backend project should look like:

```
backend/
│
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schema.py
│
├── requirements.txt
├── .env
├── Dockerfile
├── .dockerignore
```

---

# 📦 3. Create `requirements.txt`

Freeze dependencies:

```bash
pip freeze > requirements.txt
```

Example:

```
fastapi
uvicorn
python-dotenv
openai
psycopg2-binary
prometheus-client
```

---

# 🐳 4. Create Dockerfile

Create a file named `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Start FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

# 🚫 5. Create `.dockerignore`

Prevent unnecessary files from going into the image:

```
__pycache__/
*.pyc
venv/
.env
.git
```

---

# 🔐 6. Environment Variables

Do NOT hardcode secrets.

Use `.env`:

```
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-4.1-mini
CORS_ORIGINS=*
DB_HOST=postgres
DB_USER=appuser
DB_PASSWORD=apppassword
DB_NAME=appdb
```

---

# 🏗️ 7. Build Docker Image

Run:

```bash
docker build -t fastapi-backend .
```

---

# ▶️ 8. Run Container

```bash
docker run -d \
  -p 8000:8000 \
  --env-file .env \
  fastapi-backend
```

---

# 🌐 9. Test Application

Check endpoints:

* Health:

  ```
  http://localhost:8000/health
  ```

* Metrics:

  ```
  http://localhost:8000/metrics
  ```

* Chat API:

  ```
  POST /chat
  ```

---

# 🧠 10. What Happens Internally

* Docker builds an image using your Dockerfile
* Dependencies are installed inside the container
* FastAPI app runs via Uvicorn
* App is exposed on port `8000`

---

# ✅ DO’s (Best Practices)

### 🔹 1. Use Slim Images

* Prefer:

  ```
  python:3.11-slim
  ```
* Reduces image size

---

### 🔹 2. Use Layer Caching

* Copy `requirements.txt` first
* Avoid reinstalling dependencies every build

---

### 🔹 3. Use Environment Variables

* Keep secrets outside code
* Use `.env` or Docker secrets

---

### 🔹 4. Expose Only Required Ports

* Avoid unnecessary exposure

---

### 🔹 5. Keep Image Lightweight

* Remove unnecessary packages
* Use:

  ```
  --no-cache-dir
  ```

---

### 🔹 6. Use Logs via STDOUT

* Important for monitoring tools like Prometheus / Grafana / Loki

---

# ❌ DON’Ts (Common Mistakes)

### ❌ 1. Do NOT Hardcode Secrets

Bad:

```python
OPENAI_API_KEY = "xyz"
```

---

### ❌ 2. Do NOT Use Root User in Production

(Default Docker runs as root)

---

### ❌ 3. Do NOT Install Unnecessary Packages

Avoid bloated images

---

### ❌ 4. Do NOT Use `latest` Tag Blindly

Always specify versions for reproducibility

---

### ❌ 5. Do NOT Use `--reload` in Production

This is only for development

---

---
