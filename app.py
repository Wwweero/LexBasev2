from flask import Flask, render_template, request, redirect, url_for #Imports from Flask to set up the web server, render HTML, and handle form submissions
import os #Python module to interact with the operating system for the files
import spacy #NLP
import fitz #PyMuPDF for PDF reading
import re #Python RegEx module
from werkzeug.utils import secure_filename #To sanitize the uploaded file

nlp = spacy.load("en_core_web_sm") #Loads SpaCy's small English model

REDFLAG_KEYWORDS = {
    "break clause": [
        "break clause",
        "terminate early",
        "early termination",
        "either party may end this tenancy",
        "notice to end tenancy"],
    
    "professional cleaning": [
        "professional clean",
        "professional cleaning",
        "must pay for professional cleaning",
        "clean to a professional standard"],

    "rent increase": [
        "rent increase",
        "indexation",
        "rent review",
        "review the rent",
        "increase your rent",
        "adjusted rent"],
    
    "sublet": [
        "sublet",
        "sublease",
        "re-let",
        "sharing possession",
        "cannot assign"],

    "landlord access": [
        "landlord may enter",
        "landlord access at any time",
        "right of entry",
        "enter the property without notice"],
    
    "late rent fees": [
        "late rent",
        "interest on late payment",
        "interest charge",
        "overdue rent penalty" ],
    
    "unfair forfeiture": [
        "re-enter the property",
        "forfeiture clause",
        "regain possession",
        "section 8 of the Housing Act 1988" ],
    
    "deposit issues": [
        "deposit is held",
        "no deposit scheme",
        "non-refundable deposit" ],
    
    "overnight guest restriction": [
        "no overnight guests",
        "guest policy",
        "must not have visitors" ],
    
    "cleaning unfair term": [
        "professional standard before moving out",
        "pay for cleaning service"  ],
    
    "early termination penalty": [
        "must pay full rent if leaving early",
        "termination fee",
        "charge for ending early",
        "pay in full" ],

    "utility limits": [
        "fair usage clause",
        "limit on energy use",
        "reasonable usage",
    ],
    "council tax": [
        "tenant responsible for council tax",
        "unclear who pays council tax",
        "council tax",
    ],
    "incorrect tenancy type": [
        "licence agreement",
        "lodger agreement",
        "excluded licence",
    ],
}

 #A dictionary mapping the categories for potentially problematic terms to lists of pharses that could identify them


#Defines a function to detect potentially problematic clauses
def detect_red_flags(text):
    doc = nlp(text) #Processes input text with SpaCy's nlp, breaking it into sentences
    results = [] #Creates an empty list to store matches

    for sent in doc.sents:
        sentence_text = sent.text.strip()
        s = sentence_text.lower()

        for label, keywords in REDFLAG_KEYWORDS.items():
            for keyword in keywords:
                # Allows for optional whitespace or punctuation between keyword parts
                parts = re.split(r'\s+', keyword.strip())
                pattern = r'\b' + r'\s+'.join(re.escape(part) for part in parts) + r'\b'

                if re.search(pattern, s, re.IGNORECASE):
                    results.append((sentence_text, label))
                    break  # No need to check more keywords for this label
            else:
                continue
            break  # No need to check more keywords if one matched 

    return results #Returns a list of tuples




app = Flask(__name__) #Creates a Flask web app instance


app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5 MB max upload size

# Sets upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'pdf'} #Only allowes pdf files

#Consistent PDF extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Makes sure the uploads folder exists if not creates one
os.makedirs(UPLOAD_FOLDER, exist_ok=True)



#Extracts clauses by sentence patterns
def extract_clauses(text):
    clause_patterns = {
        "Tenancy Term": r"(Tenancy\s*(Duration|Term).*?)(?=\n[A-Z]|$)",
        "Rent & Payment": r"(Rent\s*(Amount|Payment|Due).*?)(?=\n[A-Z]|$)",
        "Deposit": r"(Deposit.*?)(?=\n[A-Z]|$)",
        "Repairs & Maintenance": r"(Repair.*?Maintenance.*?)(?=\n[A-Z]|$)",
        "Access & Notice": r"(Access.*?Notice.*?)(?=\n[A-Z]|$)",
        "Termination / Notice Period": r"(Termination|End of Tenancy).*?(?=\n[A-Z]|$)",
        "Tenant Obligations": r"(Tenant.*?Obligations.*?)(?=\n[A-Z]|$)",
        "Landlord Obligations": r"(Landlord.*?Obligations.*?)(?=\n[A-Z]|$)",
        "Dispute Resolution": r"(Dispute.*?Resolution.*?)(?=\n[A-Z]|$)"
    }

    results = {} 
    for name, pattern in clause_patterns.items():
        match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
        results[name] = match.group(0).strip() if match else "Clause not found" #Saves the match under its name or returns info when no match found
    return results


