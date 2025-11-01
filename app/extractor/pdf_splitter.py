from PyPDF2 import PdfReader, PdfWriter
from pathlib import Path

def split_pdf(input_path, output_dir, pages_per_part=5):
    reader = PdfReader(input_path)
    total_pages = len(reader.pages)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    part_files = []

    for i in range(0, total_pages, pages_per_part):
        writer = PdfWriter()
        for j in range(i, min(i + pages_per_part, total_pages)):
            writer.add_page(reader.pages[j])

        part_path = output_dir / f"part_{i//pages_per_part + 1}.pdf"
        with open(part_path, "wb") as f:
            writer.write(f)
        part_files.append(part_path)

    return part_files
