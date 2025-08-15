import os
from dotenv import load_dotenv
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

def get_database_connection(db_name: str):
  
    uri = os.getenv("MONGODB_URI")
    if not uri:
        raise ValueError("MongoDB URI not found in environment variables")

    client = MongoClient(
        uri,
        server_api=ServerApi('1'),
        connectTimeoutMS=5000,
        socketTimeoutMS=30000,
        maxPoolSize=50,
        retryWrites=True
    )

    try:
        client.admin.command('ping')
        print(f"✅ Successfully connected to MongoDB database: {db_name}")
        return client[db_name]
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        raise


# get_database_connection(db_name="books")