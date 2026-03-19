from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
MONGO_URI = os.getenv('MONGO_URI')
client = MongoClient(MONGO_URI)
db = client['thadomal_db']

def inspect():
    user = db.users.find_one()
    print("User fields:", user.keys() if user else "No user found")
    
    session = db.practice_sessions.find_one()
    print("Session fields:", session.keys() if session else "No session found")
    
    mapping = db.asl_mappings.find_one()
    print("Mapping fields:", mapping.keys() if mapping else "No mapping found")

if __name__ == "__main__":
    inspect()
