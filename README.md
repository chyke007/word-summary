# 🧠 LLM Knowledge Extractor

A powerful prototype that extracts insights, summaries, and structured data from any text using AI. Built with FastAPI, OpenAI, and modern web technologies.

## ✨ Features

- **Text Analysis**: Extract 1-2 sentence summaries from any text
- **Structured Data Extraction**: Get title, topics, sentiment, and keywords
- **Smart Keyword Extraction**: Uses NLP to find the most frequent nouns
- **Web Interface**: Beautiful, responsive UI for easy interaction
- **REST API**: Full API endpoints for integration
- **Search & Filter**: Find previous analyses by keyword or sentiment
- **Database Storage**: SQLite database for persistent storage
- **Docker Support**: Easy deployment with containerization
- **Mock Mode**: Works without API keys for testing
- **Comprehensive Testing**: Full test suite with pytest
- **Easy Setup**: Simple installation and configuration

## 🚀 Quick Start

### Option 1: Local Development

1. **Clone and setup**:
   ```bash
   git clone <repo-url>
   cd word-summary
   ```

2. **Create virtual environment** (recommended):
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application**:
   ```bash
   python3 run.py
   # or
   uvicorn app:app --reload
   ```

5. **Open your browser**:
   Navigate to `http://localhost:8000`

### Option 2: Docker

1. **Build and run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

2. **Or build manually**:
   ```bash
   docker build -t llm-extractor .
   docker run -p 8000:8000 llm-extractor
   ```

## 🔧 Configuration

### With OpenAI API (Recommended)

1. **Get an OpenAI API key** from [OpenAI Platform](https://platform.openai.com/api-keys)

2. **Create a `.env` file**:
   ```bash
   cp env.example .env
   ```

3. **Edit the `.env` file** and add your API key:
   ```
   OPENAI_API_KEY=sk-your-actual-openai-api-key-here
   ```

4. **Alternative: Set environment variable**:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```

### Without API Key (Mock Mode)

The application automatically falls back to mock services if no API key is provided. This is perfect for:
- Testing and development
- Demonstrations
- Understanding the codebase

## 📚 API Documentation

Once running, visit:
- **Interactive API Docs**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Key Endpoints

- `POST /analyze` - Analyze text and extract insights
- `POST /search` - Search previous analyses
- `GET /analyses` - Get all stored analyses
- `GET /stats` - Get database statistics
- `GET /health` - Health check

### Example API Usage

```bash
# Analyze text
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"text": "Your text here..."}'

# Search analyses
curl -X POST "http://localhost:8000/search" \
     -H "Content-Type: application/json" \
     -d '{"keyword": "technology", "sentiment": "positive"}'
```

## 🧪 Testing

The project includes a comprehensive test suite that covers all major functionality:

```bash
# Run all tests
python3 test_app.py
# or
pytest test_app.py -v

# Run specific test
pytest test_app.py::test_health_check -v
```

### Test Coverage

- ✅ **API Endpoints**: All REST endpoints tested
- ✅ **Service Layer**: LLM, NLP, and Database services
- ✅ **Error Handling**: Input validation and error cases
- ✅ **Mock Services**: Tests work without external dependencies
- ✅ **Web Interface**: UI loading and functionality

The tests use mock services, so they run fast and don't require API keys or external services.

## 🏗️ Architecture & Design Choices

### Why This Structure?

1. **Modular Design**: Separated concerns into distinct services (LLM, NLP, Database) for maintainability and testability
2. **FastAPI**: Chosen for its automatic API documentation, type safety, and async support
3. **Mock Services**: Implemented fallback mock services to ensure the app works without external dependencies
4. **SQLite**: Lightweight database perfect for prototyping and development
5. **Modern UI**: Clean, responsive interface that works on all devices

### Key Design Decisions

- **Service Layer Pattern**: Each service (LLM, NLP, Database) is independently testable and replaceable
- **Async/Await**: Full async support for better performance and scalability
- **Error Handling**: Comprehensive error handling with graceful fallbacks
- **Type Safety**: Pydantic models ensure data validation and type safety
- **Progressive Enhancement**: Works with or without external services

### Trade-offs Made

1. **Time vs. Features**: Focused on core functionality over advanced features like user authentication
2. **Simplicity vs. Scalability**: Used SQLite instead of PostgreSQL for easier setup
3. **Mock vs. Real Services**: Implemented mock services to ensure the app works in any environment
4. **UI vs. API**: Built both web UI and API to demonstrate different use cases

## 📁 Project Structure

```
word-summary/
├── app.py                 # Main FastAPI application
├── models.py              # Pydantic data models
├── llm_service.py         # OpenAI integration and mock service
├── nlp_service.py         # NLP keyword extraction
├── database.py            # Database operations
├── test_app.py            # Comprehensive test suite
├── run.py                 # Simple startup script
├── demo.py                # API demonstration script
├── templates/
│   └── index.html         # Beautiful web UI template
├── requirements.txt       # Python dependencies (updated versions)
├── env.example            # Environment variables template
├── Dockerfile             # Container configuration
├── docker-compose.yml     # Docker Compose setup
├── .dockerignore          # Docker ignore file
├── .gitignore             # Git ignore file
├── text_analysis.db       # SQLite database (created on first run)
└── README.md              # This file
```

## 🔍 How It Works

1. **Text Input**: User provides text via web UI or API
2. **LLM Analysis**: OpenAI GPT-3.5-turbo extracts summary, title, topics, and sentiment
3. **NLP Processing**: NLTK extracts the most frequent nouns as keywords
4. **Data Storage**: Results are saved to SQLite database
5. **Response**: Structured JSON response with all extracted data

## 🛠️ Troubleshooting

### Common Issues

**OpenAI API Key Issues:**
- Make sure your API key starts with `sk-`
- Check that the `.env` file is in the project root
- Verify the key is valid at [OpenAI Platform](https://platform.openai.com/api-keys)

**Dependency Issues:**
- Use Python 3.8+ for best compatibility
- Create a virtual environment to avoid conflicts
- Update pip: `pip install --upgrade pip`

**Database Issues:**
- The SQLite database is created automatically on first run
- If you encounter database errors, delete `text_analysis.db` and restart

**Port Already in Use:**
- Change the port: `uvicorn app:app --port 8001`
- Or kill the process using port 8000

## 🚀 Deployment

### Production Considerations

- Set `OPENAI_API_KEY` environment variable
- Use a production WSGI server like Gunicorn
- Consider using PostgreSQL for production databases
- Add authentication and rate limiting
- Set up monitoring and logging

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (optional)
- `DEBUG`: Enable debug mode (default: False)


### Sample API Calls

```bash
# Analyze a news article
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"text": "Artificial intelligence is transforming industries worldwide. Companies are adopting AI to improve efficiency and create new opportunities."}'

# Search for positive sentiment analyses
curl -X POST "http://localhost:8000/search" \
     -H "Content-Type: application/json" \
     -d '{"sentiment": "positive", "limit": 5}'
```

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 🆘 Support

If you encounter any issues:

1. Check the logs for error messages
2. Ensure all dependencies are installed
3. Verify your OpenAI API key (if using real services)
4. Try running in mock mode first
5. Check the troubleshooting section above

---

**Built with ❤️ using FastAPI, OpenAI, and modern web technologies**
