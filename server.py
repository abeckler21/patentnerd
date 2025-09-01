from http.server import HTTPServer, SimpleHTTPRequestHandler
import cgi
from scraping import get_pdf_text, extract_claims
import os

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class Handler(SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == "/upload":
            ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
            if ctype == 'multipart/form-data':
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={'REQUEST_METHOD':'POST',
                             'CONTENT_TYPE':self.headers['Content-Type'],
                             }
                )
                file_item = form['pdf_file']
                if file_item.filename:
                    # Set file paths
                    filename = os.path.basename(file_item.filename)
                    filepath_pdf = os.path.join(UPLOAD_FOLDER, filename)
                    filepath_txt = os.path.join(UPLOAD_FOLDER, f"{filename}.txt")

                    # Check if TXT already exists
                    if os.path.exists(filepath_txt):
                        # Read text from existing TXT file
                        with open(filepath_txt, 'r', encoding='utf-8') as f:
                            full_text = f.read()
                    else:
                        # Save uploaded PDF
                        with open(filepath_pdf, 'wb') as f:
                            f.write(file_item.file.read())
                        # Extract text from PDF
                        full_text, _ = get_pdf_text(filepath_pdf)
                        # Save text to TXT file
                        with open(filepath_txt, 'w', encoding='utf-8') as f:
                            f.write(full_text)

                    # Extract claims
                    claims = extract_claims(full_text)

                    # Send response
                    self.send_response(200)
                    self.send_header("Content-type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(claims.encode('utf-8'))
                else:
                    self.send_error(400, "No file uploaded")
            else:
                self.send_error(400, "Invalid form data")
        else:
            self.send_error(404, "Path not found")

if __name__ == "__main__":
    server_address = ("", 8000)
    httpd = HTTPServer(server_address, Handler)
    print("Serving on http://localhost:8000")
    httpd.serve_forever()
