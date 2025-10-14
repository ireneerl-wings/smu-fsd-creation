from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import app as backend
import os

app = FastAPI(title="FSD Chatbot API", version="1.1")

# Setup Jinja2 template folder
templates = Jinja2Templates(directory="templates")

# --- Mapping FSD ke file txt & PDF ---
FSD_MAPPING = {
    "C0177": {
        "txt": r"Txt/434077697_requirements3.md",
        "pdf": r"Pdf/C0177.pdf"
    },
    "C0338": {
        "txt": r"Txt/466681857_requirements3.md",
        "pdf": r"Pdf/C0338.pdf"
    },
    "D0091": {
        "txt": r"Txt/484147232_requirements3.md",
        "pdf": r"Pdf/D0091.pdf"
    },
}

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ask")
async def ask_fsd(fsd_code: str = Form(...), question: str = Form(...)):
    """Process user query for a selected FSD"""
    if fsd_code not in FSD_MAPPING:
        return JSONResponse(status_code=404, content={"error": "Invalid FSD code"})

    txt_path = FSD_MAPPING[fsd_code]["txt"]

    response = backend.process_streamlit(
        user_query=question,
        session_id=backend.get_session_id(),
        file_path=txt_path
    )

    return {"response": response}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port)
