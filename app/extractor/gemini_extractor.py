import os
from typing import List, Dict
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenAI

class MetricsExtractor:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError("Google API key not found. Please set GOOGLE_API_KEY environment variable.")
        
    self.llm = ChatGoogleGenAI(google_api_key=api_key, temperature=0.1)
    
    def extract_metrics(self, text_chunks: List[str]) -> Dict:
        """Extract sustainability metrics from text chunks using Gemini API."""
        metrics = {}
        
        # Base prompt for metric extraction
        base_prompt = """
        Extract sustainability metrics from the following text. Focus on:
        1. Environmental metrics (e.g., CO2 emissions, water usage, energy consumption)
        2. Social metrics (e.g., employee diversity, safety records)
        3. Governance metrics (e.g., board diversity, ethical standards)
        
        Format the output as a structured JSON with metric name, value, unit, and year.
        
        Text:
        {text}
        """
        
        try:
            for chunk in text_chunks:
                response = self.llm.invoke([
                    HumanMessage(content=base_prompt.format(text=chunk))
                ])
                
                # Parse and merge metrics from each chunk
                chunk_metrics = self._parse_response(response.content)
                metrics.update(chunk_metrics)
            
            return metrics
        except Exception as e:
            raise Exception(f"Error extracting metrics: {str(e)}")
    
    def _parse_response(self, response: str) -> Dict:
        """Parse the LLM response and convert to structured format."""
        # Implement response parsing logic here
        # This is a placeholder - actual implementation would depend on the response format
        return {}