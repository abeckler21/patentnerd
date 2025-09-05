import os
import re
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import time
from datetime import datetime
import traceback
import re
import tempfile
import pdfplumber
import pytesseract
from pdf2image import convert_from_path

# Set the working directory to the project root (Code directory)
# os.chdir(os.path.dirname(os.path.abspath(__file__)))

from Code.base.clause_comparison import clause_comparison
from Code.base.scraping import get_pdf_text, extract_claims

app = Flask(__name__, template_folder = 'ui/templates')

# Get the project root directory
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Folder where uploaded files are stored
UPLOAD_FOLDER      = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Function to check allowed file extensions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    """Render the homepage."""
    return render_template('index.html')

@app.route('/about')
def about():
    """Render the about page."""
    return render_template('about.html')


@app.route('/analyze', methods=['POST'])
def analyze():
    """Enhanced clause analysis endpoint with improved parsing and features"""
    try:
        # Input validation
        patent_file = request.files.get('patent')

        # File handling
        patent_path = None
        if patent_file and allowed_file(patent_file.filename):
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            patent_filename = secure_filename(patent_file.filename)
            patent_path = os.path.join(app.config['UPLOAD_FOLDER'], patent_filename)
            patent_file.save(patent_path)
            print(f"Processing patent: {patent_path}")
        
        patent_text = get_pdf_text(patent_file)
        claims = extract_claims(patent_text)
        print(claims)

        # Prepare legal references
    #     legal_resources = {
    #         'regulations': os.path.join(project_root, 'Data', 'Regulations',
    #                                     patent_type, jurisdiction, 'regulations.pdf'),
    #         'risky_clauses': os.path.join(project_root, 'Data', 'Risky Clauses',
    #                                       patent_type, jurisdiction, 'risky_clauses.txt')
    #     }

    #     # Enhanced analysis pipeline
    #     analysis_start = time.time()
    #     final_evaluation = clause_comparison(
    #         patent_path = patent_path,
    #         law_path      = legal_resources['regulations'],
    #         risky_clauses = legal_resources['risky_clauses'],
    #         model         = 'Meta-Llama-3.3-70B-Instruct',
    #         role          = "user",
    #         api_key       = "893bd5f1-b41e-4d17-ab1d-3ee3c7cba82b",
    #         api_base      = "https://api.sambanova.ai/v1",
    #         temperature   = 0.1,
    #         top_p         = 0.1,
    #         max_tokens    = 8192
    #     )
    #     print(f"Analysis completed in {time.time() - analysis_start:.2f}s")

    #     # Parse enhanced output format
    #     clauses = []
    #     current_clause = None
        
    #     for line in final_evaluation.split('\n'):
    #         line = line.strip()
    #         if not line:
    #             continue
        
    #         # New clause detection - handles both formats
    #         if line.startswith('### Clause') or re.match(r'^\d+\.', line):
    #             if current_clause:
    #                 clauses.append(current_clause)
                
    #             # Extract clause number from either format
    #             if line.startswith('### Clause'):
    #                 clause_num = line.replace('### Clause', '').strip()
    #             else:  # numbered format
    #                 clause_num = line.split('.', 1)[0].strip()
                
    #             current_clause = {
    #                 'number': clause_num,
    #                 'text': '',
    #                 'classification': None,
    #                 'risk_tier': None,
    #                 'details': {
    #                     'regulations': None,
    #                     'linguistic_traits': None,
    #                     'explanation': None,
    #                     'improvement_guidance': None
    #                 }
    #             }
                
    #             # Extract clause text if present in this line
    #             if 'Clause:' in line:
    #                 text_part = line.split('Clause:', 1)[1].strip()
    #                 if text_part:  # Only set if there's actual text
    #                     current_clause['text'] = text_part.strip('"')
                        
    #         elif current_clause:
    #             # Field detection - works for both formats
    #             if line.startswith('Clause:') and not current_clause['text']:
    #                 current_clause['text'] = line.split('Clause:', 1)[1].strip().strip('"')
    #             elif line.startswith('Regulation(s) Implicated:'):
    #                 current_clause['details']['regulations'] = line.split(':', 1)[1].strip()
    #             elif line.startswith('Classification:'):
    #                 classification = line.split(':', 1)[1].strip()
    #                 current_clause['classification'] = classification
    #                 current_clause['is_unenforceable'] = 'Unenforceable' in classification
    #             elif line.startswith('Risk Tier:'):
    #                 current_clause['risk_tier'] = line.split(':', 1)[1].strip()
    #             elif line.startswith('Linguistic Traits Identified:'):
    #                 current_clause['details']['linguistic_traits'] = line.split(':', 1)[1].strip() or 'None listed'
    #             elif line.startswith('Explanation of Classification:'):
    #                 current_clause['details']['explanation'] = line.split(':', 1)[1].strip()
    #             elif line.startswith('Improvement Guidance:'):
    #                 current_clause['details']['improvement_guidance'] = line.split(':', 1)[1].strip()
        
    #     # Add final clause if exists
    #     if current_clause:
    #         clauses.append(current_clause)

    #     # Generate analysis metadata
    #     analysis_metadata = {
    #         'jurisdiction': jurisdiction,
    #         'patent_type': patent_type,
    #         'timestamp': datetime.now().isoformat(),
    #         'clause_count': len(clauses),
    #         'unenforceable_count': sum(1 for c in clauses if c.get('is_unenforceable'))
    #     }

    #     print("DEBUG: Extracted clauses ->", analysis_metadata)

    #     return jsonify({
    #         "metadata": analysis_metadata,
    #         "clauses": clauses,
    #         "raw": final_evaluation,
    #         "legal_resources": legal_resources
    #     })

    except Exception as e:
        app.logger.error(f"Analysis error: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Analysis failed",
            "message": str(e),
            "trace": traceback.format_exc() if app.debug else None
        }), 500

if __name__ == "__main__":
    app.run(debug=True)
