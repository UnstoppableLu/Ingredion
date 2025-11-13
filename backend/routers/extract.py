from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from services.pdf_parser import PDFParser
from services.gemini_extractor import MetricsExtractor
from pathlib import Path
import json

router = APIRouter()

@router.post("/extract")
async def extract_metrics_endpoint(
    file: UploadFile = File(...),
    company: str = Form(...),
    year: int = Form(...),
    force: bool = Form(default=False)
):
    company = company.lower().replace(" ", "_")

    output_dir = Path("data/extracted")
    output_dir.mkdir(parents=True, exist_ok=True)
    save_path = output_dir / f"{company}_{year}.json"

    temp_path = Path("temp_uploads") / file.filename
    temp_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        if save_path.exists() and not force:
            return {
                "status": "exists",
                "file_exists": True,
                "message": f"A report for {company.title()} {year} already exists. Replace it?",
                "existing_file": str(save_path)
            }
        
        with open(temp_path, "wb") as f:
            f.write(await file.read())

        pdf_parser = PDFParser()
        chunks = pdf_parser.extract_text(str(temp_path))

        extractor = MetricsExtractor()
        metrics = extractor.extract_metrics(
            [{"page_number": i+1, "text": t} for i, t in enumerate(chunks)]
        )

        with open(save_path, "w") as f:
            json.dump(metrics, f, indent=2)

        return {
            "status": "success",
            "saved_to": str(save_path),
            "company": company,
            "year": year,
            "metrics": metrics
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing error: {str(e)}")
    
    finally:
        if temp_path.exists():
            temp_path.unlink()