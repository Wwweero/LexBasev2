# LexBase

LexBase is a lightweight Flask-based web app that lets users upload rental agreements in PDF format for review. The program highlights potentially problematic legal clauses and provides simplified definitions on some of the key terms.

## Features

- Upload UK rental agreements (PDF) for review
- Text extraction and clause analysis
- Flagging of potentially risky red-flag clauses
- Uses spaCy NLP for legal clause classification
- Clean, responsive interface with results filtering (red flags, full text, or both)
- Styled with custom HTML/CSS templates

## Requirements

All dependencies are listed in requirements.txt.

- Flask
- spaCy with en_core_web_sm
- PyMuPDF for PDF text extraction
- Gunicorn for deployment


## Installation

Clone the repository and set up a virtual environment:

git clone https://github.com/Wwweero/LexBasev2.git
cd LexBasev2

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm



## UI Overview

1) Welcome page introducing LexBase
2) Upload Page (/upload)
  - Upload PDF contract
  - Spinner shows during processing
3) Results Page (/results)
  - View extracted text and flagged clauses
  - Toggle between "Red Flags", "Full Text", or "Both"

## Structure
```
LexBasev2
├── app.py # Main Flask app
├── requirements.txt
├── static/
│ ├── style.css # Custom styling
│ └── images/
│ └── LexBase1.png
├── templates/
│ ├── index.html
│ ├── upload.html
│ └── results.html
```

## Index Page
<img width="1470" alt="Screenshot 2025-06-26 at 15 18 18" src="https://github.com/user-attachments/assets/149c540e-2d2b-44fd-8390-4668ab902251" />

## Upload Page
<img width="1470" alt="Screenshot 2025-06-26 at 15 19 15" src="https://github.com/user-attachments/assets/77fcc232-61aa-4026-8f01-7a015c1af963" />

## Results Page
<img width="1468" alt="Screenshot 2025-06-26 at 15 20 28" src="https://github.com/user-attachments/assets/702f050b-a513-42eb-a615-a7821f79dca9" />




