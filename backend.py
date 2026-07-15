from __future__ import annotations

import json
import os
import time
import socket
import sys
import io

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, UploadFile, File, Query
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pypdf import PdfReader
from livekit import api

load_dotenv()

LIVEKIT_URL = os.getenv("LIVEKIT_URL", "")
LIVEKIT_API_KEY = os.getenv("LIVEKIT_API_KEY", "")
LIVEKIT_API_SECRET = os.getenv("LIVEKIT_API_SECRET", "")


def create_token(room: str, identity: str, metadata: dict) -> str:
    if not LIVEKIT_API_KEY or not LIVEKIT_API_SECRET:
        raise RuntimeError("LIVEKIT_API_KEY and LIVEKIT_API_SECRET are required")

    token = (
        api.AccessToken(LIVEKIT_API_KEY, LIVEKIT_API_SECRET)
        .with_identity(identity)
        .with_name(identity)
        .with_metadata(json.dumps(metadata))
        .with_grants(
            api.VideoGrants(
                room_join=True,
                room=room,
                can_publish=True,
                can_subscribe=True,
                can_publish_data=True,
            )
        )
    )
    return token.to_jwt()


app = FastAPI(title="Voice Interview Coach Backend")

# Setup CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {"ok": True, "livekit_url": bool(LIVEKIT_URL)}


@app.get("/token")
def get_token(
    room: str = "interview-demo",
    identity: str = None,
    name: str = "Candidate",
    role: str = "Software Developer",
    experience: str = "Fresher",
    mode: str = "mixed",
    skills: str = "Python, AI, LiveKit",
    resume: str = "",
):
    if not identity:
        identity = f"candidate-{int(time.time())}"

    metadata = {
        "name": name,
        "role": role,
        "experience": experience,
        "skills": skills,
        "mode": mode,
        "resume": resume[:1200],
    }

    try:
        token = create_token(room, identity, metadata)
        return {
            "url": LIVEKIT_URL,
            "room": room,
            "identity": identity,
            "token": token,
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/parse-resume")
async def parse_resume(file: UploadFile = File(...)):
    filename = file.filename.lower()
    if not filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    try:
        content = await file.read()
        pdf_reader = PdfReader(io.BytesIO(content))
        text = ""
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

        # Simple clean: replace multiple spaces/newlines with single spaces
        cleaned = " ".join(text.split())
        return {"text": cleaned[:1200]}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to parse PDF: {str(exc)}")


_lock_socket = None


def ensure_singleton(port: int):
    global _lock_socket
    try:
        _lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        _lock_socket.bind(("127.0.0.1", port))
    except OSError:
        print(f"\n❌ ERROR: Another instance of this script is already running (locked port {port})!")
        print("Please close any other terminal windows or background python processes.")
        sys.exit(1)


if __name__ == "__main__":
    ensure_singleton(55056)
    if not LIVEKIT_URL:
        print("Warning: LIVEKIT_URL is missing in .env")
    print("Backend token server running at http://localhost:8787")
    uvicorn.run(app, host="127.0.0.1", port=8787, log_level="warning")
