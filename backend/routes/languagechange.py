from fastapi import APIRouter, HTTPException
from models import pydantic_models
from utils import Generate_summary
from config import mongodb_config
from bson.objectid import ObjectId

router = APIRouter()
changelang = Generate_summary.changelang()

@router.post('/changelanguage')
def change(data : pydantic_models.languageData):
    doc = mongodb_config.db.summary.find_one({
        "_id" : ObjectId(data.id)
    })
    if not doc:
        raise HTTPException(status_code = 404, detail = "file not found.")
    
    text = doc["file_content"]
    ans = changelang.change_language(text, data.language)

    return {"summary" : ans}