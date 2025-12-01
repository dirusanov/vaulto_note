# Vaulto Note Backend

Secure encrypted notes application with AI-powered transcription and text improvement. Supports self-hosted deployment via Docker Compose.

## Features

- 🔒 **Secure Notes**: End-to-end encrypted personal notes
- 🎙️ **Voice Transcription**: Whisper-powered audio-to-text
- ✨ **AI Text Improvement**: LLaMA-based text enhancement
- 🔑 **Dual Authentication**: Email/Password + Crypto Wallet (EVM)
- 🐳 **Easy Deployment**: Single-command Docker Compose setup
- 🏠 **Self-Hosted**: Full control with API key authentication

## Tech Stack

- **FastAPI** - High-performance async API
- **PostgreSQL** - Database with SQLAlchemy 2.0
- **Whisper** - Local speech-to-text
- **Ollama (LLaMA)** - Local LLM for text improvement
- **Docker Compose** - One-command deployment

## Quick Start

### 1. Clone and Configure

```bash
cd vaulto_note
cp .env.example .env
```

Edit `.env` and set your `API_SECRET_KEY`:
```bash
API_SECRET_KEY=your_strong_secret_key_here
```

### 2. Deploy with Docker Compose

```bash
docker-compose up -d
```

This starts:
- Backend API (port 8000)
- PostgreSQL database
- Whisper transcription service
- Ollama LLM service

### 3. Verify

```bash
# Check services
docker-compose ps

# View logs
docker-compose logs -f backend

# Test API
curl http://localhost:8000/docs
```

## API Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Self-Hosted Deployment

### Backend Setup

The backend supports API key authentication for self-hosted deployments:

1. Set `API_SECRET_KEY` in `.env` or via environment variable
2. Run `docker-compose up -d`
3. Use the API key as `Authorization: Bearer <API_SECRET_KEY>`

### Mobile App Configuration

Configure the Vaulto Note mobile app to connect to your server:

1. Open Settings → Self-Hosted Backend
2. Enable "Использовать Self-Hosted"
3. Enter Server URL: `http://YOUR_IP:8000/api/v1`
4. Enter API Secret Key (same as in `.env`)
5. Save settings

## API Examples

### Authentication (Email/Password)

**Register**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "securepassword"}'
```

**Login**:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "securepassword"}'
```

### Notes Management

**Create Note**:
```bash
curl -X POST "http://localhost:8000/api/v1/notes/" \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"title": "My Note", "content": "Encrypted content"}'
```

**List Notes**:
```bash
curl -X GET "http://localhost:8000/api/v1/notes/" \
     -H "Authorization: Bearer <token>"
```

### AI Services

**Transcribe Audio**:
```bash
curl -X POST "http://localhost:8000/api/v1/ai/transcribe" \
     -H "Authorization: Bearer <token>" \
     -F "file=@audio.m4a" \
     -F "language=ru"
```

**Improve Text**:
```bash
curl -X POST "http://localhost:8000/api/v1/ai/improve" \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{"text": "Your text", "prompt": "Fix grammar: {text}"}'
```

## Development

**Local setup** (without Docker):
```bash
# Install Poetry
curl -sSL https://install.python-poetry.org | python3 -

# Install dependencies
poetry install

# Run migrations
poetry run alembic upgrade head

# Start server
poetry run uvicorn app.main:app --reload
```

**Database migrations**:
```bash
# Create migration
poetry run alembic revision --autogenerate -m "description"

# Apply migrations
poetry run alembic upgrade head
```

## Architecture

```
vaulto_note/
├── app/
│   ├── api/          # API routes
│   ├── core/         # Config, security
│   ├── db/           # Database setup
│   ├── models/       # SQLAlchemy models
│   ├── schemas/      # Pydantic schemas
│   └── services/     # Business logic
├── alembic/          # Database migrations
├── tests/            # Test suite
├── docker-compose.yml
├── Dockerfile
└── pyproject.toml
```

## Security Notes

- Keep `API_SECRET_KEY` secure
- Use HTTPS in production
- Consider VPN for self-hosted access
- Regularly update dependencies

## License

MIT
