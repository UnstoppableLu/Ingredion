from extraction import text_extraction
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from prompting import process
import pandas as pd
import json
from pathlib import Path

#Specify which file you want to extract from
fn = 'Ingredion 2024 Sustainability Report' # Change to report you wish to extract
file_path = f'sus_reports/{fn}.pdf'
json_path = f'json_results/{fn}.json'

# Check if extracted Json file exists
if not Path(json_path).is_file():
    text, method = text_extraction(file_path)
    # Split the text based on the most optimal method
    if method == 'markdown':
        headers_to_split_on = [
            ('#', 'Header 1'),
            ('##', 'Header 2'),
            ('###', 'Header 3'),
        ]
        markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
        docs = markdown_splitter.split_text(text)

        results = process(docs)
        print(results)

    elif method == 'gemini_extraction':
        print('Using Gemini structured output.')
        # method will be gemini_structured
        results = text
    else:
        print('Failed')
        exit(1)

    flattened_data = []
    for result in results:
        # Handle both dict (Gemini) and object (LangChain) formats
        if isinstance(result, dict):
            title = result.get('title')
            page_ref = result.get('page_ref')
            metrics = result.get('metrics', [])
        else:
            title = result.title
            page_ref = result.page_ref
            metrics = result.metrics

        if not metrics:
            continue

        for metric in metrics:
            # Handle both dict and object formats
            if isinstance(metric, dict):
                flattened_data.append({
                    'title': title,
                    'page_ref': page_ref,
                    'category': metric.get('category'),
                    'name': metric.get('metric_name'),
                    'value': metric.get('value'),
                    'year': metric.get('year'),
                    'type': metric.get('metric_type'),
                    'scope': metric.get('scope'),
                    'unit': metric.get('unit'),
                })
            else:
                flattened_data.append({
                    'title': title,
                    'page_ref': page_ref,
                    'category': metric.category,
                    'name': metric.metric_name,
                    'value': metric.value,
                    'year': metric.year,
                    'type': metric.metric_type,
                    'scope': metric.scope,
                    'unit': metric.unit,
                })

    # save the flattened results to a directory
    directory_path = Path('json_results')
    if not directory_path.is_dir():
        directory_path.mkdir(parents=True, exist_ok=True)

    with open(json_path, 'w') as json_file:
        json.dump(flattened_data, json_file, indent=3)

    print(f'Saved JSON to {json_path}')

    df = pd.DataFrame(flattened_data)
    print(df)
else:
    print("File Previously Extracted")
    df = pd.read_json(json_path)
    print(df)

# convert the df to a csv and save to a directory
csv_directory_path = Path('csv_results')
if not csv_directory_path.is_dir():
    csv_directory_path.mkdir(parents=True, exist_ok=True)

df.to_csv(csv_directory_path / f'{fn}Gemini.csv', index=False)