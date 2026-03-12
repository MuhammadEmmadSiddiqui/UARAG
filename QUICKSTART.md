# Quick Start Guide

## ✅ Application is Ready!

Your UARAG (Uncertainty Aware Retrieval Augmented Generation) system is now fully set up and running!

### 🚀 Access the Application

**Streamlit Frontend:** [http://localhost:8501](http://localhost:8501)
**FastAPI Backend:** [http://localhost:8000](http://localhost:8000)
**API Documentation:** [http://localhost:8000/docs](http://localhost:8000/docs)

### 📝 How to Use

1. **Open your browser** and navigate to http://localhost:8501
2. **Register a new account** using the Register tab
3. **Login** with your credentials
4. **Start chatting** with the AI assistant!

### 🎯 Features Implemented

✅ **Streaming Responses** - Real-time streaming from Groq LLM  
✅ **Authentication** - OAuth2 + JWT + Bearer token security  
✅ **Database** - SQLite for user and conversation storage  
✅ **Middleware** - CORS, logging, and rate limiting  
✅ **Testing** - 18 unit tests with dependency injection  
✅ **UV Package Manager** - Fast dependency management  
✅ **LangChain + Groq** - Using llama-3.1-8b-instant model  

### 🛠️ Development Commands

```powershell
# Start backend (already running)
.\run_backend.ps1

# Start frontend (already running)
.\run_frontend.ps1

# Run tests
.\run_tests.ps1

# Initialize database
.\init_db.ps1

# Install/update dependencies
uv sync
```

### 📂 Project Structure

```
UARAG/
├── backend/
│   ├── main.py              # FastAPI app
│   ├── auth.py              # Authentication
│   ├── chat.py              # Chat endpoints with streaming
│   ├── database.py          # Database setup
│   ├── models.py            # SQLAlchemy models
│   ├── schemas.py           # Pydantic schemas
│   ├── middleware.py        # Custom middleware
│   ├── config.py            # Settings
│   └── dependencies.py      # Dependency injection
├── frontend/
│   └── app.py               # Streamlit UI
├── tests/
│   ├── conftest.py          # Test fixtures
│   ├── test_auth.py         # Auth tests
│   └── test_chat.py         # Chat tests
├── pyproject.toml           # UV config
├── .env                     # Environment variables
└── README.md                # Full documentation
```

### 🔑 API Endpoints

- `POST /auth/register` - Register new user
- `POST /auth/token` - Get access token
- `POST /chat/stream` - Stream chat responses (authenticated)
- `GET /chat/history` - Get conversation history (authenticated)
- `GET /chat/conversation/{id}` - Get specific conversation (authenticated)
- `GET /health` - Health check
- `GET /` - API info

### 🔒 Security Features

- Password hashing with bcrypt
- JWT token-based authentication
- Bearer token authorization
- CORS middleware
- Rate limiting (100 requests/minute per IP)
- Request logging

### 🧪 Testing

All 18 tests pass successfully:
- 10 authentication tests
- 8 chat/API tests

Run tests with:
```powershell
uv run pytest tests/ -v --cov=backend
```

### 🎨 Streamlit Features

- Login/Register interface
- Real-time streaming chat
- Conversation management
- New conversation button
- User authentication state
- Responsive UI

### 💡 Tips

1. **Register First**: Create an account before using the chatbot
2. **New Conversation**: Use the sidebar button to start fresh
3. **API Docs**: Check http://localhost:8000/docs for interactive API docs
4. **Environment**: Check .env file for configuration

### 🔧 Troubleshooting

If the application doesn't load:
1. Check that both servers are running
2. Verify ports 8000 and 8501 are available
3. Check the terminal output for errors
4. Ensure .env file has the correct Groq API key

### 📚 Technology Stack

- **Backend**: FastAPI, SQLAlchemy, LangChain, Groq
- **Frontend**: Streamlit
- **Database**: SQLite with async support
- **Auth**: OAuth2, JWT, Passlib/Bcrypt
- **Testing**: Pytest, pytest-asyncio
- **Package Manager**: UV

Enjoy your AI assistant! 🎉
