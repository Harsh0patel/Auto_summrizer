from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

router = APIRouter()
MODEL_VERSION = '1.0.0'

@router.get('/')
def home_page():
    return JSONResponse(
    {"message": "This is Auto Summarizer's API page. To see documentation use /docs."},
    status_code=200
)

@router.get('/health')
def health():
    return {
        "Status" : 'OK',
        "Model_version" : MODEL_VERSION
    }