
from pymongo import MongoClient
from pymongo.server_api import ServerApi
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

uri = os.getenv("MONGODB_URI")

client = MongoClient(uri, server_api=ServerApi("1"))

db = client["financial_ai"]