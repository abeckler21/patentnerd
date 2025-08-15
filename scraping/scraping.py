# brew install poppler
# brew install tesseract
import re
import tempfile
import pdfplumber
import pytesseract
from pdf2image import convert_from_path

# Common INID code patterns for metadata
INID_CODES = {
    'title': r'\(54\)\s*(.*)',
    'abstract': r'\(57\)\s*(.*)',
    'patent_number': r'\(11\)\s*(.*)',
    'application_number': r'\(21\)\s*(.*)',
    'priority_claim': r'\(30\)\s*(.*?)(?:\n\(|$)',
    'issue_date': r'\(45\)\s*(.*)',
    'inventor': r'\(72\)\s*(.*)',
    'assignee': r'\(71\)\s*(.*)',
}

# Free-text section headings (these vary by patent)
TEXT_SECTIONS = [
    'Background of the Invention',
    'Summary of the Invention',
    'Brief Description of the Invention',
    'Brief Description of the Figures',
    'Detailed Description of the Invention'
]

def remove_line_numbers(text):
    """Remove line numbers from patent text."""
    return re.sub(r'^\s*\d+\s+', '', text, flags=re.MULTILINE)

def extract_inid_metadata(first_page_text):
    """Extract metadata using INID codes."""
    data = {}
    for key, pattern in INID_CODES.items():
        m = re.search(pattern, first_page_text)
        data[key] = m.group(1).strip() if m else ''
    return data

def extract_text_sections(full_text):
    """Extract text for known sections."""
    data = {}
    for i, section in enumerate(TEXT_SECTIONS):
        pat = rf"{re.escape(section)}\s*(.*?)(?=\n(?:{'|'.join(map(re.escape, TEXT_SECTIONS[i+1:]))})|\Z)"
        m = re.search(pat, full_text, flags=re.S | re.I)
        data[section.lower().replace(' ', '_')] = m.group(1).strip() if m else ''
    return data

def extract_claims(full_text):
    """Find the last '1.' numbered list and grab until end."""
    text = remove_line_numbers(full_text)
    matches = list(re.finditer(r'\n\s*1\.\s+', text))
    if not matches:
        return ""
    start_index = matches[-1].start()
    return text[start_index:].strip()

def pdf_to_text_ocr(pdf_path):
    """Convert PDF to text using OCR."""
    text_pages = []
    with tempfile.TemporaryDirectory() as tempdir:
        images = convert_from_path(pdf_path, dpi=300, output_folder=tempdir)
        for img in images:
            page_text = pytesseract.image_to_string(img)
            text_pages.append(page_text)
    return "\n".join(text_pages), text_pages[0] if text_pages else ""

def get_pdf_text(pdf_path):
    """Try pdfplumber first; if no text found, use OCR."""
    with pdfplumber.open(pdf_path) as pdf:
        pages = [page.extract_text() or '' for page in pdf.pages]
    full_text = "\n".join(pages)
    first_page_text = pages[0] if pages else ""

    # Check if we actually got text (not just whitespace)
    if len(full_text.strip()) < 50:
        print(f"[INFO] No readable text found in {pdf_path}. Using OCR...")
        full_text, first_page_text = pdf_to_text_ocr(pdf_path)

    return full_text, first_page_text

def extract_patent_sections(pdf_path):
    """Main function to extract all required sections."""

    """ 
    TODO: FOR FIRST TIME READING A PATENT, PLEASE UNCOMMENT THE FOLLOWING
    It is annoying to have to do all the converting from pdf to txt so I'm saving it
    and can write the code to delete the txt file later. 

    full_text, first_page_text = get_pdf_text(pdf_path)
    cleaned_full_text_to_save = remove_line_numbers(full_text)
    print(cleaned_full_text_to_save)

    # Save the text to a file
    with open(f"cleaned_{fname}.txt", "w", encoding="utf-8") as f:
        f.write(cleaned_full_text_to_save)
    """

    # Load text from file
    with open(f"cleaned_{fname}.txt", "r", encoding="utf-8") as f:
        cleaned_full_text = f.read()

        # Replace single newlines with a space, but keep double newlines
        cleaned_full_text_condensed = cleaned_full_text.replace("\r\n", "\n")

        #   Replace single newlines that are not part of double newlines
        cleaned_full_text_condensed = re.sub(r'(?<!\n)\n(?!\n)', ' ', cleaned_full_text_condensed)

    # 1. Metadata
    data = extract_inid_metadata(cleaned_full_text_condensed)
    print(data)

    # # 2. Descriptive sections
    # section_data = extract_text_sections(cleaned_full_text)
    # data.update(section_data)

    # # 3. Claims
    # data['claims'] = extract_claims(full_text)

    # # Print in sequence
    # output_order = [
    #     'abstract', 'priority_claim',
    #     'background_of_the_invention', 'summary_of_the_invention',
    #     'brief_description_of_the_invention', 'brief_description_of_the_figures',
    #     'detailed_description_of_the_invention', 'inventor',
    #     'application_number', 'patent_number', 'title',
    #     'issue_date', 'assignee', 'claims'
    # ]
    # for key in output_order:
    #     print(f"{key.replace('_', ' ').title()}:\n{data.get(key, '')}\n{'-'*60}")

    # return data

# Example usage:
fname = "8825984.pdf"
extract_patent_sections(fname)
# extract_patent_sections("/mnt/data/7885983.pdf")
