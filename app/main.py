import streamlit as st
import os
import json
from pathlib import Path
import pandas as pd
import time
import pdfplumber
from google import genai
import re

from extractor.pdf_splitter import split_pdf  # your PDF splitting helper
from extractor.compare_metrics import compare_metrics_page
from extractor.gemini_extractor import MetricsExtractor  # your custom extractor

# ------------------------------------------------------------
# Page config
# ------------------------------------------------------------
st.set_page_config(page_title="Sustainability Metrics Extractor", page_icon="🌍", layout="wide")

# ------------------------------------------------------------
# Sidebar: API Key & settings
# ------------------------------------------------------------
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter Google API Key", type="password")
    pages_per_part = st.number_input("Pages per part", min_value=2, max_value=20, value=5)
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key

# ------------------------------------------------------------
# Page selection
# ------------------------------------------------------------
page = st.sidebar.selectbox(
    "Choose a page",
    ["Extract ESG Metrics", "Compare ESG Metrics"]
)

if page == "Compare ESG Metrics":
    compare_metrics_page()  # Call your compare page
    st.stop()

# ------------------------------------------------------------
# JSON cleanup helper
# ------------------------------------------------------------
def extract_json(text):
    json_match = re.search(r"```(?:json)?\s*(\[\s*{.*}\s*\])\s*```", text, re.DOTALL)
    if json_match:
        text = json_match.group(1)
    return text.strip()

# ------------------------------------------------------------
# Main App
# ------------------------------------------------------------
st.title("🌱 Sustainability Report Metrics Extractor")
st.markdown("""
Upload sustainability reports in **PDF format** to extract key ESG metrics using AI.
Large PDFs will be **split automatically** into smaller chunks to avoid API limits.
""")

uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

if uploaded_file and not api_key:
    st.error("Please enter your Google API key in the sidebar first.")
    st.stop()

if uploaded_file:
    file_name = uploaded_file.name
    results_dir = Path("data/extracted_results")
    temp_dir = Path("data/pdf_parts")
    results_dir.mkdir(parents=True, exist_ok=True)
    temp_dir.mkdir(parents=True, exist_ok=True)
    result_csv = results_dir / f"{Path(file_name).stem}.csv"

    # -------------------------
    # Check if cached CSV exists
    # -------------------------
    if result_csv.exists():
        st.success(f"✅ Report '{file_name}' already processed.")
        df = pd.read_csv(result_csv)
        st.subheader("Previously Extracted Metrics")
        st.dataframe(df)
        st.stop()

    # Save uploaded file temporarily
    temp_pdf_path = temp_dir / file_name
    with open(temp_pdf_path, "wb") as f:
        f.write(uploaded_file.getvalue())

    # -------------------------
    # Split the PDF into parts
    # -------------------------
    st.info("✂️ Splitting PDF into smaller parts...")
    pdf_parts = split_pdf(temp_pdf_path, temp_dir, pages_per_part=pages_per_part)
    st.success(f"✅ Split into {len(pdf_parts)} parts.")

    # -------------------------
    # Initialize MetricsExtractor
    # -------------------------
    extractor = MetricsExtractor(api_key=os.environ.get("GOOGLE_API_KEY"))
    all_metrics = []

    # -------------------------
    # Process each PDF part
    # -------------------------
    st.info("🔍 Extracting metrics from PDF parts...")

    page_offset = 0  # keep track of where the chunk starts in the full PDF

    for idx, part in enumerate(pdf_parts, start=1):
        st.write(f"📄 Processing part {idx}/{len(pdf_parts)}: {Path(part).name}")
        try:
            # Extract text per page
            text_chunks = []
            with pdfplumber.open(part) as pdf:
                for i, page in enumerate(pdf.pages, start=1):
                    text_chunks.append({
                        "page_number": page_offset + i,  # absolute page number
                        "text": page.extract_text()
                    })

            # Extract metrics
            metrics = extractor.extract_metrics(text_chunks)

            # Add source info & normalize categories
            for m in metrics:
                m["source"] = f"{file_name} - page {m.get('source_page', 'unknown')}"
                category = m.get("category", "").capitalize()
                if category not in ["Environmental", "Social", "Governance"]:
                    m["category"] = "Environmental"
            all_metrics.extend(metrics)

            # Update offset for next chunk
            page_offset += len(pdf.pages)

            # Cooldown to prevent rate limit
            time.sleep(5)

        except Exception as e:
            st.error(f"❌ Error on part {idx}: {str(e)}")
            time.sleep(5)
            continue

    # -------------------------
    # Combine and save results
    # -------------------------
    if all_metrics:
        df = pd.DataFrame(all_metrics)
        # Reorder columns
        columns_order = ["metric_name", "value", "unit", "year", "category", "source"]
        df = df[columns_order]
        df.to_csv(result_csv, index=False)
        st.subheader("📊 Extracted ESG Metrics")
        st.dataframe(df)
        st.success(f"✅ Combined results saved to {result_csv}")
    else:
        st.warning("⚠️ No metrics were extracted from any part of the PDF.")
