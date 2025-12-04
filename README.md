# Test Data Management Platform (TDMP)

A full-stack AI agent chat tool with data pipeline and RAG (Retrieval-Augmented Generation) capabilities for building and managing knowledge bases.

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         TDMP Architecture                            │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌─────────────────┐         ┌──────────────────────────────────┐   │
│  │   Frontend      │         │          Backend                  │   │
│  │   (NextJS)      │ ◄────── │         (FastAPI)                 │   │
│  │                 │         │                                   │   │
│  │  ┌───────────┐  │  HTTP   │  ┌────────────┐  ┌────────────┐  │   │
│  │  │   Chat    │  │ ───────►│  │  Internal  │  │  External  │  │   │
│  │  │ Interface │  │         │  │    API     │  │    API     │  │   │
│  │  └───────────┘  │         │  └─────┬──────┘  └─────┬──────┘  │   │
│  └─────────────────┘         │        │               │         │   │
│                              │        ▼               ▼         │   │
│                              │  ┌────────────────────────────┐  │   │
│                              │  │      LangGraph Agent       │  │   │
│                              │  │  (AI Chat with RAG)        │  │   │
│                              │  └─────────────┬──────────────┘  │   │
│                              │                │                 │   │
│                              │        ┌───────┴────────┐        │   │
│                              │        ▼                ▼        │   │
│                              │  ┌──────────┐    ┌───────────┐   │   │
│                              │  │  Chroma  │    │   Event   │   │   │
│                              │  │ Vector DB│    │  Pipeline │   │   │
│                              │  └──────────┘    └───────────┘   │   │
│                              └──────────────────────────────────┘   │
│                                                                      │
└─────────────────────────────────────────────────────────────────────┘
```

## Features

### Frontend (NextJS)
- Modern React-based chat interface
- Real-time messaging with AI agent
- Source document display from RAG responses
- Dark mode support
- TypeScript for type safety

### Backend (FastAPI + LangGraph)
- **AI Agent**: LangGraph-powered conversational AI
- **RAG System**: Chroma vector database for semantic search
- **Internal API**: Endpoints for the frontend chat tool
- **External API**: 3rd party integration endpoints
- **Event Pipeline**: Async event processing system

## Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`
- Swagger docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### Internal API (for Chat Tool)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/internal/chat` | Send a chat message |
| POST | `/api/v1/internal/knowledge/documents` | Add a document |
| POST | `/api/v1/internal/knowledge/query` | Query knowledge base |
| GET | `/api/v1/internal/knowledge/documents/{id}` | Get document by ID |
| DELETE | `/api/v1/internal/knowledge/documents/{id}` | Delete a document |
| GET | `/api/v1/internal/knowledge/stats` | Get knowledge base stats |

### External API (for 3rd Party Integration)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/external/data/ingest` | Ingest external data |
| POST | `/api/v1/external/events` | Publish an event |
| GET | `/api/v1/external/events/{id}` | Get event status |
| POST | `/api/v1/external/documents/bulk` | Bulk import documents |
| GET | `/api/v1/external/pipeline/stats` | Get pipeline stats |
| POST | `/api/v1/external/webhook` | Webhook handler |

## Environment Variables

### Backend

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | - | OpenAI API key for LLM |
| `OPENAI_MODEL` | gpt-4o-mini | OpenAI model to use |
| `CHROMA_PERSIST_DIRECTORY` | ./chroma_data | Chroma DB storage path |
| `CHROMA_COLLECTION_NAME` | knowledge_base | Chroma collection name |
| `REDIS_URL` | redis://localhost:6379/0 | Redis URL for event pipeline |
| `CORS_ORIGINS` | ["http://localhost:3000"] | Allowed CORS origins |

### Frontend

| Variable | Default | Description |
|----------|---------|-------------|
| `NEXT_PUBLIC_API_URL` | http://localhost:8000 | Backend API URL |

## Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v
```

### Frontend Tests

```bash
cd frontend
npm run test
```

## Project Structure

```
tdmp/
├── backend/
│   ├── app/
│   │   ├── api/           # API endpoints
│   │   │   ├── internal.py  # Internal API for chat tool
│   │   │   └── external.py  # External API for integrations
│   │   ├── agents/        # LangGraph AI agents
│   │   │   └── chat_agent.py
│   │   ├── core/          # Core configuration
│   │   │   └── config.py
│   │   ├── models/        # Database models
│   │   ├── pipeline/      # Event pipeline
│   │   │   └── events.py
│   │   ├── rag/           # RAG with Chroma
│   │   │   └── service.py
│   │   ├── schemas/       # Pydantic schemas
│   │   │   └── api.py
│   │   └── main.py        # FastAPI app entry
│   ├── tests/             # Backend tests
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/           # Next.js app router
│   │   ├── components/    # React components
│   │   │   └── ChatInterface.tsx
│   │   ├── lib/           # Utility functions
│   │   │   └── api.ts
│   │   └── types/         # TypeScript types
│   │       └── api.ts
│   ├── package.json
│   └── tsconfig.json
└── README.md
```

## License

MIT License - see [LICENSE](LICENSE) for details.

