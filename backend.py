from pathlib import Path
import logging
from pdfminer.high_level import extract_text
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import pdfplumber
import fitz
import re
import spacy
import contractions

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PDF_MUPDF_AVAILABLE = True
except ImportError:
    PDF_MUPDF_AVAILABLE = False

class FileParserError(Exception):
    pass

class Parser:
    """
    A comprehensive parser for document and PDF files 
    Supports multiple PDF parsing libraries for better compatibility
    """

    def __init__(self):
        self.supported_extensions = {'.txt', '.text', '.pdf'}

    def parse_file(self, file_path):
        """
        Main method to parse any supported file type
        """
        if hasattr(file_path, 'read'):
            # Handle file-like objects (uploaded files)
            if hasattr(file_path, 'name'):
                extension = Path(file_path.name).suffix.lower()
            else:
                # Assume PDF if no extension available
                extension = '.txt'
            
            if extension not in self.supported_extensions:
                raise FileParserError(f"Unsupported file type: {extension}")
            
            try:
                if extension == '.pdf':
                    return self._parse_pdf_file(file_path)
                else:
                    return self._parse_text_file(file_path)
            except Exception as e:
                raise FileParserError(f"Error parsing file: {str(e)}")
        else:
            # Handle file paths
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileParserError(f"File not found: {file_path}")
            
            if not file_path.is_file():
                raise FileParserError(f"Given path is not a file: {file_path}")
            
            extension = file_path.suffix.lower()
            
            if extension not in self.supported_extensions:
                raise FileParserError(f"Unsupported file type: {extension}")
            
            try:
                if extension == '.pdf':
                    return self._parse_pdf_file(file_path)
                else:
                    return self._parse_text_file(file_path)
            except Exception as e:
                raise FileParserError(f"Error parsing file {file_path}: {str(e)}")
        
    def _parse_pdf_file(self, file_path):
        methods = []
        
        if PDFPLUMBER_AVAILABLE:
            methods.append(self._parse_pdf_with_plumber)
        if PDF_MUPDF_AVAILABLE:
            methods.append(self._parse_pdf_with_mupdf)
        if PDF_PYPDF2_AVAILABLE:
            methods.append(self._parse_pdf_with_pdfminer)

        if not methods:
            raise FileParserError("No PDF parsing library is available. Please install pdfplumber, PyMuPDF, or pdfminer.six")
        
        last_error = None
        for method in methods:
            try:
                return method(file_path)
            except Exception as e:
                last_error = e
                logging.warning(f"PDF parsing method failed: {method.__name__}, trying next method...")
                continue
        
        raise FileParserError(f"All PDF parsing methods failed. Last error: {last_error}")
    
    def _parse_pdf_with_plumber(self, file_path):
        """Parse PDF with pdfplumber (best for complex layouts)"""
        text_content = []

        # Handle both file paths and file-like objects
        if hasattr(file_path, 'read'):
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append({
                            'page_number': page_num,
                            'text': page_text.strip()
                        })
        else:
            with pdfplumber.open(str(file_path)) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append({
                            'page_number': page_num,
                            'text': page_text.strip()
                        })
        
        full_text = '\n\n'.join([page['text'] for page in text_content])
        full_text = self.preprocess_text(full_text)
        full_text = self.summury_generated(full_text)
        return full_text

    def _parse_pdf_with_mupdf(self, file_path):
        """Parse PDF using PyMuPDF (fast and reliable)"""
        
        # Handle both file paths and file-like objects
        if hasattr(file_path, 'read'):
            # For file-like objects, we need to get the bytes
            content = file_path.read()
            if hasattr(file_path, 'seek'):
                file_path.seek(0)  # Reset file pointer
            doc = fitz.open(stream=content, filetype="pdf")
        else:
            doc = fitz.open(str(file_path))
        
        text_content = []

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            if text.strip():
                text_content.append({
                    'page_number': page_num + 1,
                    'text': text.strip()
                })
        doc.close()
        
        full_text = '\n\n'.join([p['text'] for p in text_content])
        full_text = self.preprocess_text(full_text)
        full_text = self.summury_generated(full_text)
        return full_text

    def _parse_pdf_with_pdfminer(self, file_path):
        """Parse PDF with pdfminer.six (robust text extraction)"""
        try:
            # Handle both file paths and file-like objects
            if hasattr(file_path, 'read'):
                full_text = extract_text(file_path)
            else:
                full_text = extract_text(str(file_path))
            
            # Preprocess text
            full_text = self.preprocess_text(full_text)
            full_text = self.summury_generated(full_text)
            return full_text

        except Exception as e:
            print(f"[ERROR] PDFMiner failed to parse: {e}")
            raise e
    
    def _parse_text_file(self, file_path):
        encodings = ['utf-8', 'utf-16', 'latin-1', 'cp1252']
        
        # Handle both file paths and file-like objects
        if hasattr(file_path, 'read'):
            raw_bytes = file_path.read()
            if isinstance(raw_bytes, str):
                # Already decoded
                content = raw_bytes
            else:
                content = None
                for encoding in encodings:
                    try:
                        content = raw_bytes.decode(encoding)
                        break
                    except UnicodeDecodeError:
                        continue
        else:
            with open(file_path, 'rb') as f:
                raw_bytes = f.read()
            content = None
            for encoding in encodings:
                try:
                    content = raw_bytes.decode(encoding)
                    break
                except UnicodeDecodeError:
                    continue

        if content is None:
            raise FileParserError(f"Could not decode text file with any supported encoding")
        
        processed_content = self.preprocess_text(content)
        processed_content = self.summury_generated(processed_content)
        return processed_content
    
    def preprocess_text(self, text):
        # Load small English model
        nlp = spacy.load("en_core_web_sm")
        # 1. Remove URLs and promotional lines
        text = re.sub(r"http\S+|www\S+|watch.*?»", "", text, flags=re.IGNORECASE)

        # 2. Remove boilerplate/copyright notices
        text = re.sub(r"Copyright.*?reserved\.", "", text, flags=re.IGNORECASE)
        text = re.sub(r"This material.*?redistributed", "", text, flags=re.IGNORECASE)

        # 3. Normalize quotes/apostrophes
        text = text.replace("’", "'").replace("‘", "'")
        text = text.replace("“", '"').replace("”", '"')

        # 4. Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()

        # Fix lowercase 'i' when it’s a pronoun
        text = re.sub(r"\bi\b", "I", text)

        # Remove trailing junk
        text = re.sub(r"E-mail to a friend\s*\.*", "", text, flags=re.IGNORECASE)
        text = re.sub(r'[^\x00-\x7F]+', ' ', text)
        text = re.sub(r"\.\.+", ".", text)
        text = re.sub(r"\b\w\b", "", text)  # Remove single-letter tokens (can hurt if text has acronyms)
        text = contractions.fix(text)

        # 5. Sentence segmentation using spaCy
        doc = nlp(text)
        sentences = [sent.text.strip().capitalize() for sent in doc.sents if sent.text.strip()]
        
        # 6. Join cleaned sentences
        clean_text = " ".join(sentences)

        return clean_text

    def summury_generated(self, text):

        model = "google/long-t5-tglobal-base"
        tokenizer = AutoTokenizer.from_pretrained(model)
        model = AutoModelForSeq2SeqLM.from_pretrained(model)

        text = "summarize: " + text
        inputs = tokenizer(text, return_tensors="pt", max_length=4096, truncation=True)

        summary_ids = model.generate(inputs["input_ids"], max_length=256, num_beams=4, early_stopping=True)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)

        return summary