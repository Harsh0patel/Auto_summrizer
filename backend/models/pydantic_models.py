from pydantic import BaseModel, Field
from typing import Annotated 

# Pydantic Models
class GenerateData(BaseModel):
    file_id : Annotated[str, Field(..., description = "mongodb _id")]

class Upload_data(BaseModel):
    file_name : Annotated[str, Field(..., description = "Name of the File")]
    file_content : Annotated[str, Field(..., description = "Data inside given file.")]  

class Upload_summary(BaseModel):
    id : Annotated[str, Field(..., description = "mongodb _id")]
    file_content : Annotated[str, Field(..., description="Generated summary by model.")]

class languageData(BaseModel):
    id : Annotated[str, Field(..., description="Mongodb_id")]
    language : Annotated[str, Field(..., description="In which language it will be translated")]