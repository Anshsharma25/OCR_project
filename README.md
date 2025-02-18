 # 🚀 Invoice Data Extraction Hub

Welcome to **Invoice Data Extraction Hub** – a cutting-edge solution to transform your invoice images into structured data seamlessly! This project combines advanced OCR, smart text processing, and a slick API & frontend interface to automate invoice processing like a pro. 💡✨

---

## 🔧 Tech Stack & Dependencies

- **Programming Language:** Python 3.x  
- **OCR Engine:** [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) 🤖  
- **Image Processing:** OpenCV  
- **Data Handling:** Pandas & Openpyxl  
- **API Framework:** Flask 🐍  
- **Frontend:** HTML5 & CSS3 🎨

---

## 🛠️ Setup & Installation

1. **Install Tesseract OCR:**  
   - **Windows:** Download from [Tesseract at UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki) 🖥️  
   - **Linux:**  
     ```bash
     sudo apt-get install tesseract-ocr
     ```  
   - **macOS:**  
     ```bash
     brew install tesseract
     ```

2. **Clone the Repository:**
   ```bash
   git clone https://github.com/yourusername/InvoiceExtractionHub.git
   cd InvoiceExtractionHub

Install Python Dependencies:
~~~
pip install opencv-python pytesseract pandas openpyxl flask
~~~

Configure Tesseract Path:
~~~
Update the Tesseract executable path in your configuration (e.g., in your Python scripts):
~~~
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
~~~
📁 Project Structure

InvoiceExtractionHub/
├── app.py                 # Flask API application 🚀
├── invoice_extraction.py  # Core invoice extraction logic 📄
├── templates/
│   └── index.html         # Frontend HTML file 🌐
├── static/
│   └── styles.css         # Custom CSS for frontend 🎨
├── output.xlsx            # Auto-generated Excel file 📊
└── README.md              # This file 📚
~~~~


⚡ How It Works
Image Processing:
Reads your invoice image and applies grayscale conversion (and optional thresholding) to optimize OCR accuracy.

# OCR Extraction:
Tesseract OCR converts the processed image into raw text.

# Smart Parsing:
Custom regular expressions extract all the vital invoice details (Invoice Number, Date, Order Number, Seller & Buyer info, GSTIN/PAN, Total Amount, Taxes) from the cleaned text.

# Data Presentation:
The parsed information is displayed in a neat table on the frontend and can be exported to Excel.

# API Interaction:
Upload your invoice image via our RESTful API and receive structured JSON responses in real-time.

# 📝 API Endpoints
GET /
Description: Returns the frontend upload page.
POST /extract
Description: Accepts an invoice image file and returns extracted data as JSON.
🎨 Frontend Magic
Our sleek, responsive frontend makes it super easy to upload invoice images and instantly view the extracted details. Check out our design powered by modern HTML & CSS that puts user experience first! 🌟

![Screenshot 2025-02-16 170546](https://github.com/user-attachments/assets/5065fd31-fb45-4b9a-89e8-3301066edaf9)

🤝 Contributing
We welcome contributions! Whether you're fixing a bug, adding a feature, or improving documentation, feel free to submit a pull request. For major changes, please open an issue first to discuss what you'd like to change.

📜 License
This project is open-source under the MIT License. Use, modify, and share it with the community! 🔓

🙏 Acknowledgements
Tesseract OCR: For its powerful text extraction capabilities. 🤖
Flask: For providing a flexible API framework. 🐍
OpenCV & Pandas: For robust image processing and data handling. 📊
Our Awesome Community: Thanks for your continuous support and contributions! ❤️
