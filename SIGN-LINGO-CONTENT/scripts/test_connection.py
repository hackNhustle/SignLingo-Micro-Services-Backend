from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import os
from dotenv import load_dotenv
import certifi

load_dotenv()

# Use the URI from .env
uri = os.getenv("MONGO_URI")

print(f"Testing connection with URI: {uri.split('@')[1] if '@' in uri else '...masked...'}")

# Create a new client and connect to the server
# Using ServerApi('1') as provided in the Atlas snippet
try:
    client = MongoClient(
        uri, 
        server_api=ServerApi('1'),
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=30000,
        connectTimeoutMS=30000
    )
    # Send a ping to confirm a successful connection
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"Connection failed: {e}")
finally:
    if 'client' in locals():
        client.close()
