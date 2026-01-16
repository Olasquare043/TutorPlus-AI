# TutorPlus AI 🎓

**A multilingual, AI-powered tutoring platform for Nigerian secondary school students**

TutorPlus AI combines advanced language models with retrieval-augmented generation (RAG) to provide curriculum-aligned tutoring in multiple Nigerian languages. Students can ask questions, practice MCQs, track progress, and interact via voice or text.

---

## ✨ Features

### 🧠 AI Tutor
- Real-time text-based tutoring powered by N-ATLaS (African LLM)
- RAG-based answers using uploaded curriculum documents
- Multi-language support (English, Yoruba, Hausa, Igbo)
- Context-aware responses based on selected subject/topic

### 📚 MCQ Practice
- AI-generated multiple-choice questions
- Customizable difficulty levels and question counts
- Auto-grading of submitted answers
- Subject and topic filtering

### 📊 Progress Tracking
- Real-time progress tracking by subject
- Visual progress bars and statistics
- Quiz score tracking
- Learning analytics dashboard

### 🎙️ Voice Features
- Text-to-Speech (gTTS) for all responses
- Speech-to-Text ready (Google Cloud integration)
- Audio playback controls
- Multilingual voice support

### 📖 RAG System
- Upload PDF curriculum documents
- Automatic chunking and embedding
- Semantic search using ChromaDB
- Prevents AI hallucination through grounded responses

### 🔐 Authentication
- JWT-based authentication with refresh tokens
- Secure user registration and login
- Protected routes and API endpoints
- User profile management

---

## 🛠️ Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Database**: SQLite (default) / PostgreSQL
- **ORM**: SQLAlchemy
- **Authentication**: JWT (PyJWT)
- **AI Model**: NCAIR1/N-ATLaS (Hugging Face)
- **Vector DB**: ChromaDB
- **Text Processing**: LangChain, pypdf
- **Voice**: gTTS (Text-to-Speech), Google Cloud Speech-to-Text (ready)

### Frontend
- **Framework**: React 18 + Vite
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Icons**: Lucide React
- **Routing**: React Router v6
- **State Management**: React Context API

### Infrastructure
- **Development**: Lightning AI / Local
- **Deployment Ready**: Docker, cloud platforms
- **API Documentation**: Swagger/OpenAPI

---

## 📋 Prerequisites

- **Node.js** 16+ (for frontend)
- **Python** 3.10+ (for backend)
- **PostgreSQL** 12+ (optional, SQLite is default)
- **Git**

---

## 🚀 Installation

### Clone Repository

```bash
git clone https://github.com/Olasquare043/TutorPlus-AI.git
cd TutorPlus_AI
```

### Backend Setup

#### 1. Navigate to backend directory

```bash
cd backend
```

#### 2. Create virtual environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

#### 3. Install dependencies

```bash
pip install -r requirements.txt
```

#### 4. Configure environment

Create `.env` file in `backend/` directory:

```properties
# Database
DATABASE_URL=sqlite:///./data/tutorplus.db

# JWT
JWT_SECRET_KEY=your-super-secret-key-min-32-chars-here
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# App
APP_ENV=development
DEBUG=True
LOG_LEVEL=INFO

# HuggingFace
HUGGINGFACE_API_KEY=your_huggingface_token

# AI Model
MODEL_NAME=NCAIR1/N-ATLaS
USE_4BIT_QUANTIZATION=False
DEVICE_MAP=cpu

# Chroma
CHROMA_PERSIST_DIR=./data/chroma_db
```

#### 5. Initialize database

```bash
python
>>> from app.database import init_db
>>> init_db()
>>> exit()
```

#### 6. Run backend server

```bash
python run.py
```

