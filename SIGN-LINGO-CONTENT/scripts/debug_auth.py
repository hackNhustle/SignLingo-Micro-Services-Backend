from pymongo import MongoClient
from pymongo.server_api import ServerApi
import certifi

# Hardcoded exactly from user's provided info
# User: emaadakhtar53_db_user
# Password: UCynnBl6LpCvvN4e
uri = "mongodb+srv://emaadakhtar53_db_user:UCynnBl6LpCvvN4e@cluster0.q3ltm0v.mongodb.net/?appName=Cluster0"

print("Attempting to ping Atlas with hardcoded credentials...")
try:
    client = MongoClient(
        uri, 
        server_api=ServerApi('1'),
        tlsCAFile=certifi.where()
    )
    client.admin.command('ping')
    print("SUCCESS: Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"FAILURE: {e}")
finally:
    if 'client' in locals():
        client.close()
