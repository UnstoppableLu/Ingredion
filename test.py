import pymupdf4llm as pym
from pathlib import Path

path_obj = Path('sus_reports/Ingredion 2024 Sustainability Report.pdf')
path_str = str(path_obj)

md_text = pym.to_markdown(path_str)
print(md_text)