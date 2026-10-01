from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader

BASE_DIR = Path(__file__).resolve().parent.parent
PDF_PATH = BASE_DIR / "data" / "politica_rh.pdf"

def load_pdf():
    pdf_loader = PyPDFLoader(str(PDF_PATH))
    text = pdf_loader.load()
    return text

document = load_pdf()
