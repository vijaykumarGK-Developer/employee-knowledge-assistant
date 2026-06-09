# Employee Knowledge Assistant

> AI-powered internal knowledge base that helps employees find information from company documents using natural language questions.

![Dashboard](screenshots/chat.png)

## Features

| Feature | Description |
|---------|-------------|
| **Document Management** | Upload PDF, DOCX, TXT, and CSV files. Auto-indexed for search. |
| **Smart Q&A** | Ask natural language questions — get answers extracted from your documents with source citations. |
| **Department Access Control** | Documents tagged by department (HR, Engineering, Finance). Users only see relevant docs. |
| **Analytics Dashboard** | Track popular questions, unanswered queries, and user activity. |
| **Admin Panel** | Manage documents, users, and view analytics. |
| **REST API** | Full OpenAPI documentation at `/docs`. |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Backend** | Python 3.12+, FastAPI, SQLAlchemy, Alembic |
| **Frontend** | Next.js 16, React 19, TypeScript, Tailwind CSS v4 |
| **Vector Store** | ChromaDB (cosine similarity search) |
| **Database** | PostgreSQL 15 (production) / SQLite (development) |
| **Embeddings** | Sentence-Transformers (`all-MiniLM-L6-v2`, 384-dim) |
| **Answer Generation** | Extractive (no LLM API needed — 100% local) |
| **Infrastructure** | Docker, Docker Compose, Nginx |

## Architecture

```
User → Browser → Nginx (:80)
                    ├── /api/* → FastAPI Backend (:8000)
                    │               ├── PostgreSQL (user data, chats)
                    │               └── ChromaDB (document vectors)
                    └── /* → Next.js Frontend (:3000)
```

## Quick Start (Local Development)

### Prerequisites
- Python 3.12+
- Node.js 22+
- npm

### 1. Backend

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate      # Windows
# source venv/bin/activate   # Linux/Mac
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API available at `http://localhost:8000` — Docs at `http://localhost:8000/docs`

### 2. Frontend

```bash
cd frontend
npm install
npm run dev
```

App available at `http://localhost:3000`

### 3. Seed Demo Data (optional)

```bash
cd backend
.\venv\Scripts\activate
python scripts/seed.py
```

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@company.com | admin123 |
| HR | hr@company.com | hr123456 |
| Engineer | engineer@company.com | eng12345 |

## Docker Deployment

```bash
# Start all services
docker compose up --build -d

# Verify
docker compose ps
curl http://localhost/api/health
```

| Service | URL |
|---------|-----|
| App | http://localhost |
| API | http://localhost/api |
| Docs | http://localhost/api/docs |

## Screenshots

| Page | Preview |
|------|---------|
| Login | ![Login](screenshots/login.png) |
| Chat Interface | ![Chat](screenshots/chat.png) |
| Admin Documents | ![Documents](screenshots/admin-documents.png) |
| Admin Analytics | ![Analytics](screenshots/admin-analytics.png) |
| API Documentation | ![API Docs](screenshots/api-docs.png) |

## API Overview

### Authentication
- `POST /api/auth/register` — Create account
- `POST /api/auth/login` — Login, returns JWT token
- `GET /api/auth/me` — Get current user info

### Documents
- `POST /api/documents/upload` — Upload document (admin)
- `GET /api/documents/` — List documents
- `GET /api/documents/:id` — Get document details
- `DELETE /api/documents/:id` — Soft delete (admin)
- `POST /api/documents/:id/reprocess` — Reprocess document

### Chats
- `POST /api/chats/` — Create new chat
- `GET /api/chats/` — List user's chats
- `GET /api/chats/:id` — Get chat with messages
- `POST /api/chats/:id/messages` — Send message, get answer
- `POST /api/chats/messages/:id/feedback` — Submit thumbs up/down
- `DELETE /api/chats/:id` — Delete chat

### Analytics (admin only)
- `GET /api/analytics/overview` — Dashboard stats
- `GET /api/analytics/popular-questions` — Top asked questions
- `GET /api/analytics/user-activity` — Daily active users
- `GET /api/analytics/unanswered` — Questions with no answer

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/           # Route handlers
│   │   ├── core/          # Config, security, database
│   │   ├── models/        # SQLAlchemy models
│   │   ├── schemas/       # Pydantic schemas
│   │   ├── services/      # Business logic
│   │   │   ├── extractors/   # PDF, DOCX, TXT, CSV text extraction
│   │   │   ├── chunker.py    # Text splitting
│   │   │   ├── embeddings.py # Vector embeddings
│   │   │   ├── vector_store.py # ChromaDB operations
│   │   │   └── rag_pipeline.py # Q&A orchestration
│   │   └── utils/         # File handling utilities
│   ├── scripts/           # Database seeding
│   ├── tests/             # Pytest test suite
│   └── alembic/           # Database migrations
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js App Router pages
│   │   ├── components/    # Reusable UI components
│   │   └── lib/           # API client, auth context
│   └── Dockerfile
├── docker/
│   └── nginx.conf         # Reverse proxy config
├── sample-docs/           # Demo documents
├── scripts/               # Deployment utilities
└── screenshots/           # README screenshots
```

## Configuration

Environment variables (copy `.env.example` to `.env`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/employee_knowledge` | Database connection |
| `SECRET_KEY` | `change-this-secret-key-in-production` | JWT signing key |
| `EMBEDDINGS_MODEL` | `sentence-transformers/all-MiniLM-L6-v2` | Embedding model |
| `CORS_ORIGINS` | `http://localhost:3000` | Allowed origins |

## Testing

```bash
cd backend
.\venv\Scripts\activate
pytest -v

# With coverage
pytest --cov=app tests/ --cov-report=term-missing
```

## License

[MIT](LICENSE)

## Contributors

- [Vijay Kumar GK](https://github.com/vijaykumarGK-Developer)
- [Kavya NR](https://github.com/nrkavya5-developer)
