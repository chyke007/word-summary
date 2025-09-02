#!/usr/bin/env python3
"""
Simple startup script for the LLM Knowledge Extractor
"""
import uvicorn
import os
import sys

def main():
    """Run the application"""
    print("🧠 Starting LLM Knowledge Extractor...")
    
    # Check if we're in mock mode
    print(os.getenv("OPENAI_API_KEY"))
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  No OpenAI API key found. Running in mock mode.")
        print("   Set OPENAI_API_KEY environment variable to use real AI services.")
    else:
        print("✅ OpenAI API key found. Using real AI services.")
    
    # Start the server
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

if __name__ == "__main__":
    main()
