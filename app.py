import pytesseract
from PIL import Image
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import re

app = Flask(__name__)
CORS(app)

# Set the Tesseract executable path if not in system PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

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
        extracted_text = pytesseract.image_to_string(image, lang='eng')

        # Parse the extracted text to find invoice details
        invoice_data = parse_invoice_text(extracted_text)

        # Save the extracted data to an Excel file
        save_to_excel(invoice_data, 'invoice_data.xlsx')

        return jsonify({'extracted_text': extracted_text, 'invoice_data': invoice_data})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': str(e)}), 500

def parse_invoice_text(text):
    """
    Parse the extracted text to find specific invoice details.
    This function uses regular expressions to locate details like brand name, invoice number, date, and total amount.
    """
    invoice_data = {}

    # Example regex patterns (these may need to be adjusted based on the invoice format)
    brand_name_pattern = r'Brand Name:\s*(.*)'
    invoice_number_pattern = r'Invoice Number:\s*(\w+)'
    date_pattern = r'Date:\s*(\d{2}/\d{2}/\d{4})'
    total_amount_pattern = r'Total Amount:\s*\$?([\d,]+\.\d{2})'

    # Search for patterns in the text
    brand_name_match = re.search(brand_name_pattern, text, re.IGNORECASE)
    invoice_number_match = re.search(invoice_number_pattern, text, re.IGNORECASE)
    date_match = re.search(date_pattern, text, re.IGNORECASE)
    total_amount_match = re.search(total_amount_pattern, text, re.IGNORECASE)

    # Extract and store the matched values
    if brand_name_match:
        invoice_data['Brand Name'] = brand_name_match.group(1).strip()
    if invoice_number_match:
        invoice_data['Invoice Number'] = invoice_number_match.group(1).strip()
    if date_match:
        invoice_data['Date'] = date_match.group(1).strip()
    if total_amount_match:
        invoice_data['Total Amount'] = total_amount_match.group(1).strip()

    return invoice_data

def save_to_excel(data, filename):
    """
    Save the extracted invoice data to an Excel file.
    """
    df = pd.DataFrame([data])
    df.to_excel(filename, index=False)

if __name__ == '__main__':
    app.run(debug=True)
