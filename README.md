# 🌿 ESG Data Extraction and Comparison App

## 📘 Overview

This project automates the extraction, structuring, and visualization of **sustainability and ESG (Environmental, Social, Governance)** metrics from company PDF reports.  
It enables users to upload multiple sustainability reports, automatically extract comparable metrics using **Google Gemini API**, and interactively **compare and visualize** the results in a Streamlit dashboard.

---

## 🎯 **Goal**

The goal of this project is to make ESG data—often locked inside lengthy, unstructured PDF reports—**machine-readable and comparable** across companies.  

This app provides:
- Automated text extraction and contextual understanding  
- Identification of **common sustainability metrics** (e.g., GHG emissions, renewable energy, diversity ratios)  
- Structured tabular data export (CSV, Excel)  
- Interactive visualizations to compare performance between companies  

---

## ⚙️ **Key Features**

| Feature | Description |
|----------|-------------|
| **PDF Upload** | Upload multiple ESG or sustainability reports (PDF). |
| **Automatic Metric Extraction** | Uses the **Gemini API** to extract structured ESG metrics in JSON format. |
| **Common Metric Detection** | Compares reports to find shared KPIs across datasets. |
| **Caching** | Automatically caches processed results for faster reloading. |
| **Interactive Visualization** | View, compare, and analyze metrics using bar charts, radar charts, heatmaps, and tables. |
| **Column Selection** | Select specific datasets and metrics to visualize. |

---

## 🧰 **Tools and Technologies**

| Tool | Purpose |
|------|----------|
| **PyMuPDF (fitz)** | Extracts text from PDF files while preserving structure. |
| **LangChain** | Manages text chunking and LLM prompt orchestration. |
| **Google Gemini API** | Understands context and extracts ESG metrics semantically. |
| **Pandas** | Cleans, aggregates, and formats metrics into structured tables. |
| **Streamlit** | Provides an interactive user interface for exploration and visualization. |
| **Plotly** | Creates dynamic, interactive charts for comparing ESG data. |

---

## **Challenges
In order to extract more metrics from the pdf reports

## 📂 **Project Structure**

app/
│
|-- .venv
├── app.py # Main Streamlit application
├── utils/
│ ├── extraction.py # Functions for PDF text extraction and preprocessing
│ ├── comparison.py # Finds common metrics across extracted datasets
│ └── visualization.py # Generates dynamic charts (bar, radar, heatmap)
│
├── extracted_results/ # Cached CSV/JSON results from processed PDFs
├── example_reports/ # Example sustainability PDFs for testing
├── requirements.txt # Python dependencies



---

## 🧠 **How It Works**

1. **Upload Reports**  
   Users upload one or more PDF sustainability reports through the Streamlit interface.

2. **Text Extraction**  
   The app extracts text using PyMuPDF and sends it to the Gemini API for contextual analysis.

3. **Metric Structuring**  
   Gemini returns structured ESG metrics in JSON format, which are normalized with Pandas.

4. **Common Metric Matching**  
   The app compares all reports to find metrics shared between companies.

5. **Visualization & Comparison**  
   Users can select metrics, datasets, and chart types (Bar, Heatmap, Radar, Table, Dot Plot) to visualize differences interactively.

---

## 🧩 **Installation**

### **1. Clone the Repository **
```bash
git clone 
cd app

source .venv/bin/activate

pip install -r requirements.txt

streamlit run main.py



