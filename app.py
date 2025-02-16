import pytesseract
from PIL import Image
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import re
import io

app = Flask(__name__)
CORS(app)

# Set the Tesseract executable path if not in system PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# OCR Configuration for better accuracy
custom_config = r'--oem 3 --psm 6'  # OCR Engine Mode (OEM) & Page Segmentation Mode (PSM)

@app.route('/')
def home():
    return send_file('index.html')

@app.route('/ocr', methods=['POST'])
def ocr():
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400

    try:
        image = Image.open(file.stream).convert('RGB')

        # Extract structured OCR data
        extracted_text = pytesseract.image_to_string(image, lang='eng', config=custom_config)

        # Parse the extracted text to find invoice details
        invoice_data = parse_invoice_text(extracted_text)

        # Save extracted data to an Excel file
        excel_data = save_to_excel(invoice_data)

        return jsonify({'extracted_text': extracted_text, 'invoice_data': invoice_data, 'excel_data': excel_data})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': str(e)}), 500

def parse_invoice_text(text):
    """
    Extracts structured invoice details using regex patterns.
    """
    invoice_data = {}

    patterns = {
        'Brand Name': r'Brand Name:\s*(.*)',
        'Invoice Number': r'Invoice Number:\s*(\w+)',
        'Date': r'Date:\s*(\d{2}/\d{2}/\d{4})',
        'Total Amount': r'Total Amount:\s*\$?([\d,]+\.\d{2})'
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            invoice_data[key] = match.group(1).strip()
        else:
            invoice_data[key] = "Not Found"

    return invoice_data

def save_to_excel(data):
    """
    Saves the extracted invoice data to an Excel file and returns the binary data for preview.
    """
    df = pd.DataFrame([data])

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Invoice Data')

    output.seek(0)
    return df.to_dict(orient='records')  # Returning data to be displayed in frontend

if __name__ == '__main__':
    app.run(debug=True)
