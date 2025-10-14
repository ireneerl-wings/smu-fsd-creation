from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import JSONResponse
import uvicorn
import app as backend
import os

app = FastAPI(title="FSD Chatbot API", version="1.0")

# --- Mapping FSD ke file txt & PDF ---
FSD_MAPPING = {
    "A0001": {
        "txt": r"Txt/436109344_requirements3 (1).md",
        "pdf": r"Pdf/SD1-A0001 - Custom Contract and Custom Order Unit in Purchase Order with Contract-140825-162547.pdf"
    },
    "B0141": {
        "txt": r"Txt/413008086_requirements3.md",
        "pdf": r"Pdf/SD1-B0141 - Auto Delete Reservation-140825-161854.pdf"
    },
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
    "E0067": {
        "txt": r"Txt/445579749_requirements3 (1).md",
        "pdf": r"Pdf/SD1-E0067- (LM) POD (Proof Of Delivery) DELMAN to SAP S4-140825-162433.pdf"
    }
}

@app.get("/")
async def root():
    return {"message": "Welcome to FSD Chatbot API 🚀"}

@app.get("/fsd-list")
async def list_fsd():
    """Return list of available FSD keys"""
    return {"available_fsd": list(FSD_MAPPING.keys())}

@app.post("/ask")
async def ask_fsd(
    fsd_code: str = Form(...),
    question: str = Form(...)
):
    """Process user query for a selected FSD"""
    if fsd_code not in FSD_MAPPING:
        return JSONResponse(status_code=404, content={"error": "Invalid FSD code"})

    txt_path = FSD_MAPPING[fsd_code]["txt"]

    response = backend.process_streamlit(
        user_query=question,
        session_id=backend.get_session_id(),
        file_path=txt_path
    )

    return {"fsd_code": fsd_code, "question": question, "response": response}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
