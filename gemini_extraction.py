import pymupdf as pym
from typing import List, Dict, Tuple, Union
import os
from google import genai
from google.genai import types
import json
from structure import *

'''
This extraction method will be attempted for non-markdown PDFs
'''
PAGES_PER_BATCH = 10
MAX_PAGES_TO_PROCESS = None

def extract_with_gemini(filename: str, api_key: str = None) -> List[Dict]:
    if api_key is None:
        api_key = os.environ['GOOGLE_API_KEY']
    if not api_key:
        raise Exception('No Google API key provided')

    # Initialize the Gemini Client
    client = genai.Client(api_key=api_key)
    model_name = 'gemini-2.5-flash-lite'

    prompt = '''
    You're an expert sustainability analyst specializing in ESG metrics extraction.
    Extract all relevant metrics, targets, and KPIs from the text and format them to the provided schema.4
    CRITICAL EXTRACTION RULES:
    1. Extract ONLY metrics with actual numeric values
    2. Include the numeric value WITH units in the 'value' field (e.g., '50%', '1,200 tons', '42 hours')
    3. Category must be one of: environmental, emissions, energy, water, waste, social, governance, safety, supply_chain, or other
    4. Metric type should be: target, actual, or baseline
    5. For percentages: include the % symbol (e.g., '28%')
    6. For currency: include currency symbol (e.g., '$14M')
    7. For targets: set metric_type='target' and include target year
    8. For historical data: set metric_type='actual' or 'baseline'

    DO NOT extract:
    - Company names, addresses, or contact information
    - Document titles or report names
    - Generic statements without numbers
    - URLs or email addresses
    
    Text to analyze:
    {text}
    '''

    all_results = []

    try:
        doc = pym.open(filename)
        total_pages = len(doc)

        if MAX_PAGES_TO_PROCESS:
            total_pages = min(total_pages, MAX_PAGES_TO_PROCESS)

        print(f'Processing {total_pages} pages with Gemini in batches of {PAGES_PER_BATCH}...')

        batch_num = 0
        for start_page in range(0, total_pages, PAGES_PER_BATCH):
            batch_num += 1
            end_page = min(start_page + PAGES_PER_BATCH, total_pages)

            batch_text = []
            for page_num in range(start_page, end_page):
                page = doc[page_num]
                text = page.get_text()

                if text and len(text.strip()) >= 100:
                    batch_text.append(f'=== Page {page_num+1} ===\n{text}\n')

            if not batch_text:
                continue

            combined_text = '\n'.join(batch_text)

            try:
                print(f' Batch {batch_num}: Processing Pages {start_page+1}-{end_page} ({len(batch_text)} pages)...')

                response = client.models.generate_content(
                    model = model_name,
                    contents = prompt.format(text = combined_text),
                    config = types.GenerateContentConfig(
                        response_mime_type='application/json',
                        response_schema=list[ExtractedMetrics]
                    )
                )

                parsed = json.loads(response.text)

                if isinstance(parsed, list):
                    batch_results = parsed
                elif isinstance(parsed, dict):
                    batch_results = [parsed]
                else:
                    print(f'Batch {batch_num} unexpected response format')
                    continue

                # Validate and add results
                valid_sections = 0
                for result in batch_results:
                    if "title" in result and "metrics" in result:
                        # Add page reference if not present
                        if not result.get("page_ref"):
                            result["page_ref"] = f"Pages {start_page + 1}-{end_page}"

                        # Validate metrics quality
                        valid_metrics = []
                        for metric in result.get("metrics", []):
                            if _is_valid_metric(metric):
                                valid_metrics.append(metric)
                            else:
                                # Silently filter invalid metrics
                                pass

                        # Only add if we have valid metrics
                        if valid_metrics:
                            result["metrics"] = valid_metrics
                            all_results.append(result)
                            valid_sections += 1

                if valid_sections > 0:
                    total_metrics = sum(len(r["metrics"]) for r in batch_results if "metrics" in r)
                    print(f"    ✓ Found {valid_sections} sections with {total_metrics} metrics")
                else:
                    print(f"    ⚠️  No valid metrics found in this batch")

            except json.JSONDecodeError as e:
                print(f"  ❌ Batch {batch_num}: JSON decode error - {e}")
                continue
            except Exception as e:
                print(f"  ❌ Batch {batch_num}: Error - {e}")
                continue

        doc.close()

        total_metrics = sum(len(r['metrics']) for r in all_results)
        total_sections = len(all_results)
        total_api_calls = batch_num

        print(f"\n✅ Gemini extraction complete:")
        print(f"   • {total_metrics} metrics found")
        print(f"   • {total_sections} sections")
        print(f"   • {total_api_calls} API calls (saved {total_pages - total_api_calls} calls!)")

        return all_results

    except Exception as e:
        print(f"❌ PDF extraction error: {e}")
        raise


def _is_valid_metric(metric: Dict) -> bool:
    """
    Validate that a metric contains actual data, not bogus information.

    Returns:
        True if metric is valid, False otherwise
    """
    # Must have required fields
    if not all(key in metric for key in ["metric_name", "value"]):
        return False

    metric_name = str(metric.get("metric_name", "")).strip()
    value = str(metric.get("value", "")).strip()

    # Filter out empty or very short names
    if not metric_name or len(metric_name) < 3:
        return False

    # Filter out empty values
    if not value or len(value) < 1:
        return False

    # Filter out non-metrics (company metadata, etc.)
    import re
    invalid_patterns = [
        r'^(legal name|company name|organization|report|document|title)',
        r'^(location|address|headquarters|contact|email|phone)',
        r'^(frequency|period|date|year published|reporting period)',
        r'^https?://',
        r'@\w+\.',
        r'^\d{4}\s+(annual|sustainability|report)',
    ]

    metric_name_lower = metric_name.lower()
    for pattern in invalid_patterns:
        if re.search(pattern, metric_name_lower):
            return False

    # Value should not be just a year or date
    if re.match(r'^\d{4}$', value):
        return False

    # Value should not be a URL or document reference
    if any(x in value.lower() for x in ["http", "www.", "report", "document"]):
        return False

    # Value should have some numeric content
    if not re.search(r'\d', value):
        return False

    return True