Backend will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/api/docs`

---

### Frontend Setup

#### 1. Navigate to frontend directory

```bash
cd frontend
```

#### 2. Install dependencies

```bash
npm install
```

#### 3. Configure environment

Create `.env.local` file in `frontend/` directory:

```properties
VITE_API_URL=http://localhost:8000
VITE_API_BASE_URL=http://localhost:8000/api
```

#### 4. Start development server

```bash
npm run dev
```

Frontend will be available at `http://localhost:5173`

---

## 📖 Usage Guide

### 1. Register & Login

1. Visit `http://localhost:5173`
2. Click "Register" to create account
3. Fill in email, username, password, and language preference
4. Login with credentials

### 2. Upload Curriculum (Optional but Recommended)

For accurate RAG-based answers:

1. Go to Swagger API: `http://localhost:8000/api/docs`
2. Find **POST /api/admin/upload-curriculum**
3. Upload PDF curriculum with subject and grade level
4. AI will automatically process and store content

### 3. Ask Questions (Tutor)

1. Navigate to "Tutor Chat" from dashboard
2. Optionally select subject and language
3. Type your question
4. Click send or use voice input (Not yet implemented)
5. Receive AI-powered answer with sources

### 4. Practice MCQs

1. Go to "MCQ Practice"
2. Select subject, topic, and difficulty
3. Generate questions
4. Answer and submit
5. View results and explanations

### 5. Track Progress

1. Visit "Progress Tracker"
2. Filter by subject
3. View statistics and progress bars
4. Monitor learning streak and quiz scores

---

## 🔌 API Endpoints

### Authentication
```
POST   /api/auth/register       - Register new user
POST   /api/auth/login          - Login user
POST   /api/auth/logout         - Logout user
POST   /api/auth/refresh        - Refresh access token
GET    /api/auth/me             - Get current user
```

### Tutor
```
POST   /api/tutor/ask           - Ask tutor question
POST   /api/tutor/generate-mcq  - Generate MCQ questions
POST   /api/tutor/generate-voice - Generate speech from text
POST   /api/tutor/process-voice-query - Process voice input
```

### Progress
```
GET    /api/progress/my         - Get user's progress
POST   /api/progress/track      - Track progress
GET    /api/progress/student/{subject} - Get subject progress
PUT    /api/progress/student/{subject} - Update subject progress
```

### MCQ
```
GET    /api/mcq/{id}            - Get specific MCQ
GET    /api/mcq/subject/{subject} - Get MCQs by subject
POST   /api/mcq/attempt         - Submit MCQ attempt
GET    /api/mcq/attempts/my     - Get user's attempts
```

### Admin
```
POST   /api/admin/upload-curriculum - Upload curriculum PDF
GET    /api/admin/curriculum-stats  - Get RAG statistics
```

---

## 📚 Project Structure

```
TutorPlus_AI/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── auth.py
│   │   │   │   ├── tutor.py
│   │   │   │   ├── mcq.py
│   │   │   │   ├── progress.py
│   │   │   │   └── admin.py
│   │   │   └── dependencies.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── progress.py
│   │   │   ├── mcq.py
│   │   │   └── syllabus.py
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── ai_service.py
│   │   │   ├── rag_service.py
│   │   │   ├── rag_pipeline.py
│   │   │   ├── user_service.py
│   │   │   └── voice_service.py
│   │   ├── utils/
│   │   ├── middleware/
│   │   ├── main.py
│   │   ├── config.py
│   │   └── database.py
│   ├── data/
│   │   ├── tutorplus.db
│   │   └── chroma_db/
│   ├── audio_outputs/
│   ├── requirements.txt
│   ├── run.py
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── client.js
│   │   │   └── endpoints.js
│   │   ├── components/
│   │   │   ├── auth/
│   │   │   ├── common/
│   │   │   ├── tutor/
│   │   │   ├── mcq/
│   │   │   └── progress/
│   │   ├── context/
│   │   │   ├── AuthContext.jsx
│   │   │   └── ThemeContext.jsx
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx
│   │   │   ├── RegisterPage.jsx
│   │   │   ├── DashboardPage.jsx
│   │   │   ├── TutorPage.jsx
│   │   │   ├── MCQPage.jsx
│   │   │   └── ProgressPage.jsx
│   │   ├── hooks/
│   │   │   ├── useAuth.js
│   │   │   └── useApi.js
│   │   ├── utils/
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── .env.local
└── README.md
```

