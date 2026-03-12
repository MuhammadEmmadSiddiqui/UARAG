# UARAG - Uncertainty Aware Retrieval Augmented Generation

A production-ready chatbot built with Streamlit frontend and FastAPI backend, featuring OAuth2 authentication, streaming responses, and LangChain integration with Groq LLM.

## Features

- 🔐 **Authentication & Authorization**: OAuth2 + JWT + Bearer token
- 💬 **Streaming Responses**: Real-time response streaming from LLM
- 🤖 **LangChain Integration**: Using Groq API with llama-3.1-8b-instant
- 🗄️ **SQLite Database**: User and conversation storage
- 🔧 **Middleware**: CORS, logging, and rate limiting
- ✅ **Unit Testing**: Comprehensive tests with dependency injection
- 📦 **UV Package Manager**: Fast dependency management

## Project Structure

```
.
├── backend/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration settings
│   ├── database.py          # Database setup
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── auth.py              # Authentication logic
│   ├── chat.py              # Chat endpoints
│   ├── middleware.py        # Custom middleware
│   └── dependencies.py      # Dependency injection
├── frontend/
│   └── app.py               # Streamlit application
├── tests/
│   ├── __init__.py
│   ├── conftest.py          # Test fixtures
│   ├── test_auth.py         # Authentication tests
│   └── test_chat.py         # Chat tests
├── pyproject.toml           # UV configuration
├── .env                     # Environment variables
└── README.md

```

## Setup

### Prerequisites

- Python 3.10+
- UV package manager

### Installation

1. Install UV (if not already installed):
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone and setup the project:
```bash
cd "c:\Experiments\UARAG"
uv sync
```

3. Initialize the database:
```bash
uv run python -c "from backend.database import init_db; import asyncio; asyncio.run(init_db())"
```

## Running the Application

### Start the FastAPI Backend

```bash
uv run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Start the Streamlit Frontend

```bash
uv run streamlit run frontend/app.py --server.port 8501
```

### Access the Application

- **Streamlit UI**: http://localhost:8501
- **FastAPI Docs**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health

## Testing

Run all tests:
```bash
uv run pytest
```

Run with coverage:
```bash
uv run pytest --cov=backend --cov-report=html
```

## API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/token` - Get access token

### Chat
- `POST /chat/stream` - Stream chat responses (requires authentication)
- `GET /chat/history` - Get chat history (requires authentication)

## Default Credentials

For testing purposes, you can register a new user via the API or Streamlit interface.

## Environment Variables

See `.env.example` for all available configuration options.

## Security Notes

- Change the `SECRET_KEY` in production
- Use HTTPS in production
- Set appropriate CORS origins
- Implement rate limiting for production use

## License

MIT
