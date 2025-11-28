import PyPDF2
from pathlib import Path
import re

class PDFParser:
    """Extract text from academic paper PDFs"""

    def __init__(self, pdf_path):
        self.pdf_path = Path(pdf_path)
    
    def extract_text(self, max_pages = 10):
        """Extract text from first N pages of PDF"""
        try:
            with open(self.pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                num_pages = min(max_pages, len(reader.pages))
                
                for page_num in range(num_pages):
                    text += reader.pages[page_num].extract_text() + "\n"
                
                return text
        except Exception as e:
            print(f"Error reading {self.pdf_path}: {e}")
            return ""
 