---

## 🔄 Workflow

### For Students

1. **Register** → Create account with language preference
2. **Ask Questions** → Get instant AI-powered answers
3. **Practice MCQs** → Generate and solve practice questions
4. **Track Progress** → Monitor learning through dashboard

### For Teachers/Admins

1. **Upload Curriculum PDFs** → Via `/api/admin/upload-curriculum`
2. **Monitor Stats** → Check RAG system via `/api/admin/curriculum-stats`
3. **View Student Progress** → Access progress tracking

---

## 🎯 Key Features Implementation

### RAG (Retrieval-Augmented Generation)
- PDFs uploaded → Chunked (1000 chars, 200 overlap)
- Text embedded → Stored in ChromaDB
- Queries → Semantic search in vector DB
- Context → Passed to LLM for grounded responses
- Result → No hallucination, curriculum-based answers

### Multilingual Support
- Languages: English, Yoruba, Hausa, Igbo
- Text-to-Speech: gTTS supports all languages
- Voice Input: Google Cloud Speech-to-Text ready
- Prompts: Language-specific instructions to AI

### Authentication
- Registration → User created with hashed password
- Login → JWT access + refresh tokens issued
- Protected Routes → React Router guards
- API → Bearer token in Authorization header
- Refresh → Auto-refresh on 401 response

---

## 🧪 Testing

### Test Backend API

```bash
# Using Swagger UI
http://localhost:8000/api/docs

# Or using cURL
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'
```

### Test Frontend

1. Open `http://localhost:5173`
2. Register account
3. Login
4. Navigate through features
5. Check browser console for errors

---

## 📦 Deployment

### Docker Deployment

```bash
docker-compose up
```

### Cloud Deployment

**Recommended platforms:**
- **Backend**: Railway, Render, Fly.io, AWS EC2
- **Frontend**: Vercel, Netlify, GitHub Pages
- **Database**: Supabase, Railway, AWS RDS
- **Storage**: AWS S3 for PDFs, audio files

### Environment Variables for Production

- Set `DEBUG=False`
- Use strong `JWT_SECRET_KEY`
- Configure `CORS_ORIGINS` for production domain
- Use managed PostgreSQL instead of SQLite
- Setup Google Cloud credentials for voice
- Configure CDN for static assets

---

## 🐛 Troubleshooting

### Issue: Model fails to load
**Solution**: Ensure sufficient RAM, use CPU-only mode, or reduce model size

### Issue: CORS errors
**Solution**: Check `.env` CORS settings, ensure frontend and backend URLs match

### Issue: Database locked
**Solution**: Close other connections, use PostgreSQL instead of SQLite for production

### Issue: Voice not working
**Solution**: Install ffmpeg, setup Google Cloud credentials

### Issue: RAG not finding documents
**Solution**: Ensure PDFs uploaded, check ChromaDB folder permissions

---

## 📝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👥 Author

- **Olayinka Olayemi pka Olasquare**
---

## 🙏 Acknowledgments

- **N-ATLaS Model**: NCAIR1 (African LLM)
- **ChromaDB**: Vector database
- **FastAPI**: Modern Python web framework
- **React**: Frontend framework

---

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Contact: olasquareconsults@gmail.com

---

## 🗺️ Roadmap

- [ ] Mobile app (iOS/Android)
- [ ] Advanced analytics dashboard
- [ ] Real-time collaboration features
- [ ] Custom curriculum builder
- [ ] Offline mode support
- [ ] Integration with WAEC/NECO/JAMB
- [ ] Teacher dashboard
- [ ] Gamification features

---

**Built with ❤️ for Nigerian students**