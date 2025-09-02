import sqlite3
import json
from datetime import datetime
from typing import List, Optional, Dict
import aiosqlite
from models import TextAnalysisResponse, SearchRequest


class DatabaseService:
    def __init__(self, db_path: str = "text_analysis.db"):
        self.db_path = db_path
    
    async def init_db(self):
        """Initialize the database with required tables"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                CREATE TABLE IF NOT EXISTS text_analyses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    original_text TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    title TEXT,
                    topics TEXT NOT NULL,  -- JSON array
                    sentiment TEXT NOT NULL,
                    keywords TEXT NOT NULL,  -- JSON array
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await db.commit()
    
    async def save_analysis(self, original_text: str, analysis_result: Dict) -> int:
        """Save a text analysis result to the database"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO text_analyses 
                (original_text, summary, title, topics, sentiment, keywords)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                original_text,
                analysis_result["summary"],
                analysis_result["title"],
                json.dumps(analysis_result["topics"]),
                analysis_result["sentiment"],
                json.dumps(analysis_result["keywords"])
            ))
            await db.commit()
            return cursor.lastrowid
    
    async def get_analysis(self, analysis_id: int) -> Optional[TextAnalysisResponse]:
        """Get a specific analysis by ID"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT id, summary, title, topics, sentiment, keywords, created_at
                FROM text_analyses WHERE id = ?
            """, (analysis_id,)) as cursor:
                row = await cursor.fetchone()
                if row:
                    return TextAnalysisResponse(
                        summary=row[1],
                        title=row[2],
                        topics=json.loads(row[3]),
                        sentiment=row[4],
                        keywords=json.loads(row[5]),
                        created_at=datetime.fromisoformat(row[6])
                    )
                return None
    
    async def search_analyses(self, search_request: SearchRequest) -> List[TextAnalysisResponse]:
        """Search analyses by keyword or sentiment"""
        async with aiosqlite.connect(self.db_path) as db:
            query = "SELECT id, summary, title, topics, sentiment, keywords, created_at FROM text_analyses WHERE 1=1"
            params = []
            
            if search_request.keyword:
                query += " AND (original_text LIKE ? OR summary LIKE ? OR topics LIKE ? OR keywords LIKE ?)"
                keyword_param = f"%{search_request.keyword}%"
                params.extend([keyword_param, keyword_param, keyword_param, keyword_param])
            
            if search_request.sentiment:
                query += " AND sentiment = ?"
                params.append(search_request.sentiment)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(search_request.limit)
            
            async with db.execute(query, params) as cursor:
                rows = await cursor.fetchall()
                results = []
                for row in rows:
                    results.append(TextAnalysisResponse(
                        summary=row[1],
                        title=row[2],
                        topics=json.loads(row[3]),
                        sentiment=row[4],
                        keywords=json.loads(row[5]),
                        created_at=datetime.fromisoformat(row[6])
                    ))
                return results
    
    async def get_all_analyses(self, limit: int = 50) -> List[TextAnalysisResponse]:
        """Get all analyses with a limit"""
        async with aiosqlite.connect(self.db_path) as db:
            async with db.execute("""
                SELECT id, summary, title, topics, sentiment, keywords, created_at
                FROM text_analyses 
                ORDER BY created_at DESC 
                LIMIT ?
            """, (limit,)) as cursor:
                rows = await cursor.fetchall()
                results = []
                for row in rows:
                    results.append(TextAnalysisResponse(
                        summary=row[1],
                        title=row[2],
                        topics=json.loads(row[3]),
                        sentiment=row[4],
                        keywords=json.loads(row[5]),
                        created_at=datetime.fromisoformat(row[6])
                    ))
                return results
    
    async def get_stats(self) -> Dict:
        """Get database statistics"""
        async with aiosqlite.connect(self.db_path) as db:
            # Total analyses
            async with db.execute("SELECT COUNT(*) FROM text_analyses") as cursor:
                total_analyses = (await cursor.fetchone())[0]
            
            # Sentiment distribution
            async with db.execute("""
                SELECT sentiment, COUNT(*) 
                FROM text_analyses 
                GROUP BY sentiment
            """) as cursor:
                sentiment_counts = dict(await cursor.fetchall())
            
            return {
                "total_analyses": total_analyses,
                "sentiment_distribution": sentiment_counts
            }


# Mock Database Service for testing
class MockDatabaseService:
    def __init__(self):
        self.analyses = []
        self.next_id = 1
    
    async def init_db(self):
        pass
    
    async def save_analysis(self, original_text: str, analysis_result: Dict) -> int:
        analysis_id = self.next_id
        self.next_id += 1
        self.analyses.append({
            "id": analysis_id,
            "original_text": original_text,
            "analysis": analysis_result,
            "created_at": datetime.now()
        })
        return analysis_id
    
    async def get_analysis(self, analysis_id: int) -> Optional[TextAnalysisResponse]:
        for analysis in self.analyses:
            if analysis["id"] == analysis_id:
                result = analysis["analysis"]
                return TextAnalysisResponse(
                    summary=result["summary"],
                    title=result["title"],
                    topics=result["topics"],
                    sentiment=result["sentiment"],
                    keywords=result["keywords"],
                    created_at=analysis["created_at"]
                )
        return None
    
    async def search_analyses(self, search_request: SearchRequest) -> List[TextAnalysisResponse]:
        results = []
        for analysis in self.analyses:
            result = analysis["analysis"]
            text = analysis["original_text"]
            
            # Check keyword filter
            if search_request.keyword:
                keyword = search_request.keyword.lower()
                if not (keyword in text.lower() or 
                       keyword in result["summary"].lower() or
                       any(keyword in topic.lower() for topic in result["topics"]) or
                       any(keyword in kw.lower() for kw in result["keywords"])):
                    continue
            
            # Check sentiment filter
            if search_request.sentiment and result["sentiment"] != search_request.sentiment:
                continue
            
            results.append(TextAnalysisResponse(
                summary=result["summary"],
                title=result["title"],
                topics=result["topics"],
                sentiment=result["sentiment"],
                keywords=result["keywords"],
                created_at=analysis["created_at"]
            ))
            
            if len(results) >= search_request.limit:
                break
        
        return results
    
    async def get_all_analyses(self, limit: int = 50) -> List[TextAnalysisResponse]:
        results = []
        for analysis in self.analyses[-limit:]:
            result = analysis["analysis"]
            results.append(TextAnalysisResponse(
                summary=result["summary"],
                title=result["title"],
                topics=result["topics"],
                sentiment=result["sentiment"],
                keywords=result["keywords"],
                created_at=analysis["created_at"]
            ))
        return results
    
    async def get_stats(self) -> Dict:
        sentiment_counts = {}
        for analysis in self.analyses:
            sentiment = analysis["analysis"]["sentiment"]
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
        
        return {
            "total_analyses": len(self.analyses),
            "sentiment_distribution": sentiment_counts
        }
