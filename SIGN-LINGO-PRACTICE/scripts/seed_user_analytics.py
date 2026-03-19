"""
Quick seed script - automatically finds your user or uses provided ID
Creates 30 days of realistic practice data that updates dynamically
"""

from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta

import sys
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB setup - use Atlas connection from .env
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
client = MongoClient(MONGO_URI)
db = client['thadomal_db']

print(f"🔌 Connecting to: {MONGO_URI[:20]}...")

# Collections
users_collection = db['users']
practice_sessions_collection = db['practice_sessions']
analytics_events_collection = db['analytics_events']

def get_user_id():
    """Get user ID from command line or database"""
    # Check if user ID provided as argument
    if len(sys.argv) > 1:
        user_id = sys.argv[1]
        user = users_collection.find_one({'_id': ObjectId(user_id)})
        if user:
            return user_id, user
        print(f"❌ User ID {user_id} not found!")
    
    # Otherwise, get first user from database
    user = users_collection.find_one()
    if not user:
        print("\n❌ No users in database!")
        print("\n📝 Please register a user first:")
        print("   1. Start your backend server: python app.py")
        print("   2. Start your frontend: npm run dev")
        print("   3. Register a new account")
        print("   4. Come back and run this script again")
        return None, None
    
    return str(user['_id']), user

def clear_and_seed():
    """Clear old data and create new seed data"""
    
    # Get user
    USER_ID, user = get_user_id()
    if not USER_ID:
        return
    
    print(f"\n✅ Found user: {user['username']} ({user['email']})")
    print(f"   User ID: {USER_ID}")
    
    # Clear existing data
    sessions_deleted = practice_sessions_collection.delete_many({'user_id': USER_ID})
    events_deleted = analytics_events_collection.delete_many({'user_id': USER_ID})
    print(f"🗑️ Cleared {sessions_deleted.deleted_count} old sessions")
    print(f"🗑️ Cleared {events_deleted.deleted_count} old events")
    
    # Create practice sessions for past 30 days
    sessions = []
    signs = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
             'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
             'Hello', 'Thankyou', 'Mother', 'Father']
    
    session_types = ['alphabet_practice', 'sign_practice', 'vocabulary_practice', 'writing_practice']
    
    for days_ago in range(30):
        date = datetime.utcnow() - timedelta(days=days_ago)
        
        # Skip some days randomly (realistic gaps)
        if random.random() < 0.25:
            continue
        
        # 1-3 sessions per day
        for _ in range(random.randint(1, 3)):
            session = {
                'user_id': USER_ID,
                'session_type': random.choice(session_types),
                'character': random.choice(signs),
                'score': random.randint(75, 98),
                'duration': random.randint(20, 50),
                'completed': True,
                'notes': f'Practice session',
                'created_at': date - timedelta(hours=random.randint(9, 21))
            }
            sessions.append(session)
    
    # Insert sessions
    if sessions:
        result = practice_sessions_collection.insert_many(sessions)
        print(f"✅ Created {len(result.inserted_ids)} practice sessions")
    
    # Create analytics events
    events = []
    event_types = ['vocabulary_learned', 'isl_conversion', 'stem_lesson_completed', 
                   'writing_practice_completed', 'video_watched']
    
    for _ in range(50):
        days_ago = random.randint(0, 30)
        event = {
            'user_id': USER_ID,
            'event_type': random.choice(event_types),
            'event_data': {
                'character': random.choice(signs),
                'score': random.randint(75, 98)
            },
            'created_at': datetime.utcnow() - timedelta(days=days_ago)
        }
        events.append(event)
    
    if events:
        result = analytics_events_collection.insert_many(events)
        print(f"✅ Created {len(result.inserted_ids)} analytics events")
    
    print("\n" + "="*60)
    print("✅ SEED COMPLETE!")
    print("="*60)
    print(f"\n📊 Your profile now has:")
    print(f"   - {len(sessions)} practice sessions over 30 days")
    print(f"   - {len(events)} analytics events")
    print(f"   - Learning streak calculated from consecutive days")
    print(f"   - {len(set([s['character'] for s in sessions]))} unique signs learned")
    print(f"\n💡 Visit your profile to see the dynamic analytics!")
    print(f"\n🚀 Going forward, every time you practice:")
    print(f"   - Your practice sessions are auto-recorded")
    print(f"   - Analytics update in real-time")
    print(f"   - Streak continues when you practice daily")
    print("\n" + "="*60)

if __name__ == '__main__':
    try:
        clear_and_seed()
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
