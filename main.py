import logging

from IPython import display
from pydantic import BaseModel, Field
from rich import print
from typing import Optional, List

from docling.datamodel.base_models import InputFormat
from docling.document_extractor import DocumentExtractor

'''
class EmissionTarget(BaseModel):
    scope_name: str = Field(
        examples=["Scope 1 and 2", "Total Scope 3", "Total Scope 3 FLAG", "Total Scope 3 E&I"]
    )
    baseline_year: Optional[int] = Field(default=None, examples=[2015, 2021])
    total_baseline_emissions: Optional[float] = Field(default=None, examples=[2.1, 55.3])
    emissions_in_scope_percent: Optional[float] = Field(default=None, examples=[95.6, 71.8])
    emissions_in_scope_unit: str = Field(default="%", examples=["%"])
    baseline_emissions_in_scope_of_target: Optional[float] = Field(default=None, examples=[2.0, 39.8])
    baseline_emissions_in_scope_percent: Optional[float] = Field(default=None, examples=[100.0, 39.5])
    target_reduction_factor: Optional[float] = Field(default=None, examples=[2.0, 15.7])
    unit: str = Field(default="million tonnes CO2e", examples=["million tonnes CO2e"])


class DecarbonisationLever(BaseModel):
    lever_name: str = Field(
        examples=[
            "Supplier Climate Programme",
            "Reformulating products",
            "Regenerative agriculture",
        ]
    )
    contribution_percent: float = Field(default=0, examples=[14.0, 13.0])
    notes: Optional[str] = Field(default=None, examples=["Covers baseline plus growth period to 2030"])


class SummaryNotes(BaseModel):
    sbti_scope1_2_coverage: Optional[str] = Field(
        default="Exceeds minimum coverage required by SBTi of 95%",
        examples=["Exceeds minimum coverage required by SBTi of 95%"],
    )
    sbti_scope3_coverage: Optional[str] = Field(
        default="Exceeds minimum coverage required by SBTi of 67.5%",
        examples=["Exceeds minimum coverage required by SBTi of 67.5%"],
    )
    scaling_innovation_gap_explanation: Optional[str] = Field(
        default="Gap represents GHG emissions needing new or scaled solutions",
        examples=["Gap represents GHG emissions needing new or scaled solutions"],
    )


class SustainabilityTargets(BaseModel):
    company_name: Optional[str] = Field(default=None, examples=["Example Corp"])
    reporting_year: Optional[int] = Field(default=None, examples=[2023])
    emission_targets: List[EmissionTarget] = Field(default_factory=list)
    decarbonisation_levers: List[DecarbonisationLever] = Field(default_factory=list)
    subtotal_contribution_percent: Optional[float] = Field(default=78.0, examples=[78.0])
    scaling_innovation_gap_percent: Optional[float] = Field(default=22.0, examples=[22.0])
    total_contribution_percent: Optional[float] = Field(default=100.0, examples=[100.0])
    notes: SummaryNotes = Field(default=SummaryNotes())
'''

#file_path = "../../OneDrive/Documents/Rutgers/Fall 2025/Extern Experience I/UnileverTest2024.pdf"

file_path = (
    "https://upload.wikimedia.org/wikipedia/commons/9/9f/Swiss_QR-Bill_example.jpg"
)


logging.basicConfig(level = logging.INFO)

extractor = DocumentExtractor(allowed_formats=[InputFormat.PDF, InputFormat.IMAGE])

result = extractor.extract(
    source = file_path,
    template = {
        "bill_no": "string",
        "total": "float"
    },
)
print(result.pages)