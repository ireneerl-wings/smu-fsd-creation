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
    "A0001 - Enhancement for Custom Contract and Custom Order Unit in Purchase Order with Contract": {
        "txt": r"Txt/436109344_requirements3.md",
        "pdf": r"Pdf/SD1-A0001 - Custom Contract and Custom Order Unit in Purchase Order with Contract-140825-162547.pdf"
    },
    "B0141 - Auto Delete Reservation enhancement for SAP system": {
        "txt": r"Txt/413008086_requirements3.md",
        "pdf": r"Pdf/SD1-B0141 - Auto Delete Reservation-140825-161854.pdf"
    },
    "C0177 - Weighing Machine at BS for GI & GR based on CO PRO - Connect to Weighing Machine from Fiori - SAP S/4": {
        "txt": r"Txt/434077697_requirements3.md",
        "pdf": r"Pdf/C0177.pdf"
    },
    "C0338 - OUT I/F to provide detail stock in Storage Bin - SAP S/4": {
        "txt": r"Txt/466681857_requirements3.md",
        "pdf": r"Pdf/C0338.pdf"
    },
    "D0091 - Inbound interface from satellite Apps to create SO - SFA - API - SAP S/4": {
        "txt": r"Txt/484147232_requirements3.md",
        "pdf": r"Pdf/D0091.pdf"
    },
    "E0067 - (LM) POD (Proof Of Delivery) DELMAN to SAP S4": {
        "txt": r"Txt/445579749_requirements3.md",
        "pdf": r"Pdf/SD1-E0067- (LM) POD (Proof Of Delivery) DELMAN to SAP S4-140825-162433.pdf"
    },
    "E0187 - Delivery Optimization Master": {
        "txt": r"Txt/567182258_requirements.md",
        "pdf": None
    },
    "E0424 - Delivery Optimization Master WGO": {
        "txt": r"Txt/407634084_requirements.md",
        "pdf": None
    },
    "C0168 - Difference List & Posting for Cycle Count - SAP S/4": {
        "txt": r"Txt/434110468_requirements.md",
        "pdf": None,
    },
    "C0169 - Difference List & Posting for Periodic Count - SAP S/4": {
        "txt": r"Txt/434077714_requirements.md",
        "pdf": None,
    },
    "Z0003 - Automation on Material Master status change - cost is released (NPD Not Launched and Active Status)": {
        "txt": r"Txt/469599062_requirements.md",
        "pdf": None,
    },
    "Z0004 - Automation on Material Master status change - NPD Launched - SAP S/4": {
        "txt": r"Txt/600375455_requirements.md",
        "pdf": None,
    }
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

    response = backend.process_fsd_query(
        user_query=question,
        session_id=backend.get_session_id(),
        file_path=txt_path
    )

    if not response:
        return JSONResponse(content={"response": "⚠️ No response generated for this query."})

    return JSONResponse(content={"response": response})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=port)
