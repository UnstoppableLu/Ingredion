import streamlit as st
import os
import json
from pathlib import Path
import pandas as pd
from google import genai
import re

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
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key
        
        
        
def extract_json(text):
    # Try to extract JSON inside ```json ... ``` or ``` ... ```
    json_match = re.search(r"```(?:json)?\s*(\[\s*{.*}\s*\])\s*```", text, re.DOTALL)
    if json_match:
        text = json_match.group(1)
    # Trim stray characters
    text = text.strip()
    return text

# ------------------------------------------------------------
# Main App
# ------------------------------------------------------------
def main():
    st.title("🌱 Sustainability Report Metrics Extractor")
    st.markdown("""
    Upload sustainability reports in **PDF format** to extract key metrics using AI.
    """)

    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

    if uploaded_file and not api_key:
        st.error("Please enter your Google API key in the sidebar first.")
        return

    if uploaded_file:
        file_name = uploaded_file.name
        results_dir = Path("data/extracted_results")
        results_dir.mkdir(parents=True, exist_ok=True)
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

        # -------------------------
        # Send PDF directly to Gemini
        # -------------------------
        try:
            st.info("📤 Uploading PDF to Gemini for analysis...")

           # ✅ Initialize the Gemini client (google-genai)
            client = genai.Client(api_key=os.environ.get("GOOGLE_API_KEY"))

            # ✅ Upload the file (correct syntax for google-genai)
            uploaded_pdf = client.files.upload(
                file=uploaded_file, config={'mime_type': 'application/pdf'}
            )
            st.success(f"✅ Uploaded {file_name} to Gemini. Processing...")

            # Prompt for ESG metric extraction
            prompt = """
            Extract all Environmental, Social, and Governance metrics from the PDF.

            Return your answer *strictly as a valid JSON array* of objects with keys:
            metric, value, category.
            Do not include any explanations, comments, or markdown code fences.
            """

            # Generate content with Gemini
            response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[prompt, uploaded_pdf]
)

            metrics_text = response.text
            st.subheader("🧠 Raw Gemini Output")
            st.code(metrics_text, language="json")

            
            metrics_text = extract_json(metrics_text)

            try:
                metrics_list = json.loads(metrics_text)
            except json.JSONDecodeError:
                st.warning("⚠️ Gemini output was not valid JSON. Please review manually.")
                st.code(metrics_text)
                metrics_list = []


            # Display results
            if metrics_list:
                df = pd.DataFrame(metrics_list)
                st.subheader("📊 Extracted Metrics Table")
                st.dataframe(df)
                df.to_csv(result_csv, index=False)
                st.success(f"✅ Results saved to {result_csv}")
            else:
                st.warning("⚠️ No structured metrics extracted from the report.")

        except Exception as e:
            st.error(f"❌ Error sending PDF to Gemini: {str(e)}")


if __name__ == "__main__":
    main()
