# Digital Banking Platform

A secure, scalable, and user-friendly full-stack web application for digital banking operations.

## Features

### Core Features
- User registration and authentication with JWT
- Account management and balance tracking
- Transaction history and real-time updates
- Fund transfers between accounts
- Real-time notifications via WebSocket
- Role-based access control (User/Admin)

### Security Features
- JWT-based authentication
- Rate limiting and CSRF protection
- Data encryption at rest and in transit
- Input validation and sanitization
- Session management with Redis

### Admin Features
- Admin dashboard for monitoring
- Transaction approval workflow
- User activity monitoring
- System analytics

### Optional Features
- Two-Factor Authentication (2FA)
- PDF account statements
- Scheduled/recurring payments
- Fraud detection rules
- User analytics dashboard

## Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React, Redux Toolkit, TailwindCSS |
| Backend | FastAPI, SQLAlchemy, Pydantic |
| Database | PostgreSQL |
| Caching | Redis |
| Messaging | Apache Kafka |
| Authentication | JWT (OAuth2) |
| Containerization | Docker, Docker Compose |
| CI/CD | GitHub Actions |
| Testing | Pytest, Jest, React Testing Library |

## Project Structure

```
digital-banking-platform/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # API routes
│   │   ├── core/           # Core configuration
│   │   ├── models/         # Database models
│   │   ├── schemas/        # Pydantic schemas
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utility functions
│   ├── tests/              # Backend tests
│   └── requirements.txt
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── pages/          # Page components
│   │   ├── store/          # Redux store
│   │   ├── services/       # API services
│   │   └── utils/          # Utility functions
│   ├── public/
│   └── package.json
├── kafka/                  # Kafka consumers
├── docker-compose.yml      # Docker services
├── .github/               # GitHub Actions
└── docs/                  # Documentation
```

## Quick Start

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)

### Development Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd digital-banking-platform
```

2. Start all services with Docker Compose:
```bash
docker-compose up -d
```

3. Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Admin Dashboard: http://localhost:3000/admin

### Environment Variables

Create `.env` files for each service:

#### Backend (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/banking_db
REDIS_URL=redis://localhost:6379
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30
```

#### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws
```

## Development

### Backend Development
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm install
npm start
```

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

## Deployment

The application is containerized and can be deployed using Docker Compose or Kubernetes.

### Production Deployment
1. Set production environment variables
2. Build and deploy containers:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Security Considerations

- All API endpoints are protected with JWT authentication
- Rate limiting implemented on sensitive endpoints
- CSRF protection enabled
- Data encrypted at rest and in transit
- Input validation on all user inputs
- SQL injection prevention with parameterized queries

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new features
5. Submit a pull request

## License

This project is licensed under the MIT License. 
