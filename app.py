import os
from datetime import datetime
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from models import TextAnalysisRequest, TextAnalysisResponse, SearchRequest, SearchResponse
from llm_service import LLMService, MockLLMService
from nlp_service import NLPService, MockNLPService
from database import DatabaseService, MockDatabaseService

# Use mock services if no API key is provided
use_mock = not os.getenv("OPENAI_API_KEY")
if use_mock:
    llm_service = MockLLMService()
    nlp_service = MockNLPService()
    db_service = MockDatabaseService()
else:
    llm_service = LLMService()
    nlp_service = NLPService()
    db_service = DatabaseService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    await db_service.init_db()
    yield

# Initialize services
app = FastAPI(title="LLM Knowledge Extractor", version="1.0.0", lifespan=lifespan)

# Templates for web UI
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the main web interface"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/analyze", response_model=TextAnalysisResponse)
async def analyze_text(request: TextAnalysisRequest):
    """
    Analyze text using LLM and NLP to extract summary, topics, sentiment, and keywords
    """
    try:
        # Get LLM analysis
        llm_result = await llm_service.analyze_text(request.text)
        
        # Get NLP keywords
        keywords = nlp_service.extract_keywords(request.text)
        
        # Combine results
        analysis_result = {
            "summary": llm_result["summary"],
            "title": llm_result["title"],
            "topics": llm_result["topics"],
            "sentiment": llm_result["sentiment"],
            "keywords": keywords
        }
        
        # Save to database
        await db_service.save_analysis(request.text, analysis_result)
        
        # Return response
        return TextAnalysisResponse(
            summary=analysis_result["summary"],
            title=analysis_result["title"],
            topics=analysis_result["topics"],
            sentiment=analysis_result["sentiment"],
            keywords=analysis_result["keywords"],
            created_at=datetime.now()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/search", response_model=SearchResponse)
async def search_analyses(request: SearchRequest):
    """
    Search through stored analyses by keyword or sentiment
    """
    try:
        results = await db_service.search_analyses(request)
        stats = await db_service.get_stats()
        
        return SearchResponse(
            results=results,
            total=stats["total_analyses"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/analyses", response_model=SearchResponse)
async def get_all_analyses(limit: int = 50):
    """
    Get all stored analyses with optional limit
    """
    try:
        results = await db_service.get_all_analyses(limit)
        stats = await db_service.get_stats()
        
        return SearchResponse(
            results=results,
            total=stats["total_analyses"]
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analyses: {str(e)}")

@app.get("/stats")
async def get_stats():
    """
    Get database statistics
    """
    try:
        return await db_service.get_stats()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "llm": "mock" if use_mock else "openai",
            "nlp": "mock" if use_mock else "nltk",
            "database": "mock" if use_mock else "sqlite"
        }
    }
