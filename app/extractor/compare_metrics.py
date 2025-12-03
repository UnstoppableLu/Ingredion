import streamlit as st
import pandas as pd
import os, json, re
from pathlib import Path
from google import genai


# ------------------------------------------------------------
# Helper to extract JSON safely from Gemini output
# ------------------------------------------------------------
def extract_json(text: str):
    """Extract JSON from Gemini output, even if wrapped in code fences."""
    json_match = re.search(r"```(?:json)?\s*(\[[\s\S]*\])\s*```", text, re.DOTALL)
    if json_match:
        text = json_match.group(1)
    return text.strip()


# ------------------------------------------------------------
# Display tables of common metrics (side-by-side datasets)
# ------------------------------------------------------------
def display_common_metrics_tables(common_metrics):
    for group in common_metrics:
        common_metric_name = group.get("common_metric", "Unnamed Metric")
        st.subheader(common_metric_name)

        # Identify dataset keys dynamically
        dataset_keys = [key for key in group.keys() if key.startswith("dataset_")]

        if not dataset_keys:
            st.warning(f"No datasets found for {common_metric_name}")
            continue

        # Find the maximum number of entries among datasets
        max_len = max(len(group[key]) for key in dataset_keys if isinstance(group[key], list))

        table_data = {}

        for dataset_key in dataset_keys:
            entries = group.get(dataset_key, [])

            metric_names = [entry.get("metric_name", "") for entry in entries]
            values = [entry.get("value", "") for entry in entries]
            units = [entry.get("unit", "") for entry in entries]
            years = [entry.get("year", "") for entry in entries]
            sources = [entry.get("source", "") for entry in entries]

            # Pad to align table rows
            metric_names += [""] * (max_len - len(metric_names))
            values += [""] * (max_len - len(values))
            units += [""] * (max_len - len(units))
            years += [""] * (max_len - len(years))
            sources += [""] * (max_len - len(sources))

            # Add to table data (each dataset contributes 5 columns)
            table_data[f"{dataset_key}_metric_name"] = metric_names
            table_data[f"{dataset_key}_value"] = values
            table_data[f"{dataset_key}_unit"] = units
            table_data[f"{dataset_key}_year"] = years
            table_data[f"{dataset_key}_source"] = sources

        # Create DataFrame for this common metric
        df = pd.DataFrame(table_data)
        st.dataframe(df, use_container_width=True)


# ------------------------------------------------------------
# Main Comparison Page
# ------------------------------------------------------------
def compare_metrics_page():
    st.header("📊 Compare Extracted ESG Metrics")

    # Directories
    results_dir = Path("data/extracted_results")
    cache_dir = Path("data/cached_json")
    cache_dir.mkdir(parents=True, exist_ok=True)

    if not results_dir.exists():
        st.warning("⚠️ No extracted CSV files found yet.")
        return

    # List extracted CSV files
    csv_files = sorted(results_dir.glob("*.csv"))
    if not csv_files:
        st.warning("⚠️ No extracted CSV files found in 'data/extracted_results'.")
        return

    # File selection
    selected_files = st.multiselect(
        "Select one or more extracted CSV files to compare:",
        options=[f.name for f in csv_files],
        help="These CSVs were created from your previous extractions."
    )

    category = st.selectbox("Select ESG Category to Focus On",
                            ["Environmental", "Social", "Governance"])

    if not selected_files:
        st.info("👆 Select files above to start.")
        return

    # Build cache filename
    safe_fnames = "_".join([os.path.splitext(f)[0].replace(" ", "_") for f in selected_files])
    cache_file = cache_dir / f"common_metrics_{category.lower()}_{safe_fnames}.json"

    # --------------------------------------------------------
    # STEP 1: Check cache first
    # --------------------------------------------------------
    if cache_file.exists():
        st.success(f"✅ Loaded cached common metrics for {category} from {cache_file.name}")
        with open(cache_file, "r") as f:
            common_metrics = json.load(f)
    else:
        # --------------------------------------------------------
        # STEP 2: Generate via Gemini if cache not found
        # --------------------------------------------------------
        if st.button("🔍 Compare Selected CSVs"):
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                st.error("❌ Please enter your Google API key in the sidebar first.")
                return

            client = genai.Client(api_key=api_key)

            # Load and filter CSVs
            dataframes = []
            for fname in selected_files:
                path = results_dir / fname
                try:
                    df = pd.read_csv(path)
                    expected_cols = {"metric_name", "value", "unit", "year", "category", "source"}
                    if not expected_cols.issubset(df.columns):
                        st.warning(f"{fname} missing expected columns — skipping.")
                        continue
                    df_filtered = df[df["category"].str.lower() == category.lower()]
                    dataframes.append(df_filtered)
                except Exception as e:
                    st.warning(f"⚠️ Could not read {fname}: {e}")

            if len(dataframes) < 2:
                st.warning("Please select at least two valid CSVs with the chosen category.")
                return

            # Prepare Gemini input
            tables = [df.to_dict(orient="records") for df in dataframes]
            prompt = f"""
You are an ESG data analyst. I will give you multiple sustainability metric tables (as JSON).

Each dataset has the following columns:
- "metric_name": the name of the metric (e.g., Scope 1 GHG emissions, renewable electricity use)
- "value": the reported figure
- "unit": the measurement unit (e.g., metric tons CO2e)
- "year": the reporting year
- "category": one of Environmental, Social, or Governance
- "source": file and page origin

Your task:
1. Identify and group metrics that are **semantically common** across these datasets for the category: {category}.
   - “Common” means they refer to the same underlying sustainability indicator (e.g., GHG emissions, water use, energy consumption).
   - Names do not have to match exactly; interpret semantically.
2. For each group of common metrics, return a structured JSON object with:
   - "common_metric": a concise name summarizing the shared topic (e.g. "GHG Emissions (Scopes 1 & 2)")
   - "dataset_1": an array of matching metric objects from the first dataset
   - "dataset_2": an array of matching metric objects from the second dataset
   - etc. for all datasets.

Return **only** a valid JSON array, no explanations or text.
"""

            with st.spinner("🤖 Analyzing and comparing data using Gemini..."):
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[prompt, json.dumps(tables, indent=2)]
                )

            with st.expander("🧾 See Raw Gemini Output"):
                st.code(response.text)

            # Extract JSON safely
            metrics_text = extract_json(response.text)

            try:
                common_metrics = json.loads(metrics_text)
                # Cache result
                with open(cache_file, "w") as f:
                    json.dump(common_metrics, f, indent=2)
                st.success(f"✅ Analysis complete and cached as {cache_file.name}")
            except json.JSONDecodeError:
                st.error("❌ Gemini output was not valid JSON.")
                return
        else:
            st.stop()

    # --------------------------------------------------------
    # STEP 3: Display results
    # --------------------------------------------------------
    if not common_metrics:
        st.warning("⚠️ No common metrics found.")
        return

    st.subheader(f"📊 {len(common_metrics)} Common Metric Groups Found")

    display_common_metrics_tables(common_metrics)
