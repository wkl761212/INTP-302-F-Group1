from fastapi import FastAPI, Request, Form, File, UploadFile
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.middleware.processPrompt import promptResponse
import requests
import shutil
import tempfile


app = FastAPI()

# Setup templates directory
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

# @app.post("/", response_class=HTMLResponse)
# async def process_form(request: Request, prompt: str = Form(...)):
#     # Here you can process the prompt and get the response

#     newResponse = promptResponse(prompt)
#     return templates.TemplateResponse("form.html", {"request": request, "response": newResponse})

def query_hugging_face(file_path):
    # Implement the logic to query the Hugging Face API with the saved file
    # and return the response JSON
    pass

@app.post("/", response_class=HTMLResponse)
async def process_form(request: Request, file: UploadFile = File(...)):
    # Save uploaded file to temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = temp_file.name

    # Query the Hugging Face API with the saved file
    response_json = query_hugging_face(temp_file_path)

    return templates.TemplateResponse("form.html", {"request": request, "response": response_json})

def query_hugging_face(filename):
    API_URL = "https://api-inference.huggingface.co/models/selvakumarcts/sk_invoice_receipts"
    headers = {"Authorization": f"Bearer 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"}
    #"rb" is used to read the file in binary mode
    with open(filename, "rb") as f:
        data = f.read()
    response = requests.post(API_URL, headers=headers, data=data)
    return response.json()
