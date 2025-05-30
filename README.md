# AI Interview API

A comprehensive AI-powered interview assessment platform that processes audio and text responses, provides intelligent scoring using NLP, and offers detailed feedback to help users improve their interview performance.

## Features

### Core Functionality
- **Audio Processing**: Speech-to-text conversion using OpenAI Whisper
- **Text Analysis**: Advanced NLP scoring using OpenAI GPT and spaCy
- **Intelligent Scoring**: Multi-dimensional evaluation including:
  - Content relevance
  - Communication clarity
  - Structure and organization
  - Technical accuracy (for technical questions)
  - Sentiment analysis
  - Confidence indicators

### Admin Panel
- **Question Management**: Create, update, delete, and organize interview questions
- **Category System**: Organize questions by categories with color coding
- **Bulk Import/Export**: CSV-based question management
- **Analytics Dashboard**: Performance metrics and usage statistics
- **User Management**: Monitor and manage user accounts

### User Features
- **Multiple Input Methods**: Submit responses via text or audio
- **Real-time Processing**: Background processing with status updates
- **Detailed Feedback**: Comprehensive analysis with improvement suggestions
- **Response History**: Track progress over time
- **Personalized Recommendations**: AI-generated improvement tips

## Technology Stack

- **Backend**: FastAPI (Python)
- **Database**: SQLAlchemy with SQLite (easily upgradeable to PostgreSQL)
- **Audio Processing**: OpenAI Whisper, pydub, librosa
- **NLP**: OpenAI GPT-3.5, spaCy, NLTK
- **Authentication**: JWT tokens with bcrypt password hashing
- **File Handling**: Secure audio file upload and storage

## Installation

### Prerequisites
- Python 3.8+
- OpenAI API key
- (Optional) spaCy English model

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd ai_interview_api
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download spaCy model**
   ```bash
   python -m spacy download en_core_web_sm
   ```

5. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

6. **Initialize the database**
   ```bash
   python -c "from app.database import create_tables; create_tables()"
   ```

7. **Create admin user**
   ```bash
   python -c "
   from app.database import SessionLocal
   from app.utils.security import create_admin_user
   db = SessionLocal()
   create_admin_user(db)
   db.close()
   print('Admin user created')
   "
   ```

## Running the Application

### Development
```bash
python app/main.py
```

### Production
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login user
- `GET /api/v1/auth/me` - Get current user info
- `POST /api/v1/auth/init-admin` - Initialize admin user

### Interview
- `GET /api/v1/interview/questions` - Get random questions
- `POST /api/v1/interview/submit-text` - Submit text response
- `POST /api/v1/interview/submit-audio` - Submit audio response
- `GET /api/v1/interview/response/{id}` - Get response analysis
- `GET /api/v1/interview/history` - Get response history

### Admin
- `POST /api/v1/admin/questions` - Create question
- `GET /api/v1/admin/questions` - List questions with filters
- `PUT /api/v1/admin/questions/{id}` - Update question
- `DELETE /api/v1/admin/questions/{id}` - Delete question
- `POST /api/v1/admin/questions/bulk-import` - Import questions from CSV
- `GET /api/v1/admin/questions/export` - Export questions to CSV
- `GET /api/v1/admin/statistics` - Get system statistics
- `GET /api/v1/admin/analytics/performance` - Get performance analytics

## Configuration

### Environment Variables

```env
# Database
DATABASE_URL=sqlite:///./interview_api.db

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Admin
ADMIN_EMAIL=admin@example.com
ADMIN_PASSWORD=admin123

# File Upload
MAX_FILE_SIZE_MB=50
ALLOWED_AUDIO_FORMATS=mp3,wav,m4a,flac

# Application
DEBUG=True
HOST=0.0.0.0
PORT=8000
```

## Sample Data

Load sample questions using the provided CSV file:

```bash
# Using the admin API endpoint
curl -X POST "http://localhost:8000/api/v1/admin/questions/bulk-import" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -F "file=@sample_questions.csv"
```

## Usage Examples

### 1. Register and Login
```python
import requests

# Register
response = requests.post("http://localhost:8000/api/v1/auth/register", json={
    "email": "user@example.com",
    "username": "testuser",
    "password": "password123",
    "full_name": "Test User"
})

# Login
response = requests.post("http://localhost:8000/api/v1/auth/login-json", json={
    "username": "testuser",
    "password": "password123"
})
token = response.json()["access_token"]
```

### 2. Get Interview Questions
```python
headers = {"Authorization": f"Bearer {token}"}
response = requests.get(
    "http://localhost:8000/api/v1/interview/questions?count=3&difficulty=medium",
    headers=headers
)
questions = response.json()
```

### 3. Submit Text Response
```python
response = requests.post(
    "http://localhost:8000/api/v1/interview/submit-text",
    headers=headers,
    json={
        "question_id": 1,
        "text_response": "I am a software engineer with 5 years of experience..."
    }
)
analysis = response.json()
```

### 4. Submit Audio Response
```python
with open("response.mp3", "rb") as audio_file:
    response = requests.post(
        "http://localhost:8000/api/v1/interview/submit-audio",
        headers=headers,
        data={"question_id": 1},
        files={"audio_file": audio_file}
    )
```

## Scoring System

The AI scoring system evaluates responses across multiple dimensions:

### Scoring Criteria (0-100 scale)
1. **Content Relevance**: How well the response addresses the question
2. **Communication Clarity**: Clarity and articulation of the response
3. **Structure & Organization**: Logical flow and organization
4. **Technical Accuracy**: Technical correctness (for technical questions)

### Additional Metrics
- **Sentiment Analysis**: Emotional tone of the response
- **Confidence Indicators**: Words/phrases indicating confidence level
- **Filler Words**: Count of filler words (um, uh, like, etc.)
- **Vocabulary Diversity**: Unique word usage ratio

### Feedback Generation
- **Strengths**: Identified positive aspects
- **Weaknesses**: Areas needing improvement
- **Suggestions**: Specific actionable recommendations
- **Improvement Plan**: Structured development roadmap

## Security Features

- **JWT Authentication**: Secure token-based authentication
- **Password Hashing**: bcrypt for secure password storage
- **File Validation**: Audio file type and size validation
- **Input Sanitization**: Text input cleaning and validation
- **Admin Authorization**: Role-based access control
- **CORS Configuration**: Configurable cross-origin requests

## Performance Considerations

- **Background Processing**: Audio transcription and NLP analysis run asynchronously
- **File Storage**: Organized user-specific audio file storage
- **Database Optimization**: Indexed queries and efficient relationships
- **Caching Ready**: Structure supports Redis caching implementation
- **Scalable Architecture**: Easily deployable to cloud platforms

## Deployment

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations
- Use PostgreSQL instead of SQLite
- Implement Redis for caching
- Set up proper logging
- Configure environment-specific settings
- Use HTTPS in production
- Implement rate limiting
- Set up monitoring and alerting

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the configuration options in `.env.example`

## Roadmap

- [ ] Real-time WebSocket updates for processing status
- [ ] Video interview support
- [ ] Advanced analytics dashboard
- [ ] Multi-language support
- [ ] Integration with popular ATS systems
- [ ] Mobile app support
- [ ] Advanced AI models for specialized domains
