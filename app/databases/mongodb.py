from pymongo import MongoClient
from app.config import MONGODB_URI, MONGODB_DB_NAME, MONGODB_COLLECTION_NAME

def conectar_mongodb():
    client = MongoClient(MONGODB_URI)
    db = client[MONGODB_DB_NAME]
    return db[MONGODB_COLLECTION_NAME]
