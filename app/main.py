from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.middleware.processPrompt import promptResponse
import requests
import shutil
import tempfile
import xml.etree.ElementTree as ET
import re



app = FastAPI()

# Setup templates directory
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@app.post("/", response_class=HTMLResponse)
async def process_form(request: Request, file: UploadFile = File(...)):

    # Save uploaded file to temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = temp_file.name

    # Ensure query_hugging_face returns the JSON response correctly
    response_json = query_hugging_face(temp_file_path)

    # Extract generated_text from the model's response
    if response_json and 'generated_text' in response_json[0]:
        generated_text = response_json[0]['generated_text']
        # Parse the generated_text to extract invoice data
        invoice_data = parse_generated_text(generated_text)
    else:
        invoice_data = {"error": "Invalid response or missing 'generated_text' in the response."}
    # Now pass invoice_data to your template
    return templates.TemplateResponse("form.html", {"request": request, "response": invoice_data, "invoice_data": invoice_data})


def query_hugging_face(filename):
    API_URL = "https://api-inference.huggingface.co/models/selvakumarcts/sk_invoice_receipts"
    headers = {"Authorization": f"Bearer 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"}
    #"rb" is used to read the file in binary mode
    with open(filename, "rb") as f:
        data = f.read()
    response = requests.post(API_URL, headers=headers, data=data)
    return response.json()

def parse_generated_text(generated_text):
    import re

    pattern = r'<s_(\w+)>(.*?)<\/s_\1>'
    matches = re.findall(pattern, generated_text, re.DOTALL)

    invoice_data = {}
    for key, value in matches:
        cleaned_value = value.strip() or "No Information"
        
        # Special handling for line_items
        if key == 'line_items':
            cleaned_value = parse_line_items(value)

        if key in invoice_data:
            if isinstance(invoice_data[key], list):
                invoice_data[key].append(cleaned_value)
            else:
                invoice_data[key] = [invoice_data[key], cleaned_value]
        else:
            invoice_data[key] = cleaned_value

    return invoice_data

def parse_line_items(line_items_str):
    pattern = r'<s_item_(\w+)>(.*?)<\/s_item_\1>'
    items = re.findall(pattern, line_items_str, re.DOTALL)
    
    line_items = []
    current_item = {}
    for key, value in items:
        cleaned_value = value.strip() or "No Information"
        current_item[key] = cleaned_value

        # Assuming 'sep' or the end of the items indicates a new item
        if key == 'quantity' or '<sep/>' in value:  
            line_items.append(current_item)
            current_item = {}
    
    # Add the last item if not empty
    if current_item:
        line_items.append(current_item)
    
    return line_items

