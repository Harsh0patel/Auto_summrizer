from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi import HTTPException
import Generate_summary as generator
from pydantic import BaseModel
import os
import pymongo
from bson.objectid import ObjectId
from dotenv import load_dotenv

# Database
load_dotenv()
mongo_url = os.getenv("MONGO_URL")
client = pymongo.MongoClient(mongo_url)
db = client["file_db"]

# API
app = FastAPI()

# Model
model = generator.Generate_summary()

# Pydantic Models
class GenerateData(BaseModel):
    file_id : str

class Upload_data(BaseModel):
    file_name : str
    file_content : str  

@app.get('/')
def home_page():
    return JSONResponse("This is Auto summurizer api page.", status_code = 200)

@app.post('/upload')
def upload_file(data: Upload_data):
    file_id = db.files.insert_one({
        "file_name" : data.file_name,
        "file_content" : data.file_content
    }).inserted_id
    return {"file_id" : str(file_id)}

@app.post('/Generatetext')
def Generate_text(data : GenerateData):

    doc = db.files.find_one({"_id": ObjectId(data.file_id)})
    if not doc:
        return HTTPException(status_code = 404, detail = "file not found")
    
    txt = doc["file_content"]
    return {"summary" : model.summury_generated(txt)}