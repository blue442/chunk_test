from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI()

# Serve static files (HTML, JS, CSS)

app.mount("/static", StaticFiles(directory="static", html=True), name="static")


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/upload-chunk")
async def upload_chunk(
    chunk: UploadFile,
    chunkIndex: int = Form(...),
    totalChunks: int = Form(...),
    fileName: str = Form(...),
    fileId: str = Form(...)
):
    file_dir = os.path.join(UPLOAD_DIR, fileId)
    os.makedirs(file_dir, exist_ok=True)

    chunk_path = os.path.join(file_dir, f"chunk_{chunkIndex}")
    with open(chunk_path, "wb") as f:
        content = await chunk.read()
        f.write(content)

    return JSONResponse(content={"status": "success", "chunk": chunkIndex})
