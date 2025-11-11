import streamlit as st
import os
import json
from pathlib import Path
import pandas as pd
from google import genai
import re
import time

from extractor.pdf_splitter import split_pdf  # ✅ Import your PDF splitting helper
from extractor.compare_metrics import compare_metrics_page
from extractor.structure_helper import parse_gemini_output


# ------------------------------------------------------------
# Page config
# ------------------------------------------------------------
st.set_page_config(page_title="Sustainability Metrics Extractor", page_icon="🌍", layout="wide")


# ------------------------------------------------------------
# Sidebar: API Key
# ------------------------------------------------------------
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter Google API Key", type="password")
    pages_per_part = st.number_input("Pages per part", min_value=2, max_value=20, value=5)
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        
# In main(), or at the top of your Streamlit app
page = st.sidebar.selectbox(
    "Choose a page",
    ["Extract ESG Metrics", "Compare ESG Metrics"]
)

if page == "Extract ESG Metrics":
    # Your existing extraction logic
    st.title("🌱 Sustainability Report Metrics Extractor")
    # ... rest of your extraction code ...

elif page == "Compare ESG Metrics":
    # Call the compare_metrics_page function
    compare_metrics_page()


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
def main():
    st.title("🌱 Sustainability Report Metrics Extractor")
    st.markdown("""
    Upload sustainability reports in **PDF format** to extract key metrics using AI.
    Large PDFs will be **split automatically** into smaller chunks to avoid API limits.
    """)

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file and not api_key:
        st.error("Please enter your Google API key in the sidebar first.")
        return

    if uploaded_file:
        file_name = uploaded_file.name
        results_dir = Path("data/extracted_results")
        temp_dir = Path("data/pdf_parts")
        results_dir.mkdir(parents=True, exist_ok=True)
        temp_dir.mkdir(parents=True, exist_ok=True)
        result_csv = results_dir / f"{Path(file_name).stem}.csv"

        # -------------------------
        # If cached CSV exists
        # -------------------------
        if result_csv.exists():
            st.success(f"✅ Report '{file_name}' already processed.")
            df = pd.read_csv(result_csv)
            st.subheader("Previously Extracted Metrics")
            st.dataframe(df)
            return

        # Save uploaded file temporarily
        temp_pdf_path = temp_dir / file_name
        with open(temp_pdf_path, "wb") as f:
            f.write(uploaded_file.getvalue())

        # -------------------------
        # Split the PDF
        # -------------------------
        st.info("✂️ Splitting PDF into smaller parts...")
        pdf_parts = split_pdf(temp_pdf_path, temp_dir, pages_per_part=pages_per_part)
        st.success(f"✅ Split into {len(pdf_parts)} parts.")

        # -------------------------
        # Initialize Gemini client
        # -------------------------
        client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))
        all_metrics = []

        # -------------------------
        # Process each PDF part
        # -------------------------
        for idx, part in enumerate(pdf_parts, start=1):
            st.write(f"📄 Processing part {idx}/{len(pdf_parts)}: {Path(part).name}")

            try:
                uploaded_pdf = client.files.upload(file=open(part, "rb"), config={"mime_type": "application/pdf"})
                prompt_text = (
                    "Extract all performance metrics from this PDF and return ONLY a JSON object "
                    "matching this schema: {'category': str, 'metrics': [{'metric_name': str, 'value': str, 'year': int}]}."
                )

                response = client.models.generate_content(
                    model="gemini-2.0-flash",
                    contents=[prompt_text, uploaded_pdf]
                )

                #metrics_text = extract_json(response.text)
                output_text = response.text
                print(output_text)
                try:
                    validated_reports = parse_gemini_output(output_text)
                    for report in validated_reports:
                        # Convert each ReportMetrics object to dict and extend the list
                        all_metrics.extend([m.dict() for m in report.metrics])
                except Exception as e:
                    st.warning(f"⚠️ Could not parse part {idx}: {e}")
                    continue
                # Cooldown to prevent rate limit (429)
                time.sleep(2)

            except Exception as e:
                st.error(f"❌ Error on part {idx}: {str(e)}")
                time.sleep(5)
                continue

        # -------------------------
        # Combine and save results
        # -------------------------
        if all_metrics:
            df = pd.DataFrame(all_metrics)
            df.to_csv(result_csv, index=False)
            st.subheader("📊 Extracted ESG Metrics")
            st.dataframe(df)
            st.success(f"✅ Combined results saved to {result_csv}")
        else:
            st.warning("⚠️ No metrics were extracted from any part of the PDF.")


if __name__ == "__main__":
    main()
