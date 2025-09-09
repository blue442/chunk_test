import logging
from fastapi import FastAPI, UploadFile, Form
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os

logging.basicConfig(level=logging.DEBUG)

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

    # save the chunks
    chunk_path = os.path.join(file_dir, f"chunk_{chunkIndex}")
    with open(chunk_path, "wb") as f:
        logging.debug(f"Saving chunk {chunkIndex} of {totalChunks} for file {fileName} (ID: {fileId})")
        content = await chunk.read()
        f.write(content)


    # Check if all chunks are present
    existing_chunks = len([name for name in os.listdir(file_dir) if name.startswith("chunk_")])
    if existing_chunks == totalChunks:
        # Reconstruct the file
        final_path = os.path.join(UPLOAD_DIR, fileName)
        with open(final_path, "wb") as final_file:
            for i in range(totalChunks):
                chunk_path = os.path.join(file_dir, f"chunk_{i}")
                with open(chunk_path, "rb") as chunk_file:
                    final_file.write(chunk_file.read())
        # Optionally, clean up chunk files
        for i in range(totalChunks):
            os.remove(os.path.join(file_dir, f"chunk_{i}"))
        os.rmdir(file_dir)
        logging.debug(f"File {fileName} (ID: {fileId}) reconstructed successfully")
        return JSONResponse(content={"status": "complete", "file": final_path})


    return JSONResponse(content={"status": "success", "chunk": chunkIndex})
