from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os

app = FastAPI()

# Allow CORS for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

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
