# Architecture

## System Design

```
┌─────────────┐     ┌─────────────┐
│             │     │             │
│   Browser   │────▶│   Nginx     │
│             │     │   (:80)     │
└─────────────┘     └──────┬──────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
     ┌────────────────┐  ┌──────────────────┐
     │  /api/*        │  │  /*              │
     │  FastAPI       │  │  Next.js         │
     │  (:8000)       │  │  (:3000)         │
     └───────┬────────┘  └──────────────────┘
             │
      ┌──────┼──────┐
      │      │      │
      ▼      ▼      ▼
  ┌──────┐ ┌────┐ ┌────────┐
  │ Post │ │Chro│ │ File   │
  │ greS │ │maDB│ │ System │
  │ QL   │ │    │ │(Uploads│
  └──────┘ └────┘ └────────┘
```

## Data Flow — Question Answering

1. **User asks question** → Frontend sends `POST /api/chats/:id/messages`
2. **Off-topic detection** → RAG pipeline checks if question is company-related
3. **Department detection** → Keywords in question auto-filter to relevant dept
4. **Embedding generation** → Question converted to 384-dim vector
5. **Vector search** → ChromaDB finds top-3 most similar document chunks
6. **Answer construction** → Top chunks grouped by document title, returned as answer
7. **Response** → Frontend displays answer to user

## Data Flow — Document Upload

1. **Admin uploads file** → `POST /api/documents/upload`
2. **File validation** → Type check (PDF/DOCX/TXT/CSV), size check (< 50MB)
3. **File storage** → Saved to `uploads/` directory, DB record created
4. **Text extraction** → Extractor factory selects parser based on file type
5. **Chunking** → Text split into 512-char chunks with 50-char overlap
6. **Embedding** → Each chunk converted to vector embedding
7. **Vector storage** → Chunks + embeddings stored in ChromaDB

## Directory Layout

```
backend/
├── app/
│   ├── api/          # FastAPI route handlers (auth, docs, chats, analytics)
│   ├── core/         # Config (pydantic-settings), security (JWT + bcrypt), database (SQLAlchemy)
│   ├── models/       # SQLAlchemy ORM models
│   ├── schemas/      # Pydantic request/response schemas
│   ├── services/     # Business logic layer
│   │   ├── extractors/   # File-specific text parsers
│   │   ├── chunker.py    # RecursiveCharacterTextSplitter
│   │   ├── embeddings.py # SentenceTransformer wrapper
│   │   ├── vector_store.py # ChromaDB CRUD operations
│   │   ├── rag_pipeline.py # Orchestration + off-topic dept detection
│   │   └── llm_service.py # Extractive answer builder
│   └── utils/        # File handler (validation, sanitization)
├── scripts/          # Database seed utility
├── tests/            # 34 pytest tests across 5 test files
└── alembic/          # Migration versions
```

## Key Design Decisions

### 1. Extractive over Generative
No LLM API is used. Answers are built by extracting and grouping relevant text chunks from documents. This eliminates hallucination, requires no API keys, and runs entirely offline.

### 2. SQLite for Development
The `@compiles(JSONB, "sqlite")` decorator enables SQLite compatibility for local dev while the production stack uses PostgreSQL.

### 3. Department-Level Access
Documents are tagged with a department. Users only see documents from their department plus "all" department. Question keywords can auto-detect department relevance.

### 4. Off-Topic Detection
Questions about weather, sports, movies, etc. are detected via keyword matching and politely redirected to company-related queries.
