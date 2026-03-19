from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
print(f"🔌 Connecting to: {MONGO_URI[:30]}...")
client = MongoClient(MONGO_URI)
db = client['thadomal_db']
users = list(db['users'].find())

if not users:
    print("No users found in database")
else:
    print("Available users:")
    for user in users:
        print(f"  - {user['username']} ({user['email']}) - ID: {user['_id']}")
