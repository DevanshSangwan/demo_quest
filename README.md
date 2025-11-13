# ToneQuest - Professional Writing Evaluation Platform

A modern full-stack application for evaluating and improving professional writing skills through AI-powered similarity scoring and competitive leaderboards.

## 🏗️ Architecture

- **Frontend**: React 19 + TypeScript + Vite + TailwindCSS + shadcn/ui
- **Backend**: FastAPI + Python
- **Authentication**: Firebase Authentication (decoupled)
- **Database**: Google Cloud Firestore
- **Caching**: Redis (with fakeredis fallback for development)
- **AI/ML**: Sentence Transformers for semantic similarity scoring

## 📋 Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.9+
- **Firebase Project** with Firestore and Authentication enabled
- **Redis** (optional, uses fakeredis for development)

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd dummy_quest
```

### 2. Backend Setup

#### Install Dependencies

```bash
pip install -r requirements.txt
```

#### Configure Firebase

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project (or create a new one)
3. Navigate to **Project Settings > Service Accounts**
4. Click **Generate New Private Key**
5. Save the JSON file as `tonequest_backend/app/ServiceAccountKey.json`

#### Set Environment Variables (Optional)

```bash
cp .env.example .env
# Edit .env with your configuration
```

#### Seed Question Data

Create sample questions in Firestore:

1. Go to Firebase Console > Firestore Database
2. Create a collection named `QnA`
3. Add documents with this structure:

```json
{
  "id": 1,
  "prompt_text": "Describe a time when you had to handle a difficult client situation.",
  "category": "Professional Communication",
  "difficulty": "Medium",
  "answers": [
    "I once worked with a client who was unhappy with our initial deliverable...",
    "When faced with a challenging client, I prioritize active listening..."
  ]
}
```

#### Run the Backend

```bash
cd tonequest_backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

- API Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/v1/health`

### 3. Frontend Setup

#### Install Dependencies

```bash
cd frontend
npm install
```

#### Configure Environment

```bash
cp .env.example .env
```

Edit `frontend/.env` with your Firebase configuration:

1. Go to Firebase Console > Project Settings > Your apps
2. Select your web app (or create one)
3. Copy the configuration values to `.env`:

```env
VITE_API_BASE_URL=http://localhost:8000

VITE_FIREBASE_API_KEY=your_api_key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id
```

#### Run the Frontend

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

## 📁 Project Structure

```
dummy_quest/
├── frontend/                    # React frontend application
│   ├── src/
│   │   ├── api/                # API client and services
│   │   │   ├── generated/      # Auto-generated TypeScript types
│   │   │   ├── services/       # API service functions
│   │   │   └── axiosInstance.ts
│   │   ├── components/         # React components
│   │   │   ├── auth/          # Authentication components
│   │   │   ├── layout/        # Layout components
│   │   │   ├── leaderboard/   # Leaderboard components
│   │   │   └── ui/            # shadcn/ui components
│   │   ├── hooks/             # Custom React hooks
│   │   ├── pages/             # Page components
│   │   ├── store/             # Zustand state management
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── .env                   # Environment variables (not in git)
│   └── package.json
│
├── tonequest_backend/          # FastAPI backend application
│   ├── app/
│   │   ├── routers/           # API route handlers
│   │   │   ├── auth.py        # Authentication endpoints
│   │   │   ├── evaluation.py # Question & evaluation endpoints
│   │   │   └── leaderboard.py # Leaderboard endpoints
│   │   ├── core/              # Core utilities
│   │   ├── dependencies.py    # FastAPI dependencies
│   │   ├── firebase_config.py # Firebase initialization
│   │   ├── main.py           # FastAPI application
│   │   ├── schemas.py        # Pydantic models
│   │   └── ServiceAccountKey.json  # Firebase credentials (not in git)
│   └── test_auth.py
│
├── requirements.txt           # Python dependencies
├── ArchitecturalBlueprint.txt # Architecture documentation
└── README.md
```

## 🔑 Key Features

### Authentication Flow
1. User signs up/logs in via Firebase Client SDK (frontend)
2. Firebase returns an ID token (JWT)
3. Token is stored in Zustand store and localStorage
4. Axios interceptor adds token to all API requests
5. Backend verifies token using Firebase Admin SDK

### State Management
- **Zustand**: Global client state (authentication only)
- **TanStack Query**: Server state, caching, and mutations

### API Endpoints

#### Authentication
- `POST /api/v1/auth/signup` - Create new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user profile

#### Evaluation
- `GET /api/v1/questions/next` - Get random question
- `POST /api/v1/evaluate_answer` - Submit answer for evaluation

#### Leaderboard
- `GET /api/v1/leaderboard` - Get global leaderboard
- `GET /api/v1/leaderboard/around_me` - Get relative leaderboard
- `POST /api/v1/leaderboard/update` - Manual score adjustment (admin)

## 🧪 Testing

### Backend Tests

```bash
cd tonequest_backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm run test
```

## 🔧 Development

### Generate TypeScript Types from OpenAPI

After making changes to backend Pydantic models:

```bash
cd frontend
npm run generate-api
```

This reads the OpenAPI schema from the running backend and generates TypeScript types.

### Code Formatting

**Frontend:**
```bash
npm run lint
```

**Backend:**
```bash
# Install black and flake8
pip install black flake8
black app/
flake8 app/
```

## 🐛 Troubleshooting

### CORS Errors
- Ensure backend CORS is configured with your frontend URL
- Check `tonequest_backend/app/main.py` origins list

### Authentication Fails
- Verify Firebase service account key is in correct location
- Check Firebase project ID matches in both frontend and backend
- Ensure Firestore has proper security rules

### Questions Not Loading
- Verify Firestore `QnA` collection exists and has documents
- Check backend logs for Firestore connection errors

### API Calls Fail
- Verify `VITE_API_BASE_URL` in frontend `.env`
- Ensure backend is running on the correct port
- Check browser console for detailed error messages

## 📦 Deployment

### Backend Deployment

1. Set production environment variables
2. Use a production WSGI server (e.g., Gunicorn)
3. Configure production Redis instance
4. Set up proper Firebase service account credentials
5. Enable HTTPS

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Frontend Deployment

1. Update `.env` with production API URL
2. Build the application:

```bash
npm run build
```

3. Deploy the `dist/` folder to your hosting service (Vercel, Netlify, etc.)

### Environment-Specific Configuration

Create separate `.env` files:
- `.env.development` - Local development
- `.env.staging` - Staging environment
- `.env.production` - Production environment

## 🔒 Security Considerations

- Never commit `.env` files or Firebase credentials
- Use Firebase App Check in production
- Implement rate limiting on API endpoints
- Enable HTTPS in production
- Regularly rotate Firebase service account keys
- Implement proper Firestore security rules

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Firebase Documentation](https://firebase.google.com/docs)
- [TanStack Query Documentation](https://tanstack.com/query/latest)
- [shadcn/ui Documentation](https://ui.shadcn.com/)

## 📄 License

[Your License Here]

## 🤝 Contributing

[Your Contributing Guidelines Here]

## 📧 Support

For issues and questions, please open an issue on GitHub or contact [your-email@example.com]
