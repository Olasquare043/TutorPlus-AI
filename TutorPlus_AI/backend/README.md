# TutorPlus AI Backend

## Setup Instructions

### 1. Create Virtual Environment
\`\`\`bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
\`\`\`

### 2. Install Dependencies
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 3. Configure Environment
- Copy `.env` and update database credentials
- Ensure PostgreSQL is running
- Update HuggingFace API key

### 4. Initialize Database
\`\`\`bash
python
>>> from app.database import init_db
>>> init_db()
>>> exit()
\`\`\`

### 5. Run Development Server
\`\`\`bash
python run.py
\`\`\`

Server runs at `http://localhost:8000`
API docs at `http://localhost:8000/api/docs`

## Project Structure
- `app/models/` - SQLAlchemy ORM models
- `app/schemas/` - Pydantic request/response models
- `app/services/` - Business logic (AI, RAG, etc.)
- `app/api/routes/` - API endpoints
- `app/utils/` - Helper functions (JWT, logging, exceptions)
- `app/middleware/` - Custom middleware
- `chroma_db/` - ChromaDB vector storage (persisted)