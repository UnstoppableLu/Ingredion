import streamlit as st
import pandas as pd
import os, json
from pathlib import Path
from google import genai

def compare_metrics_page():
    st.header("📊 Compare Extracted ESG Metrics")

    results_dir = Path("data/extracted_results")
    if not results_dir.exists():
        st.warning("No extracted CSV files found yet.")
        return

    csv_files = sorted(results_dir.glob("*.csv"))
    if not csv_files:
        st.warning("No extracted CSV files found in 'data/extracted_results'.")
        return

    selected_files = st.multiselect(
        "Select one or more extracted CSV files to compare:",
        options=[f.name for f in csv_files],
        help="These CSVs were created from your previous extractions."
    )

    category = st.selectbox(
        "Select ESG Category to Focus On",
        ["Environmental", "Social", "Governance"]
    )

    if st.button("🔍 Compare Selected CSVs") and selected_files:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            st.error("Please enter your Google API key in the sidebar first.")
            return

        client = genai.Client(api_key=api_key)

        dataframes = []
        for fname in selected_files:
            path = results_dir / fname
            try:
                df = pd.read_csv(path)
                if "category" in df.columns:
                    df_filtered = df[df["category"].str.lower() == category.lower()]
                    dataframes.append(df_filtered)
            except Exception as e:
                st.warning(f"⚠️ Could not read {fname}: {e}")

        if len(dataframes) < 2:
            st.warning("Please select at least two valid CSVs with the chosen category.")
            return

        tables = [df.to_dict(orient="records") for df in dataframes]
        prompt = f"""
        You are an ESG data analyst. I will give you multiple sustainability metric tables (as JSON).
        Find and return metrics that appear **in common** across these datasets for the category: {category}.
        "Common" means similar metric_name and year (and optionally similar values).
        Return the result as a valid JSON array.
        """

        with st.spinner("Analyzing and comparing data using Gemini..."):
            response = client.models.generate_content(
                model="gemini-2.5-pro",
                contents=[prompt, json.dumps(tables, indent=2)]
            )

        with st.expander("See Raw Gemini Output"):
            st.code(response.text)

        try:
            common_metrics = json.loads(response.text)
            if isinstance(common_metrics, list) and common_metrics:
                df_common = pd.DataFrame(common_metrics)
                st.subheader("✅ Common Metrics Found Across Files")
                st.dataframe(df_common)

                csv_data = df_common.to_csv(index=False)
                st.download_button(
                    label="💾 Download Common Metrics CSV",
                    data=csv_data,
                    file_name="common_metrics.csv",
                    mime="text/csv"
                )
            else:
                st.warning("⚠️ No common metrics found or Gemini returned an empty result.")
        except json.JSONDecodeError:
            st.error("❌ Gemini output was not valid JSON.")
