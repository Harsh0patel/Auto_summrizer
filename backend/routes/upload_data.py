from fastapi import APIRouter
from models import pydantic_models
from config import mongodb_config
from bson.objectid import ObjectId


router = APIRouter()

@router.post('/upload')
def upload_file(data: pydantic_models.Upload_data):
    file_id = mongodb_config.db.files.insert_one({
        "file_name" : data.file_name,
        "file_content" : data.file_content
    }).inserted_id
    return {"file_id" : str(file_id)}

@router.post('/upload_summury')
def upload_summury(data : pydantic_models.Upload_summary):
    file_id = mongodb_config.db.summary.insert_one({
        "_id" : ObjectId(data.id),
        "file_content" : data.file_content
    }).inserted_id
    return {"file_id" : str(file_id)}