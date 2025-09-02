import os
import json
import re
from typing import Dict
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class LLMService:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-3.5-turbo"
    
    async def analyze_text(self, text: str) -> Dict:
        """
        Analyze text using LLM to extract summary, title, topics, and sentiment
        """
        try:
            # Create the prompt for the LLM
            prompt = f"""
            Analyze the following text and provide a structured response in JSON format:
            
            Text: "{text[:2000]}"  # Limit text to avoid token limits
            
            Please provide a JSON response with the following structure:
            {{
                "summary": "A 1-2 sentence summary of the text",
                "title": "A descriptive title for the text (or null if not applicable)",
                "topics": ["topic1", "topic2", "topic3"],
                "sentiment": "positive/neutral/negative"
            }}
            
            Guidelines:
            - Summary should be concise and capture the main points
            - Title should be descriptive and relevant
            - Topics should be the 3 most important themes or subjects
            - Sentiment should be one of: positive, neutral, negative
            - Return only valid JSON, no additional text
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that analyzes text and returns structured JSON data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # Parse the JSON response
            content = response.choices[0].message.content.strip()
            
            # Clean up the response to ensure it's valid JSON
            content = self._clean_json_response(content)
            
            result = json.loads(content)
            
            # Validate the response structure
            return self._validate_response(result)
            
        except Exception as e:
            print(f"Error in LLM analysis: {e}")
            # Return a fallback response
            return {
                "summary": "Unable to generate summary due to processing error.",
                "title": None,
                "topics": ["analysis", "error", "processing"],
                "sentiment": "neutral"
            }
    
    def _clean_json_response(self, content: str) -> str:
        """Clean and extract JSON from LLM response"""
        # Remove any markdown formatting
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        
        # Find JSON object boundaries
        start = content.find('{')
        end = content.rfind('}') + 1
        
        if start != -1 and end != 0:
            content = content[start:end]
        
        return content
    
    def _validate_response(self, result: Dict) -> Dict:
        """Validate and ensure all required fields are present"""
        required_fields = ["summary", "topics", "sentiment"]
        
        for field in required_fields:
            if field not in result:
                if field == "summary":
                    result[field] = "Summary not available"
                elif field == "topics":
                    result[field] = ["general", "content", "analysis"]
                elif field == "sentiment":
                    result[field] = "neutral"
        
        # Ensure title is present (can be null)
        if "title" not in result:
            result["title"] = None
        
        # Ensure topics is a list with exactly 3 items
        if not isinstance(result["topics"], list):
            result["topics"] = ["general", "content", "analysis"]
        elif len(result["topics"]) != 3:
            # Pad or truncate to exactly 3 topics
            while len(result["topics"]) < 3:
                result["topics"].append("general")
            result["topics"] = result["topics"][:3]
        
        # Ensure sentiment is valid
        valid_sentiments = ["positive", "neutral", "negative"]
        if result["sentiment"] not in valid_sentiments:
            result["sentiment"] = "neutral"
        
        return result


# Mock LLM Service for testing without API key
class MockLLMService:
    def __init__(self):
        pass
    
    async def analyze_text(self, text: str) -> Dict:
        """Mock implementation for testing"""
        return {
            "summary": f"This is a mock summary for text containing {len(text)} characters.",
            "title": "Mock Title",
            "topics": ["technology", "analysis", "mock"],
            "sentiment": "neutral"
        }
