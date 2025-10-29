import streamlit as st
import os
import json
from datetime import datetime
from pathlib import Path

from extractor import PDFParser, MetricsExtractor, clean_text, format_metrics

# Page configuration
st.set_page_config(
    page_title="Sustainability Metrics Extractor",
    page_icon="🌍",
    layout="wide"
)

# Sidebar for API key configuration
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter Google API Key", type="password")
    if api_key:
        os.environ["GOOGLE_API_KEY"] = api_key

def main():
    st.title("Sustainability Report Metrics Extractor")
    st.markdown("""
    Upload sustainability reports in PDF format to extract key metrics using AI.
    The tool will analyze environmental, social, and governance metrics.
    """)
    
    # File upload
    uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")
    
    if uploaded_file and not api_key:
        st.error("Please enter your Google API key in the sidebar first.")
        return

    if uploaded_file:
        # Save uploaded file temporarily
        temp_path = Path("data/sample_reports") / uploaded_file.name
        temp_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        try:
            with st.spinner("Processing PDF..."):
                # Initialize extractors
                pdf_parser = PDFParser()
                metrics_extractor = MetricsExtractor()
                
                # Extract text
                text_chunks = pdf_parser.extract_text(str(temp_path))
                st.success(f"Successfully extracted {len(text_chunks)} text chunks")
                
                # Extract metrics
                with st.spinner("Extracting metrics..."):
                    metrics = metrics_extractor.extract_metrics(text_chunks)
                    formatted_metrics = format_metrics(metrics)
                
                # Display results
                st.subheader("Extracted Metrics")
                st.json(formatted_metrics)
                
                # Save results
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = Path("data/extracted_results") / f"{uploaded_file.name}_{timestamp}.json"
                excel_path = Path("data/extracted_results") / f"{uploaded_file.name}_{timestamp}.xlsx"
                output_path.parent.mkdir(parents=True, exist_ok=True)

                with open(output_path, "w") as f:
                    json.dump(formatted_metrics, f, indent=2)

                # Save as Excel file
                import pandas as pd
                # If metrics is a dict of dicts, convert to DataFrame
                if isinstance(formatted_metrics, dict):
                    df = pd.DataFrame([formatted_metrics]) if not any(isinstance(v, dict) for v in formatted_metrics.values()) else pd.DataFrame(formatted_metrics).T
                else:
                    df = pd.DataFrame(formatted_metrics)
                df.to_excel(excel_path, index=False)

                st.success(f"Results saved to {output_path} and {excel_path}")
        
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
        
        finally:
            # Cleanup
            if temp_path.exists():
                temp_path.unlink()

if __name__ == "__main__":
    main()