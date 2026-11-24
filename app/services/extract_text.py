from pathlib import Path
import fitz
from docx import Document
class ExtractionError(ValueError):pass
def extract_text(data:bytes, filename:str)->tuple[str,str]:
    ext=Path(filename).suffix.lower()
    if ext=='.pdf':
        try:doc=fitz.open(stream=data,filetype='pdf')
        except Exception as e:raise ExtractionError('The PDF file is invalid or damaged. Please export it again and retry.') from e
        pages=[p.get_text() for p in doc]; text='\n'.join(pages)
        if not text.strip():
            try:
                import pytesseract
                from PIL import Image
                import io
                text='\n'.join(pytesseract.image_to_string(Image.open(io.BytesIO(p.get_pixmap().tobytes('png')))) for p in doc)
            except Exception as e: raise ExtractionError('This PDF appears scanned and no working OCR engine is installed. Install Tesseract + pytesseract, then retry.') from e
        return text,'pymupdf'
    if ext=='.docx':
        import io
        try:return '\n'.join(p.text for p in Document(io.BytesIO(data)).paragraphs),'python-docx'
        except Exception as e:raise ExtractionError('The DOCX file is invalid or damaged. Please export it again and retry.') from e
    if ext in ('.txt','.md'):return data.decode('utf-8',errors='replace'),'plain_text'
    if ext in ('.png','.jpg','.jpeg'):
        try:
            import pytesseract
            from PIL import Image
            import io
            return pytesseract.image_to_string(Image.open(io.BytesIO(data))),'tesseract_ocr'
        except Exception as e:raise ExtractionError('Image OCR is unavailable. Install Tesseract and pytesseract to parse PNG/JPG files.') from e
    raise ExtractionError('Unsupported file type. Upload PDF, DOCX, TXT, PNG or JPG.')
