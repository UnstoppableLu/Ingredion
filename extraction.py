import pymupdf4llm as pymllm
from gemini_extraction import extract_with_gemini
from typing import List, Dict, Tuple, Union


'''
Two extraction methods will be attempted, dependent on the PDF.
1. Markdown extraction allows us to split chunks based on headers
2. Raw text extraction will rip all text from general PDFs
'''

def text_extraction(fn: str) -> Tuple[Union[str, List[Dict]], str]:
    '''
    try:
        md_text = pymllm.to_markdown(fn)
        if len(md_text.strip()) > 100:
            print("Markdown extraction Complete")
            return md_text, 'markdown'

    except Exception as e:
        print(f'Not enough markdown text for extraction: {e}')
    '''
    try:
        print(f'Using Gemini structured output.')
        # we call a method to extract with gemini?
        metrics = extract_with_gemini(fn)
        return metrics, 'gemini_extraction'
    except Exception as e:
        print(f'Gemini extraction failed: {e}')

    return '', 'failed'


