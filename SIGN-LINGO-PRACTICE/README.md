# SIGN LINGO Backend

A complete backend for the Indian Sign Language Learning Platform, built with FastAPI, MongoDB, and Cloudinary. This backend powers authentication, user progress, video management, practice, analytics, and conversion features for ISL/ASL learning.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [Configuration](#configuration)
- [Running the App](#running-the-app)
- [API Endpoints](#api-endpoints)
- [Database Schema](#database-schema)
- [Scripts](#scripts)
- [Testing](#testing)
- [Docker & Deployment](#docker--deployment)
- [Legacy & Migration](#legacy--migration)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **FastAPI**: High-performance async API framework
- **MongoDB (Motor)**: Asynchronous database driver
- **JWT Authentication**: Secure login, registration, and role management
- **Cloudinary**: Async image/video uploads
- **Modular Structure**: Clean separation of routes, models, schemas, and services
- **User Progress & Analytics**: XP, streaks, achievements, weekly charts
- **Practice & Learning**: Alphabet, vocabulary, writing, quizzes
- **Conversion**: Text/speech to sign metadata
- **Dockerized**: Easy deployment with Docker & Compose
- **Testing**: Pytest-based async tests

---

## Project Structure

```
├── main.py                # FastAPI app entrypoint
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker build file
├── docker-compose.yml     # Compose for app & MongoDB
├── pytest.ini             # Pytest config
├── api/                   # API routes & dependencies
│   └── v1/endpoints/      # All endpoint modules
├── core/                  # Config & security
├── db/                    # Database connection
├── models/                # Data models
├── schemas/               # Pydantic schemas
├── scripts/               # Utility scripts
├── tests/                 # Test cases
└── ...
```

---

## Setup & Installation

1. **Clone the repository**
     ```bash
     git clone <repo-url>
     cd SIGN-LINGO-BACKEND
     ```

2. **Create a virtual environment**
     ```bash
     python -m venv venv
     venv\Scripts\activate   # On Windows
     source venv/bin/activate # On Linux/Mac
     ```

3. **Install dependencies**
     ```bash
     pip install -r requirements.txt
     ```

---

## Configuration

Create a `.env` file in the root directory:

```env
MONGO_URI=mongodb://localhost:27017
JWT_SECRET_KEY=your_secret_key
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_api_key
CLOUDINARY_API_SECRET=your_api_secret
CORS_ALLOWED_ORIGINS=["http://localhost:3000"]
```

---

## Running the App

Start the server:

```bash
uvicorn main:app --host 0.0.0.0 --port 5002 --reload
```

API available at: [http://localhost:5002](http://localhost:5002)

Interactive docs:
- [Swagger UI](http://localhost:5002/docs)
- [ReDoc](http://localhost:5002/redoc)

---

## API Endpoints

Base URL: `/api/v1`

### Authentication
- `POST /auth/register` — Register new user
- `POST /auth/login` — Login, get JWT token
- `GET /auth/role` — Get current user role

### Users
- `GET /user/profile` — Get profile
- `PUT /user/profile` — Update profile
- `POST /user/profile/picture` — Upload profile picture
- `GET /user/all` — List all users
- `GET /user/progress` — XP, level, streak
- `GET /user/analytics` — Practice stats, accuracy, lessons
- `GET /user/weekly-chart` — 7-day activity
- `GET /user/daily-practice` — Daily recommended signs
- `GET /user/daily-quiz` — Daily quiz

### Progress
- `GET /progress/overview` — Completion, achievements
- `GET /progress/lesson/{lesson_id}` — Lesson state
- `POST /user/progress/chapter` — Mark chapter complete

### Videos
- `GET /videos` — List videos
- `GET /videos/{video_id}` — Video details
- `POST /videos` — Upload video

### Learning
- `GET /alphabet/list` — List A-Z, 0-9
- `GET /alphabet/{character}` — Character details
- `GET /glyphs/{letter}` — Writing glyphs
- `GET /vocabulary/{letter}` — Vocabulary by letter

### Practice
- `POST /practice/submit` — Submit practice
- `GET /practice/score` — Practice scores
- `POST /practice/writing` — Writing practice

### Conversion
- `POST /convert/text-to-sign` — Text to sign
- `POST /convert/speech-to-sign` — Speech to sign

---

## Database Schema

### users
- `_id`: ObjectId
- `username`: String (unique)
- `email`: String (unique)
- `hashed_password`: String
- `role`: String (default: "user")
- `photo_url`: String (optional)
- `created_at`: Date
- `updated_at`: Date

### videos
- `_id`: ObjectId
- `title`: String
- `url`: String
- `duration`: Number (seconds)
- `category`: String ("alphabet", "numbers", etc.)
- `user_id`: String (ref User)
- `is_public`: Boolean

### practice_sessions
- `_id`: ObjectId
- `user_id`: String (ref User)
- `session_type`: String ("writing_practice", etc.)
- `language`: String ("ISL", "ASL")
- `score`: Number
- `completed`: Boolean
- `details`: Object (letter, strokes, etc.)
- `created_at`: Date

### analytics_events
- `_id`: ObjectId
- `user_id`: String
- `event_type`: String
- `event_data`: Object
- `timestamp`: Date

### alphabet
- `character`: String
- `video_id`: String (Cloudinary ID)

### glyphs
- `letter`: String
- `strokes`: Array

---

## Scripts

Located in `scripts/`:

- `check_categories.py` — Validate video categories
- `check_env.py` — Check environment variables
- `check_users.py` — Inspect user data
- `debug_auth.py` — Debug authentication
- `get_ip.py` — Get current IP for MongoDB Atlas
- `initialize_db.py` — Seed initial database
- `inspect_db_structure.py` — Print DB schema
- `inspect_users.py` — Print user info
- `migrate_asl_mapping.py` — Migrate ASL mappings
- `migrate_users.py` — Migrate user data
- `seed_analytics.py` — Seed analytics events
- `seed_user_analytics.py` — Seed user analytics
- `test_cloudinary.py` — Test Cloudinary upload
- `test_common_words.py` — Test common words
- `test_connection.py` — Test DB connection
- `test_endpoints.py` — Test API endpoints
- `test_video_urls.py` — Test video URLs
- `test_words.py` — Test word data
- `upload_asl_videos.py` — Upload ASL videos

---

## Testing

- All tests are in `tests/`.
- Uses `pytest` for async testing.
- Run tests:
    ```bash
    pytest
    ```
- Configured via `pytest.ini`.

---

## Docker & Deployment

### Build & Run with Docker

1. Build the image:
     ```bash
     docker build -t sign-lingo-backend .
     ```
2. Run the container:
     ```bash
     docker run -p 5002:5002 --env-file .env sign-lingo-backend
     ```

### Using Docker Compose

```yaml
services:
    web:
        build: .
        ports:
            - "5002:5002"
        env_file:
            - .env
        volumes:
            - .:/app
        command: uvicorn main:app --host 0.0.0.0 --port 5002 --reload
    mongodb:
        image: mongo:latest
        ports:
            - "27017:27017"
        volumes:
            - mongodb_data:/data/db
volumes:
    mongodb_data:
```

---

## Legacy & Migration

- Migrated from Flask single-file app (`app.py`).
- Legacy files kept for reference.
- All new code is in `api/`, `core/`, `db/`, `models/`, `schemas/`.

---

## Contributing

Pull requests and issues are welcome! Please follow best practices for Python, FastAPI, and MongoDB.

---

## License

MIT License. See [LICENSE](LICENSE) for details.
