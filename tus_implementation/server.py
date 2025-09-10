from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
import os

TUSD_URL = os.environ.get("TUSD_URL", "http://localhost:1080/files/")

app = FastAPI()

@app.post("/uploads")
async def create_upload(request: Request):
    """
    Example wrapper: authenticate user, add metadata, then forward to tusd.
    """
    user_id = request.headers.get("X-User-ID")
    if not user_id:
        raise HTTPException(status_code=401, detail="Missing user id")

    # Add tus metadata header (tus spec requires base64-encoded values)
    filename = "test.bin"
    headers = {
        "Tus-Resumable": "1.0.0",
        "Upload-Length": "5242880",
        "Upload-Metadata": f"filename {filename.encode().hex()}"  # tus spec = base64; using hex here for demo
    }

    async with httpx.AsyncClient() as client:
        resp = await client.post(TUSD_URL, headers=headers)

    if resp.status_code != 201:
        raise HTTPException(status_code=resp.status_code, detail=resp.text)

    # You can store mapping in your DB: {user_id, tus_upload_id, filename}
    return JSONResponse({"upload_url": resp.headers["Location"]})

@app.post("/uploads/{upload_id}/complete")
async def after_upload(upload_id: str):
    """
    Called by client after upload is done.
    Here you can trigger post-processing (DB, ML job, etc.)
    """
    # You could query tusd’s file info via HEAD or GET /files/{id}
    return {"status": "ok", "upload_id": upload_id}
