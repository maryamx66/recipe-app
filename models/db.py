from pymongo import MongoClient
import os

def get_client():
    database_url = os.environ.get("DATABASE_URL", "mongodb://127.0.0.1:27017")
    client = MongoClient(database_url)
    return client

def get_db():
    client = get_client()
    db = client["recipe-app"]
    return db

client = get_client()
db = get_db()
