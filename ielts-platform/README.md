# 🎯 IELTS Master Platform

A comprehensive, full-stack IELTS preparation platform with AI-powered tutoring, 1000+ practice tests, gamification, and personalized learning paths.

![IELTS Master Platform](https://via.placeholder.com/800x400?text=IELTS+Master+Platform)

## ✨ Features

### 📚 Practice Tests (1000+ Tests)
- **Reading**: 300+ passages across 8 topic categories with multiple question types
- **Listening**: 400+ audio exercises covering all 4 IELTS sections
- **Writing**: 200+ Task 1 & Task 2 prompts with sample answers
- **Speaking**: 150+ Part 1, 2, and 3 practice questions

### 🤖 AI-Powered Features
- **AI Writing Analysis**: Get instant band scores and detailed feedback on your essays
- **AI Speaking Feedback**: Analyze your speaking responses with AI
- **AI Tutor Chatbot**: Get personalized IELTS guidance anytime

### 🎮 Gamification
- **XP & Levels**: Earn experience points and level up (10 levels)
- **Achievements**: Unlock 12+ badges for various accomplishments
- **Study Streaks**: Maintain daily practice streaks
- **Progress Tracking**: Visualize your improvement over time

### 📊 Smart Learning
- **Diagnostic Tests**: Identify your current level and weak areas
- **Full Mock Tests**: Simulate real IELTS exam conditions
- **Vocabulary Builder**: Spaced repetition for effective learning
- **Study Planner**: Create and manage your study schedule

### 🎨 User Experience
- **Dark Mode**: Easy on the eyes for night study sessions
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Real-time Notifications**: Stay updated on your progress

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- MongoDB 6+
- Anthropic API Key (for AI features)

### Option 1: Local Development

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/ielts-platform.git
cd ielts-platform
```

2. **Setup Backend**
```bash
cd backend
cp .env.example .env
# Edit .env with your MongoDB URI and Anthropic API key
npm install
npm run dev
```

3. **Setup Frontend** (new terminal)
```bash
cd frontend
npm install
npm start
```

4. **Seed the Database** (optional, for 1000+ tests)
```bash
cd backend
npm run seed
```

5. **Open your browser**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000

### Option 2: Docker Compose

1. **Create environment file**
```bash
cp backend/.env.example .env
# Edit .env with your Anthropic API key
```

2. **Start all services**
```bash
docker-compose up -d
```

3. **Access the application**
- Frontend: http://localhost:3000
- Backend API: http://localhost:5000
- MongoDB Admin: http://localhost:8081 (admin/admin123)

## 📁 Project Structure

```
ielts-platform/
├── frontend/                 # React Frontend
│   ├── public/
│   │   ├── index.html
│   │   └── manifest.json
│   ├── src/
│   │   ├── App.js           # Main application component
│   │   ├── index.js         # React entry point
│   │   ├── index.css        # Tailwind CSS styles
│   │   └── services/
│   │       └── api.js       # API client and hooks
│   ├── package.json
│   ├── tailwind.config.js
│   ├── postcss.config.js
│   └── Dockerfile
├── backend/                  # Node.js Backend
│   ├── server.js            # Express API server
│   ├── seed.js              # Database seeding script
│   ├── package.json
│   ├── .env.example
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🔧 Configuration

### Backend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `PORT` | Server port | `5000` |
| `NODE_ENV` | Environment | `development` |
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017/ielts-platform` |
| `ANTHROPIC_API_KEY` | Anthropic API key for AI features | Required |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:3000` |

### Frontend Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `REACT_APP_API_URL` | Backend API URL | `http://localhost:5000/api` |

## 📡 API Endpoints

### Tests
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/reading` | Get all reading tests |
| GET | `/api/reading/:id` | Get reading test by ID |
| GET | `/api/listening` | Get all listening tests |
| GET | `/api/listening/:id` | Get listening test by ID |
| GET | `/api/writing` | Get all writing tasks |
| GET | `/api/writing/:id` | Get writing task by ID |
| GET | `/api/speaking` | Get all speaking tests |
| GET | `/api/speaking/:id` | Get speaking test by ID |
| GET | `/api/tests` | Get all full mock tests |
| GET | `/api/tests/:id` | Get mock test by ID |

### AI Services
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ai/analyze-writing` | Analyze writing and get band score |
| POST | `/api/ai/analyze-speaking` | Analyze speaking transcript |
| POST | `/api/ai/chat` | Chat with AI tutor |

### User Progress
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/user/:userId/progress` | Get user progress |
| PUT | `/api/user/:userId/progress` | Update user progress |
| POST | `/api/user/:userId/test-result` | Save test result |

### Database
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/seed` | Seed database with tests |

## 🎯 Test Categories

### Reading
- Technology (AI, Space, Energy, etc.)
- Environment (Climate, Conservation, etc.)
- History (Ancient Civilizations, Wars, etc.)
- Science (Genetics, Astronomy, etc.)
- Society (Education, Healthcare, etc.)
- Psychology (Memory, Behavior, etc.)
- Business (Trade, Entrepreneurship, etc.)
- Arts (Modern Art, Music, etc.)

### Writing Task Types
- **Task 1**: Line graphs, Bar charts, Pie charts, Tables, Process diagrams, Maps
- **Task 2**: Education, Technology, Environment, Society, Health, Work, Crime, Media

### Speaking Parts
- **Part 1**: Personal questions (Work, Studies, Hobbies, etc.)
- **Part 2**: Long turn topics with cue cards
- **Part 3**: Discussion questions on abstract topics

## 🏆 Achievements System

| Achievement | Description | XP Reward |
|-------------|-------------|-----------|
| First Steps | Complete your first practice test | 50 |
| Week Warrior | Maintain a 7-day streak | 100 |
| Reading Master | Complete 50 reading tests | 200 |
| Listening Pro | Complete 50 listening tests | 200 |
| Writing Expert | Complete 30 writing tasks | 200 |
| Speaking Star | Complete 30 speaking practices | 200 |
| Vocabulary Builder | Learn 100 vocabulary words | 150 |
| Mock Champion | Complete 10 full mock tests | 300 |
| Band 7 Achiever | Score band 7 or above | 500 |
| Perfectionist | Score 100% on any test | 250 |
| Night Owl | Study after midnight | 50 |
| Early Bird | Study before 6 AM | 50 |

## 🔐 Security Notes

- Store API keys securely using environment variables
- Never commit `.env` files to version control
- Use HTTPS in production
- Implement rate limiting for API endpoints
- Sanitize all user inputs

## 🛠️ Development

### Running Tests
```bash
# Backend tests
cd backend
npm test

# Frontend tests
cd frontend
npm test
```

### Building for Production
```bash
# Frontend build
cd frontend
npm run build

# The build folder is ready to be deployed
```

## 📝 License

MIT License - feel free to use this project for personal or commercial purposes.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📧 Support

For questions or support, please open an issue on GitHub.

---

Built with ❤️ for IELTS learners worldwide
