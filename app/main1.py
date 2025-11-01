import streamlit as st
import os
import json
from datetime import datetime
from pathlib import Path
import pandas as pd
import re

from extractor import PDFParser, MetricsExtractor
from extractor.compare_metrics import compare_metrics_page


# ------------------------------------------------------------
# Page configuration
# ------------------------------------------------------------
st.set_page_config(
    page_title="Sustainability Metrics Extractor",
    page_icon="🌍",
    layout="wide"
)

# ------------------------------------------------------------
# Sidebar for API key configuration
# ------------------------------------------------------------
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter Google API Key", type="password")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key


# ------------------------------------------------------------
# Helper: Parse Gemini output safely into a Python list/dict
# ------------------------------------------------------------
def parse_gemini_output(output):
    """Clean Gemini raw JSON output and return a Python object."""
    if isinstance(output, (list, dict)):
        
        return output
    if not isinstance(output, str):
        return {}

    # Remove code fences like ```json ... ```
    cleaned = re.sub(r"^```json|```$", "", output.strip(), flags=re.IGNORECASE | re.MULTILINE).strip()

    # Extract JSON structure (list or dict)
    match = re.search(r"(\[.*\]|\{.*\})", cleaned, re.DOTALL)
    if not match:
        return {}

    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        st.warning("⚠️ Gemini output is not valid JSON.")
        return {}
    
def flatten_metrics(data):
    """Flatten the parsed Gemini output into a list of dicts for DataFrame."""
    if isinstance(data, list):
        # List of dicts → usually fine
        flat_list = [item for item in data if isinstance(item, dict)]
    elif isinstance(data, dict):
        # If dict contains lists (like categories), flatten them
        flat_list = []
        for value in data.values():
            if isinstance(value, list):
                flat_list.extend([item for item in value if isinstance(item, dict)])
            elif isinstance(value, dict):
                flat_list.append(value)
    else:
        flat_list = []

    return flat_list



# ------------------------------------------------------------
# Main App Logic
# ------------------------------------------------------------
def main():
    st.title("🌱 Sustainability Report Metrics Extractor")
    st.markdown("""
    Upload sustainability reports in **PDF format** to extract key metrics using AI.
    The tool will analyze **Environmental**, **Social**, and **Governance** metrics.
    """)

    # File upload
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file and not api_key:
        st.error("Please enter your Google API key in the sidebar first.")
        return

    if uploaded_file:
        file_name = uploaded_file.name
        reports_dir = Path("data/sample_reports")
        results_dir = Path("data/extracted_results")
        json_cache_path = Path("data/cached_json") / f"{Path(file_name).stem}.json"
        reports_dir.mkdir(parents=True, exist_ok=True)
        results_dir.mkdir(parents=True, exist_ok=True)
        json_cache_path.parent.mkdir(parents=True, exist_ok=True)

        temp_path = reports_dir / file_name
        result_csv = results_dir / f"{file_name}.csv"
        

        # ✅ If already processed, load existing results
        if result_csv.exists():
            st.success(f"✅ Report '{file_name}' already processed.")
            df = pd.read_csv(result_csv)
            st.subheader("Previously Extracted Metrics")
            st.dataframe(df)
            return

        # Save uploaded file
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getvalue())
            
            
    # ---------- Step 1: Check if cached JSON exists ----------
        if json_cache_path.exists():
            st.info(f"✅ Found cached JSON for {uploaded_file.name}. Loading it instead of calling Gemini.")
            with open(json_cache_path, "r") as f:
                metrics = f.read()
                raw_text = metrics
                st.write("Here is the metrics")
                st.write(metrics)
                # Step 2: Clean the string (remove 'json\n' prefix)
                

                # Step 3: Parse JSON
                try:
                    metrics_list = json.loads(metrics)
                except json.JSONDecodeError:
                    metrics_list = []
                    print("❌ Could not decode JSON")

# Step 4: Convert to DataFrame
                if metrics_list:
                    df = pd.DataFrame(metrics_list)
                    if not df.empty:
                        st.subheader("Extracted Metrics Table")
                        st.dataframe(df)

                # Save to CSV for reuse
                        df.to_csv(result_csv, index=False)
                        st.success(f"✅ Results saved: {result_csv}")
                    else:
                        st.warning("⚠️ No valid table data extracted.")
                #parsed_metrics = parse_gemini_output(metrics)

            
        else:

            try:
                with st.spinner("Converting PDF to text..."):
                    import fitz  # PyMuPDF
                    import pymupdf4llm
                    try:
                        md_text = pymupdf4llm.to_markdown(str(temp_path))
                    except Exception as e:
                        print(f"⚠️ pymupdf4llm failed, using fallback text extraction: {e}")
                        doc = fitz.open(temp_path)
                        md_text = ""
                        for page in doc:
                            md_text += page.get_text("text") + "\n"
                        doc.close()

                st.subheader("Extracted Markdown Preview")
                st.code(md_text[:2000], language="markdown")

                text_chunks = [md_text]

            # Extract metrics using Gemini
                with st.spinner("Extracting metrics via Gemini..."):
                    pdf_parser = PDFParser()
                    metrics_extractor = MetricsExtractor()
                    metrics = metrics_extractor.extract_metrics(text_chunks)
                
                with open(json_cache_path, "w") as f:
                    json.dump(metrics, f, indent=2)
                st.success("✅ Saved Gemini output to cache.")

            # Parse output
                st.write("Here is the metrics")
                st.write(metrics)
                # Step 2: Clean the string (remove 'json\n' prefix)
                

                # Step 3: Parse JSON
                try:
                    metrics_list = metrics
                except json.JSONDecodeError:
                    metrics_list = []
                    print("❌ Could not decode JSON")

# Step 4: Convert to DataFrame
                if metrics_list:
                    df = pd.DataFrame(metrics_list)
                    if not df.empty:
                        st.subheader("Extracted Metrics Table")
                        st.dataframe(df)

                # Save to CSV for reuse
                    df.to_csv(result_csv, index=False)
                    st.success(f"✅ Results saved: {result_csv}")
                else:
                    st.warning("⚠️ No valid table data extracted.")

            except Exception as e:
                st.error(f"❌ Error processing file: {str(e)}")

            finally:
                if temp_path.exists():
                    temp_path.unlink()


if __name__ == "__main__":
    main()
