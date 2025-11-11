from pydantic import BaseModel, Field, ValidationError
from typing import List, Optional
import json


# ------------------------------------------------------------
# 1️⃣ Define your data schema
# ------------------------------------------------------------
class Metric(BaseModel):
    metric_name: str = Field(..., description="Name of the ESG metric, e.g., 'CO2 Emissions'")
    value: str = Field(..., description="Reported value, e.g., '25,000 tons'")
    year: Optional[int] = Field(None, description="Reporting year if available")


class ReportMetrics(BaseModel):
    category: str = Field(..., description="ESG Category, e.g., 'Governance'")
    metrics: List[Metric] = Field(..., description="List of extracted metrics")


# ------------------------------------------------------------
# 2️⃣ Helper to parse and validate LLM output
# ------------------------------------------------------------
def parse_gemini_output(text: str):
    """
    Attempts to extract valid JSON from the Gemini model output and
    validate it against the Pydantic schema.
    Returns a list of ReportMetrics.
    """
    # Try to extract JSON-like text (if wrapped in markdown)
    import re
    json_match = re.search(r"```(?:json)?\s*(\[.*?\]|\{.*?\})\s*```", text, re.DOTALL)
    if json_match:
        text = json_match.group(1)

    text = text.strip()

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError:
        raise ValueError("❌ Gemini output is not valid JSON.")

    # Normalize single object into list
    if isinstance(parsed, dict):
        parsed = [parsed]

    # Validate each item using Pydantic
    validated_reports = []
    for item in parsed:
        try:
            validated = ReportMetrics(**item)
            validated_reports.append(validated)
        except ValidationError as e:
            print(f"⚠️ Validation error for item: {item}\n{e}")

    return validated_reports
