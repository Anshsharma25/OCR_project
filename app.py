import pytesseract
from PIL import Image
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import pandas as pd
import re
import os

app = Flask(__name__)
CORS(app)

# Set the Tesseract executable path if not in system PATH
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
custom_config = r'--oem 3 --psm 6'

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
        extracted_text = pytesseract.image_to_string(image, lang='eng', config=custom_config)
        invoice_data = parse_invoice_text(extracted_text)
        return jsonify({
            'extracted_text': extracted_text,
            'invoice_data': invoice_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def parse_invoice_text(text):
    """
    Extract key invoice fields (including bill-to/from details) using regular expressions.
    Regex patterns may need refinement based on the invoice format.
    """
    invoice_data = {}

    # Invoice & Order Identification
    invoice_number_pattern = r'Invoice Number:\s*([\w\d]+)'
    order_number_pattern = r'Order Number:\s*([\w\d\-]+)'
    packet_id_pattern = r'PackettD:\s*#?([\w\d\-]+)'

    # Dates
    invoice_date_pattern = r'(?:Invoice Date|Tnvoice Date):\s*(\d{1,2}\s\w+\s\d{4})'
    order_date_pattern = r'Order Date:\s*(\d{1,2}\s\w+\s\d{4})'

    # Transaction Details
    nature_transaction_pattern = r'Nature of Transaction:\s*([\w\-]+)'
    nature_supply_pattern = r'Nature of Supply:\s*(\w+)'
    place_supply_pattern = r'Place of Supply:\s*([\w\s]+)'

    # Billing & Shipping Information (multiline capture)
    bill_to_pattern = r'Bl to Ship wo:\s*(.*?)Bl From:'
    bill_from_pattern = r'Bl From:\s*(.*?)GSTIN Number:'
    gstin_pattern = r'GSTIN Number:\s*([\w\d]+)'

    # Itemized Details
    product_pattern = r'(RDTPCASH[\w\(\)\.\-]+)\s*-\s*(.*?),\s*Size:'
    hsn_pattern = r'HSN:\s*(\d+)'

    # Totals
    total_pattern = r'TOTAL\s+(.*)'

    match = re.search(invoice_number_pattern, text, re.IGNORECASE)
    invoice_data['Invoice Number'] = match.group(1).strip() if match else "Not Found"

    match = re.search(order_number_pattern, text, re.IGNORECASE)
    invoice_data['Order Number'] = match.group(1).strip() if match else "Not Found"

    match = re.search(packet_id_pattern, text, re.IGNORECASE)
    invoice_data['Packet/Reference ID'] = match.group(1).strip() if match else "Not Found"

    match = re.search(invoice_date_pattern, text, re.IGNORECASE)
    invoice_data['Invoice Date'] = match.group(1).strip() if match else "Not Found"

    match = re.search(order_date_pattern, text, re.IGNORECASE)
    invoice_data['Order Date'] = match.group(1).strip() if match else "Not Found"

    match = re.search(nature_transaction_pattern, text, re.IGNORECASE)
    invoice_data['Nature of Transaction'] = match.group(1).strip() if match else "Not Found"

    match = re.search(nature_supply_pattern, text, re.IGNORECASE)
    invoice_data['Nature of Supply'] = match.group(1).strip() if match else "Not Found"

    match = re.search(place_supply_pattern, text, re.IGNORECASE)
    invoice_data['Place of Supply'] = match.group(1).strip() if match else "Not Found"

    # Extract Bill To details (name and address)
    match = re.search(bill_to_pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        bill_to_full = match.group(1).strip()
        lines = [line.strip() for line in bill_to_full.splitlines() if line.strip()]
        if lines:
            invoice_data['Bill To Name'] = lines[0]
            invoice_data['Bill To Address'] = " ".join(lines[1:]) if len(lines) > 1 else "Not Found"
        else:
            invoice_data['Bill To Name'] = "Not Found"
            invoice_data['Bill To Address'] = "Not Found"
    else:
        invoice_data['Bill To Name'] = "Not Found"
        invoice_data['Bill To Address'] = "Not Found"

    # Extract Bill From details (name and address)
    match = re.search(bill_from_pattern, text, re.IGNORECASE | re.DOTALL)
    if match:
        bill_from_full = match.group(1).strip()
        lines = [line.strip() for line in bill_from_full.splitlines() if line.strip()]
        if lines:
            invoice_data['Bill From Name'] = lines[0]
            invoice_data['Bill From Address'] = " ".join(lines[1:]) if len(lines) > 1 else "Not Found"
        else:
            invoice_data['Bill From Name'] = "Not Found"
            invoice_data['Bill From Address'] = "Not Found"
    else:
        invoice_data['Bill From Name'] = "Not Found"
        invoice_data['Bill From Address'] = "Not Found"

    match = re.search(gstin_pattern, text, re.IGNORECASE)
    invoice_data['GSTIN Number'] = match.group(1).strip() if match else "Not Found"

    match = re.search(product_pattern, text, re.IGNORECASE)
    if match:
        invoice_data['Item/Product Code'] = match.group(1).strip()
        invoice_data['Product Description'] = match.group(2).strip()
    else:
        invoice_data['Item/Product Code'] = "Not Found"
        invoice_data['Product Description'] = "Not Found"

    match = re.search(hsn_pattern, text, re.IGNORECASE)
    invoice_data['HSN/SAC Code'] = match.group(1).strip() if match else "Not Found"

    match = re.search(total_pattern, text, re.IGNORECASE)
    invoice_data['Totals'] = match.group(1).strip() if match else "Not Found"

    return invoice_data

@app.route('/download-excel', methods=['POST'])
def download_excel():
    # Get the original invoice data from the request
    invoice_data = request.json.get('invoice_data', {})
    if not invoice_data:
        return jsonify({'error': 'No data to save'}), 400

    # Build ordered groups (Serial Number removed)
    ordered_groups = {
        "Person Details": {
            "Bill To Name": invoice_data.get("Bill To Name", "Not Found"),
            "Bill To Address": invoice_data.get("Bill To Address", "Not Found"),
            "Bill From Name": invoice_data.get("Bill From Name", "Not Found"),
            "Bill From Address": invoice_data.get("Bill From Address", "Not Found")
        },
        "Invoice & Order Identification": {
            "Invoice Number": invoice_data.get("Invoice Number", "Not Found"),
            "Order Number": invoice_data.get("Order Number", "Not Found"),
            "Packet/Reference ID": invoice_data.get("Packet/Reference ID", "Not Found")
        },
        "Dates": {
            "Invoice Date": invoice_data.get("Invoice Date", "Not Found"),
            "Order Date": invoice_data.get("Order Date", "Not Found")
        },
        "Transaction Details": {
            "Nature of Transaction": invoice_data.get("Nature of Transaction", "Not Found"),
            "Nature of Supply": invoice_data.get("Nature of Supply", "Not Found"),
            "Place of Supply": invoice_data.get("Place of Supply", "Not Found")
        },
        "Billing & Shipping Information": {
            "GSTIN Number": invoice_data.get("GSTIN Number", "Not Found")
        },
        "Itemized Details": {
            "Item/Product Code": invoice_data.get("Item/Product Code", "Not Found"),
            "Product Description": invoice_data.get("Product Description", "Not Found"),
            "HSN/SAC Code": invoice_data.get("HSN/SAC Code", "Not Found")
        },
        "Totals": {
            "Totals": invoice_data.get("Totals", "Not Found")
        }
    }

    # For each group, build a comma-separated string of fields
    grouped_data = {}
    for group, fields in ordered_groups.items():
        items = [f"{field}: {fields[field]}" for field in fields]
        grouped_data[group] = ", ".join(items)

    # Create a DataFrame with one row; columns are ordered as in ordered_groups
    df = pd.DataFrame([grouped_data], columns=list(ordered_groups.keys()))
    output_path = 'invoice_data.xlsx'
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Invoice Data')
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
