import pytest
import asyncio
from fastapi.testclient import TestClient
from app import app
from llm_service import MockLLMService
from nlp_service import MockNLPService
from database import MockDatabaseService

# Use mock services for testing
app.llm_service = MockLLMService()
app.nlp_service = MockNLPService()
app.db_service = MockDatabaseService()

client = TestClient(app)


def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "services" in data


def test_analyze_text_success():
    """Test successful text analysis"""
    test_text = "This is a test article about artificial intelligence and machine learning. The technology is advancing rapidly and shows great promise for the future."
    
    response = client.post("/analyze", json={"text": test_text})
    assert response.status_code == 200
    
    data = response.json()
    assert "summary" in data
    assert "title" in data
    assert "topics" in data
    assert "sentiment" in data
    assert "keywords" in data
    assert "created_at" in data
    
    # Validate data types and structure
    assert isinstance(data["summary"], str)
    assert isinstance(data["topics"], list)
    assert len(data["topics"]) == 3
    assert data["sentiment"] in ["positive", "neutral", "negative"]
    assert isinstance(data["keywords"], list)
    assert len(data["keywords"]) == 3


def test_analyze_text_empty():
    """Test analysis with empty text"""
    response = client.post("/analyze", json={"text": ""})
    assert response.status_code == 422
    # Check that validation error contains the expected message
    error_detail = response.json()["detail"][0]
    assert "Text cannot be empty" in error_detail["msg"]


def test_analyze_text_whitespace():
    """Test analysis with whitespace-only text"""
    response = client.post("/analyze", json={"text": "   \n\t   "})
    assert response.status_code == 422
    # Check that validation error contains the expected message
    error_detail = response.json()["detail"][0]
    assert "Text cannot be empty" in error_detail["msg"]


def test_search_analyses():
    """Test searching analyses"""
    # First, create some test data
    test_texts = [
        "This is a positive article about technology.",
        "This is a negative article about problems.",
        "This is a neutral article about facts."
    ]
    
    for text in test_texts:
        client.post("/analyze", json={"text": text})
    
    # Test search by sentiment
    response = client.post("/search", json={"sentiment": "positive", "limit": 10})
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total" in data
    assert isinstance(data["results"], list)


def test_get_all_analyses():
    """Test getting all analyses"""
    response = client.get("/analyses")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "total" in data
    assert isinstance(data["results"], list)


def test_get_stats():
    """Test getting statistics"""
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_analyses" in data
    assert "sentiment_distribution" in data
    assert isinstance(data["total_analyses"], int)
    assert isinstance(data["sentiment_distribution"], dict)


def test_web_interface():
    """Test the web interface loads"""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "LLM Knowledge Extractor" in response.text


# Test individual services
def test_mock_llm_service():
    """Test the mock LLM service"""
    service = MockLLMService()
    
    async def test_analysis():
        result = await service.analyze_text("Test text")
        assert "summary" in result
        assert "title" in result
        assert "topics" in result
        assert "sentiment" in result
        assert len(result["topics"]) == 3
    
    asyncio.run(test_analysis())


def test_mock_nlp_service():
    """Test the mock NLP service"""
    service = MockNLPService()
    keywords = service.extract_keywords("This is a test article about technology and innovation.")
    assert isinstance(keywords, list)
    assert len(keywords) == 3


def test_mock_database_service():
    """Test the mock database service"""
    service = MockDatabaseService()
    
    async def test_database():
        await service.init_db()
        
        # Test saving analysis
        analysis_id = await service.save_analysis("Test text", {
            "summary": "Test summary",
            "title": "Test title",
            "topics": ["test", "analysis", "mock"],
            "sentiment": "neutral",
            "keywords": ["test", "keyword", "extraction"]
        })
        assert analysis_id == 1
        
        # Test retrieving analysis
        analysis = await service.get_analysis(1)
        assert analysis is not None
        assert analysis.summary == "Test summary"
        
        # Test search
        from models import SearchRequest
        search_req = SearchRequest(keyword="test", limit=10)
        results = await service.search_analyses(search_req)
        assert len(results) >= 1
        
        # Test stats
        stats = await service.get_stats()
        assert stats["total_analyses"] >= 1
    
    asyncio.run(test_database())


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
