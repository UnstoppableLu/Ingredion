from typing import List, Dict
from PyPDF2 import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter

class PDFParser:
    def __init__(self, chunk_size: int = 4000, chunk_overlap: int = 200):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len
        )
    
    def extract_text(self, file_path: str) -> List[str]:
        """Extract text from PDF and split into chunks."""
        try:
            with open(file_path, 'rb') as file:
                pdf = PdfReader(file)
                text = ''
                for page in pdf.pages:
                    text += page.extract_text()
                
                # Split text into chunks
                chunks = self.text_splitter.split_text(text)
                return chunks
        except Exception as e:
            raise Exception(f"Error extracting text from PDF: {str(e)}")
    
    def get_document_info(self, file_path: str) -> Dict:
        """Get basic information about the PDF document."""
        try:
            with open(file_path, 'rb') as file:
                pdf = PdfReader(file)
                info = {
                    'num_pages': len(pdf.pages),
                    'metadata': pdf.metadata
                }
                return info
        except Exception as e:
            raise Exception(f"Error getting document info: {str(e)}")