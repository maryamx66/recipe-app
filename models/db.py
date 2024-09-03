from pymongo import MongoClient
import os

def get_db():
    database_url = os.environ.get("DATABASE_URL", "mongodb://127.0.0.1:27017")
    client = MongoClient(database_url)
    db = client["recipe-app"]
    return db


