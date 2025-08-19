import pymongo
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv

# Database
load_dotenv()
mongo_url = os.getenv("MONGO_URL")
client = pymongo.MongoClient(mongo_url)
db = client["file_db"]