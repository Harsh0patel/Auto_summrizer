from fastapi import APIRouter, HTTPException
from bson.objectid import ObjectId
from models import pydantic_models
from config import mongodb_config
from utils import preprocess, Generate_summary

router = APIRouter()
summary = Generate_summary.Generate_summary()

@router.post('/Generatetext')
def Generate_text(data : pydantic_models.GenerateData):

    doc = mongodb_config.db.files.find_one({"_id": ObjectId(data.file_id)})
    if not doc:
        return HTTPException(status_code = 404, detail = "file not found")
    
    txt = doc["file_content"]
    txt = preprocess.preprocess_text(txt)
    ans = summary.summury_generated(txt)
    return {"summary" : ans}