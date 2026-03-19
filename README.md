# SignLingo Microservices Backend

A microservices-based backend architecture for the SignLingo ISL/ASL learning platform.

## Architecture

```
Frontend → SIGN-LINGO-GATEWAY (port 8000)
              ├── /api/v1/auth/*     → Auth Service (5002)
              ├── /api/v1/user/*     → Auth Service (5002)
              ├── /api/v1/convert/*  → Convert Service (5005)
              ├── /api/v1/videos/*   → Content Service (5003)
              ├── /api/v1/alphabet/* → Content Service (5003)
              ├── /api/v1/practice/* → Practice Service (5004)
              └── /api/v1/progress/* → Practice Service (5004)
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| **Gateway** | 8000 | Lightweight FastAPI reverse proxy with JWT validation |
| **Auth** | 5002 | User registration, login, profiles, analytics |
| **Content** | 5003 | Videos, alphabet data, vocabulary |
| **Practice** | 5004 | Practice sessions, progress tracking |
| **Convert** | 5005 | Text-to-sign, speech-to-sign conversion |

## Local Development

### Prerequisites
- Docker & Docker Compose

### Setup
1. Create the shared Docker network:
   ```bash
   docker network create signlingo-mesh
   ```

2. Copy `.env.example` to `.env` in each service directory and fill in your values.

3. Start all services:
   ```bash
   for dir in SIGN-LINGO-AUTH SIGN-LINGO-CONTENT SIGN-LINGO-PRACTICE SIGN-LINGO-CONVERT SIGN-LINGO-GATEWAY; do
     cd $dir && docker compose up -d --build && cd ..
   done
   ```

4. Test the gateway:
   ```bash
   curl http://localhost:8000/health
   ```

## Environment Variables

Each service requires a `.env` file. See `.env.example` in each service directory.

Key variables:
- `MONGO_URI` — MongoDB Atlas connection string
- `JWT_SECRET_KEY` — Shared JWT signing secret
- `AUTH_SERVICE_URL`, `CONTENT_SERVICE_URL`, etc. — Service URLs (Gateway only)