@app.route('/') #Handles the root url
def index():
    return render_template('index.html') #Gets the Index LexBase page

@app.route('/upload', methods=['GET', 'POST']) 
def upload_file():
    if request.method == 'POST':
        if request.content_length and request.content_length > 5 * 1024 * 1024:
                return "File too large. Maximum allowed size is 5 MB.", 413 #File too big error
        uploaded_file = request.files['filename'] #Gets the uploaded file from the form
        if uploaded_file and allowed_file(uploaded_file.filename):
            filename = secure_filename(uploaded_file.filename)
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(save_path)
            return redirect(url_for('results', filename=filename))
        return "Only PDF files are allowed.", 400 #Returns an error if the file is invalid
    return render_template('upload.html')

@app.route('/results')
def results():
    filename = request.args.get('filename') #Gets the filename from the URL
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename) #Constructs the full path to the uploaded PDF
    
    #Opens the PDF using PyMuPDF
    try:
        doc = fitz.open(filepath)
        pages = []

        for page in doc:
            page_text = page.get_text()
            pages.append(page_text.strip())

        doc.close()

        text = "\n\n---PAGEBREAK---\n\n".join(pages)

    except Exception as e:
        return f"Error: Could not read PDF file. Reason: {str(e)}", 500



    # A dictionary of common tenancy terms
    keywords_with_definitions = {
        "deposit": "A sum of money held as security for the performance of the tenant's obligations.",
        "landlord": "The person who owns and rents out the property.",
        "tenant": "The person who rents the property from the landlord.",
        "notice period": "The time required to give the other party before ending the tenancy.",
        "fixed term": "A tenancy with a set end date (e.g., 12 months).",
        "repairs": "Responsibilities for maintaining the property.",
        "gas safety": "Legal requirement for gas appliances to be safe.",
        "access": "When and how the landlord can enter the property.",
        "termination": "How the tenancy can legally end.",
        "agreement": "The tenancy contract.",
        "assured shorthold tenancy":"A type of tenancy defined in the Housing Act 1988.",
        "property":"The premises being rented",
         "break clause": "A contract clause allowing the tenancy to be ended early by tenant, landlord, or both.",
        "subletting": "Renting out part or all of the rented property to someone else.",
        "cleaning": "The condition the property must be left in at the end of the tenancy.",
        "rent review": "A clause allowing the landlord to raise the rent during the tenancy.",
        "overcrowding": "When more people live in a property than legally permitted.",
        "joint tenancy": "Where two or more tenants share responsibility for the whole property.",
        "utilities": "Services such as gas, electricity, and water that may or may not be included in rent.",
        "council tax": "A local tax paid to the council for public services like waste collection.",
        "guarantor": "A person who agrees to pay the rent if the tenant cannot.",
        "early termination": "Ending the tenancy before the fixed term expires, typically with conditions.",
        "letting agent": "A person or company acting on behalf of the landlord in managing the property.",
        "rent arrears": "Unpaid rent owed by the tenant.",
        "deposit protection scheme": "A government-approved scheme that protects tenants' deposits.",
        "forfeiture": "A landlord’s right to end the tenancy due to a serious breach by the tenant.",
    }


    
    def highlight_terms(text, keywords_dict):
        highlighted = set()  # Keeps track of already highlighted words

        def make_replacer(word):
            def replacer(match):
                if word.lower() in highlighted:
                    return match.group(0)  # Don't highlight again
                highlighted.add(word.lower())
                definition = keywords_dict.get(word.lower(), "")
                return f'<span class="highlight-definition">{match.group(0)}<span class="definition-text">{definition}</span></span>'
            return replacer

        sorted_keywords = sorted(keywords_dict.keys(), key=len, reverse=True) #Sorts keywords by length 

        #Highlights keyword
        for word in sorted_keywords:
            pattern = re.compile(rf'\b({re.escape(word)})\b', re.IGNORECASE)
            text = pattern.sub(make_replacer(word), text)

        return text
    
    text=text.replace("---PAGEBREAK---", "<div class='page-break'></div>")

    


    highlighted_text = highlight_terms(text, keywords_with_definitions) #Applies visual highlighting

    

    if os.path.exists(filepath):
        os.remove(filepath) #Deletes the uploaded file after processing 

        try:
            flagged = detect_red_flags(text) #Runs the function
        except Exception as e:
            flagged = [("NLP processing error", f"Could not analyze text: {str(e)}")] #Error message if SpaCy fails


    return render_template('results.html', flagged_clauses=flagged, filename=filename, text=highlighted_text) #Gets the results page

if __name__ == '__main__':
    app.run(debug=True) #Runs the app in debug mode 
    
