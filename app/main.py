from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from app.middleware.processPrompt import promptResponse

app = FastAPI()

# Setup templates directory
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})

@app.post("/", response_class=HTMLResponse)
async def process_form(request: Request, prompt: str = Form(...)):
    # Here you can process the prompt and get the response

    newResponse = promptResponse(prompt)
    return templates.TemplateResponse("form.html", {"request": request, "response": newResponse})
