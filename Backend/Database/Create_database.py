from pymongo import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://tejashreechaganti07_db_user:Teju_2007@test.acy3cud.mongodb.net/?appName=test"


client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Connected Successfully!")

    db = client["financial_ai"]

    collections = [
        "users",
        "workspaces",
        "documents",
        "financial_metrics",
        "red_flags",
        "comparisons",
        "chat_sessions",
        "messages",
        "reports"
    ]

    for collection in collections:
        try:
            db.create_collection(collection)
            print(f"{collection} created")
        except Exception:
            print(f"{collection} already exists")

except Exception as e:
    print(e)