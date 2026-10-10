"""
IncidentIQ - NLP & Voice API Routes
"""
from fastapi import APIRouter, File, UploadFile, HTTPException
from pydantic import BaseModel
from typing import Optional
from backend.nlp.query_engine import process_natural_language_query, SUPPORTED_EXAMPLE_QUERIES
from backend.nlp.voice_service import transcribe_audio_bytes

router = APIRouter(prefix="/api/nlp", tags=["nlp"])

class QueryRequest(BaseModel):
    query: str

@router.post("/query")
def api_query(req: QueryRequest):
    return process_natural_language_query(req.query)

@router.get("/examples")
def api_examples():
    return {"examples": SUPPORTED_EXAMPLE_QUERIES}

@router.post("/voice/transcribe")
async def api_voice_transcribe(audio: UploadFile = File(...)):
    try:
        contents = await audio.read()
        res = transcribe_audio_bytes(contents)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Audio transcription error: {str(e)}")
