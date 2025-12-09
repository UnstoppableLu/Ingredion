from pydantic import BaseModel, Field
from typing import Optional, List, Literal

'''
We define a desired structure to force structured output from the LLM.
The LLM will return structured data in the form of JSON objs, Pydantic models, or dataclasses.
'''

class Metric(BaseModel):
    metric_name: str = Field(..., description="The name of the metric")
    value: str = Field(..., description="The numeric value with units (e.g., '50%', '1,200 tons')")
    year: Optional[int] = Field(None, description="Target or reporting year")

    category: Optional[Literal[
        "environmental", "emissions", "energy", "water", "waste", "social",
        "governance", "safety", "supply_chain", "other"
    ]] = Field(None, description="The Sustainability Category the metric belongs too")

    metric_type: Optional[Literal['target', 'actual', 'baseline']] = Field(
        None, description="describes if the metric is a target, actual result, or baseline value")

    scope: Optional[str] = Field(None, description="The scope of the metric (e.g., 'Scope 1', 'Scope 2')")
    unit: Optional[str] = Field(None, description="The unit of measurement (e.g., '%', 'tons', 'GWh', 'C02e')")

class ExtractedMetrics(BaseModel):
    title: str = Field(..., description="Section title or topic")
    metrics: List[Metric] = Field(..., description= "A list of all the metrics found in the text")
    # Page reference will help us identify how successful the extraction is
    page_ref: Optional[str] = Field(None, description="Page # or section reference")

