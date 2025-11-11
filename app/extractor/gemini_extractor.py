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

    def extract_metrics(self, text_chunks: List[Dict[str, str]]) -> List[Dict]:
        """
        Extract ESG metrics from text chunks.
        Each chunk is expected to be a dict with:
          {
            "page_number": int,
            "text": str
          }
        """
        base_prompt = """
        You are an ESG data extraction assistant.
        Extract sustainability metrics from the text and return a **valid JSON array**.
        Each entry must include:
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
            page_number = chunk.get("page_number")
            text = chunk.get("text", "")

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=base_prompt.format(text=text)
            )

            print(f"🧾 Raw Gemini 2.5 flash response for page {page_number}:", response.text)
            raw_text = response.text.strip()
            try:
                parsed = json.loads(raw_text)
                if isinstance(parsed, list):
                    for item in parsed:
                        if isinstance(item, dict):
                            item["source_page"] = page_number
                            all_metrics.append(item)
                elif isinstance(parsed, dict):
                    parsed["source_page"] = page_number
                    all_metrics.append(parsed)
            except json.JSONDecodeError:
                match = re.search(r'(\[.*\]|\{.*\})', raw_text, re.DOTALL)
                if match:
                    parsed = json.loads(match.group())
                    if isinstance(parsed, list):
                        for item in parsed:
                            if isinstance(item, dict):
                                item["source_page"] = page_number
                                all_metrics.append(item)
                    elif isinstance(parsed, dict):
                        parsed["source_page"] = page_number
                        all_metrics.append(parsed)
                else:
                    all_metrics.append({
                        "raw_output": raw_text,
                        "source_page": page_number
                    })

        return all_metrics
