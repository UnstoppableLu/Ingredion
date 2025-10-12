# Introduction
### Goal

The objective of this project is to automate the extraction of sustainability and ESG (Environmental, Social, and Governance) data from company reports—typically published as unstructured PDF documents. These reports often contain valuable quantitative metrics (e.g., greenhouse gas emissions, renewable energy usage, water consumption, and workforce diversity), but extracting them manually is time-consuming and error-prone.

This notebook demonstrates a data extraction pipeline that converts unstructured sustainability reports into structured, machine-readable datasets, enabling further analysis, comparison, and visualization.

# Challenges

Sustainability reports present several technical challenges for automated data extraction:

Unstructured Format:
Most reports are designed for human readability, not machine parsing. Text is embedded within complex layouts, tables, and mixed formatting, which makes direct parsing difficult.

Inconsistent Terminology:
Companies use varied naming conventions for similar metrics (e.g., “Scope 1 CO₂ emissions” vs. “Direct GHG emissions”), complicating rule-based extraction.

Context Ambiguity:
Numeric data often lacks context when extracted without surrounding text. For instance, “1,200” could refer to tons of CO₂ or MWh of energy, depending on the section.

Data Scattering Across Pages:
Key metrics may appear in different sections—environmental, social, or governance—requiring contextual understanding to correctly associate them.

# Tools and Technologies

To overcome these challenges, the following tools and frameworks were integrated into the workflow:

### Tool & Purpose
PyMuPDF (fitz):	Extracts raw text content from PDF files while preserving basic structure and layout.
LangChain:	Manages document chunking, prompt orchestration, and communication with the language model for contextual analysis.
Gemini API (Google Generative AI):	Performs semantic understanding of extracted text, identifying and structuring sustainability metrics in tabular JSON format.
Pandas:	Normalizes, cleans, and aggregates the extracted metrics into a structured DataFrame for analysis and export.
# Outcome

The final output is a structured dataset (in Excel format) containing key sustainability indicators extracted from the report, along with contextual information such as metric category, units, and description. This pipeline streamlines ESG data collection and enables scalable sustainability analytics across multiple companies.
