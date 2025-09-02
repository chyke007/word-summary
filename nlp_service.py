import re
import collections
from typing import List, Dict
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

try:
    nltk.data.find('taggers/averaged_perceptron_tagger')
except LookupError:
    nltk.download('averaged_perceptron_tagger')


class NLPService:
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
        # Add common words that aren't useful as keywords
        self.stop_words.update(['said', 'says', 'would', 'could', 'should', 'will', 'can', 'may', 'might'])
    
    def extract_keywords(self, text: str, num_keywords: int = 3) -> List[str]:
        """
        Extract the most frequent nouns from text using simple NLP
        """
        try:
            # Clean and tokenize the text
            text = self._clean_text(text)
            tokens = word_tokenize(text.lower())
            
            # Filter out stop words and short words
            filtered_tokens = [
                token for token in tokens 
                if token not in self.stop_words 
                and len(token) > 2 
                and token.isalpha()
            ]
            
            # Tag parts of speech
            pos_tags = pos_tag(filtered_tokens)
            
            # Extract nouns (including proper nouns)
            nouns = [
                word for word, pos in pos_tags 
                if pos in ['NN', 'NNS', 'NNP', 'NNPS']
            ]
            
            # Count frequency
            noun_counts = collections.Counter(nouns)
            
            # Get most common nouns
            most_common = noun_counts.most_common(num_keywords)
            
            # Return just the words, not the counts
            keywords = [word for word, count in most_common]
            
            # If we don't have enough nouns, fill with other frequent words
            if len(keywords) < num_keywords:
                all_word_counts = collections.Counter(filtered_tokens)
                additional_words = [
                    word for word, count in all_word_counts.most_common(num_keywords * 2)
                    if word not in keywords
                ]
                keywords.extend(additional_words[:num_keywords - len(keywords)])
            
            return keywords[:num_keywords]
            
        except Exception as e:
            print(f"Error in keyword extraction: {e}")
            # Fallback: return simple word frequency
            return self._fallback_keywords(text, num_keywords)
    
    def _clean_text(self, text: str) -> str:
        """Clean text for processing"""
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def _fallback_keywords(self, text: str, num_keywords: int) -> List[str]:
        """Fallback keyword extraction using simple word frequency"""
        try:
            # Simple word frequency approach
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
            word_counts = collections.Counter(words)
            
            # Remove common words
            common_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'man', 'men', 'put', 'say', 'she', 'too', 'use'}
            filtered_words = {word: count for word, count in word_counts.items() if word not in common_words}
            
            most_common = collections.Counter(filtered_words).most_common(num_keywords)
            return [word for word, count in most_common]
            
        except Exception:
            return ["text", "content", "analysis"]


# Mock NLP Service for testing without NLTK
class MockNLPService:
    def __init__(self):
        pass
    
    def extract_keywords(self, text: str, num_keywords: int = 3) -> List[str]:
        """Mock implementation for testing"""
        return ["mock", "keyword", "extraction"]
