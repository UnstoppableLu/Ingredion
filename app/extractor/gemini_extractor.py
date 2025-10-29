from google import genai
import os, json
from typing import List, Dict
import re

class MetricsExtractor:
    def __init__(self, api_key: str = None):
        if api_key is None:
            api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("Google API key not found. Please set GOOGLE_API_KEY.")
        self.client = genai.Client(api_key=api_key)

    def extract_metrics(self, text_chunks: List[str]) -> Dict:
        base_prompt = """
        You are an ESG data extraction assistant.
        Extract sustainability metrics from the text and return a **valid JSON array**.
        Each entry should have:
          - metric_name
          - value
          - unit
          - year
          - category (Environmental, Social, Governance)
        Do NOT include any explanations, markdown, or code fences. Return strictly JSON.

        Text:
        {text}
        """

        all_metrics = []
        for chunk in text_chunks:
            response = self.client.models.generate_content(
                model="gemini-2.5-pro",  # ✅ use 2.5 here
                contents=base_prompt.format(text=chunk)
            )

            print("Raw Gemini 2.5 response:", response.text)
            raw_text = response.text.strip()
            try:
                parsed = json.loads(raw_text)
                if isinstance(parsed, list):
                    all_metrics.extend(parsed)
                else:
                    all_metrics.append(parsed)
            except json.JSONDecodeError:
                # fallback: try extracting JSON portion from any stray text
                match = re.search(r'(\[.*\]|\{.*\})', raw_text, re.DOTALL)
                if match:
                    parsed = json.loads(match.group())
                    if isinstance(parsed, list):
                        all_metrics.extend(parsed)
                    else:
                        all_metrics.append(parsed)
                else:
                    # store raw text if parsing fails
                    all_metrics.append({"raw_output": raw_text})
        return all_metrics
