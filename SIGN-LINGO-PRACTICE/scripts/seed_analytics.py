"""
Seed script to populate MongoDB with sample analytics data
Run this to add test data for the analytics dashboard
"""

from pymongo import MongoClient
from datetime import datetime, timedelta
import random
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB setup - use Atlas connection from .env
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
print(f"🔌 Connecting to MongoDB Atlas...")
client = MongoClient(MONGO_URI)
db = client['thadomal_db']

# Collections
users_collection = db['users']
practice_sessions_collection = db['practice_sessions']
analytics_events_collection = db['analytics_events']

def get_or_create_test_user():
    """Get existing user or prompt for user ID"""
    print("\n=== User Selection ===")
    users = list(users_collection.find())
    
    if not users:
        print("❌ No users found in database!")
        print("Please register a user first through the application.")
        return None
    
    print("\nAvailable users:")
    for i, user in enumerate(users, 1):
        print(f"{i}. {user['username']} ({user['email']}) - ID: {user['_id']}")
    
    choice = input("\nEnter user number (or press Enter for first user): ").strip()
    
    if not choice:
        selected_user = users[0]
    else:
        try:
            selected_user = users[int(choice) - 1]
        except (ValueError, IndexError):
            selected_user = users[0]
    
    print(f"\n✅ Selected user: {selected_user['username']}")
    return selected_user

def create_practice_sessions(user_id):
    """Create sample practice sessions for the past 30 days"""
    sessions = []
    
    signs = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 
             'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z',
             'Hello', 'Thankyou', 'Mother', 'Father', 'Wife', 'Husband',
             '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
    
    session_types = [
        'alphabet_practice', 
        'sign_practice', 
        'vocabulary_practice',
        'writing_practice',
        'sentence_practice'
    ]
    
    # Create sessions for the past 30 days
    for days_ago in range(30):
        date = datetime.utcnow() - timedelta(days=days_ago)
        
        # Skip some days randomly (to create realistic gaps)
        if random.random() < 0.3:  # 30% chance to skip a day
            continue
        
        # Create 1-4 sessions per day
        num_sessions = random.randint(1, 4)
        
        for _ in range(num_sessions):
            session = {
                'user_id': str(user_id),
                'session_type': random.choice(session_types),
                'character': random.choice(signs),
                'score': random.randint(70, 100),  # Random score between 70-100
                'duration': random.randint(15, 60),  # 15-60 minutes
                'completed': True,
                'notes': f'Practice session for {random.choice(signs)}',
                'created_at': date - timedelta(hours=random.randint(0, 23), 
                                               minutes=random.randint(0, 59))
            }
            sessions.append(session)
    
    # Insert sessions
    if sessions:
        result = practice_sessions_collection.insert_many(sessions)
        print(f"✅ Inserted {len(result.inserted_ids)} practice sessions")
    else:
        print("⚠️ No sessions to insert")
    
    return len(sessions)

def create_analytics_events(user_id, num_events=50):
    """Create sample analytics events"""
    events = []
    
    event_types = [
        'vocabulary_learned',
        'isl_conversion',
        'stem_lesson_completed',
        'writing_practice_completed',
        'video_watched'
    ]
    
    for i in range(num_events):
        days_ago = random.randint(0, 30)
        date = datetime.utcnow() - timedelta(days=days_ago)
        
        event = {
            'user_id': str(user_id),
            'event_type': random.choice(event_types),
            'event_data': {
                'character': random.choice(['A', 'B', 'C', 'D', 'E']),
                'word': random.choice(['Hello', 'Thanks', 'Please', 'Sorry']),
                'score': random.randint(70, 100)
            },
            'created_at': date
        }
        events.append(event)
    
    # Insert events
    if events:
        result = analytics_events_collection.insert_many(events)
        print(f"✅ Inserted {len(result.inserted_ids)} analytics events")
    else:
        print("⚠️ No events to insert")
    
    return len(events)

def clear_existing_data(user_id):
    """Clear existing practice sessions and analytics for the user"""
    user_id_str = str(user_id)
    
    sessions_deleted = practice_sessions_collection.delete_many({'user_id': user_id_str})
    events_deleted = analytics_events_collection.delete_many({'user_id': user_id_str})
    
    print(f"\n🗑️ Cleared {sessions_deleted.deleted_count} existing sessions")
    print(f"🗑️ Cleared {events_deleted.deleted_count} existing events")

def main():
    print("\n" + "="*60)
    print("  📊 Analytics Data Seeder for ISL Learning Platform")
    print("="*60)
    
    # Get user
    user = get_or_create_test_user()
    if not user:
        return
    
    user_id = user['_id']
    
    # Ask if user wants to clear existing data
    clear = input("\n🗑️ Clear existing analytics data for this user? (y/n): ").strip().lower()
    if clear == 'y':
        clear_existing_data(user_id)
    
    print("\n" + "-"*60)
    print("  📝 Creating Sample Data...")
    print("-"*60)
    
    # Create data
    sessions_count = create_practice_sessions(user_id)
    events_count = create_analytics_events(user_id)
    
    print("\n" + "="*60)
    print("  ✅ SEED COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"\n📊 Summary:")
    print(f"   - User: {user['username']}")
    print(f"   - Practice Sessions: {sessions_count}")
    print(f"   - Analytics Events: {events_count}")
    print(f"\n💡 Now visit the profile page to see dynamic analytics data!")
    print(f"   The data includes:")
    print(f"   - Learning streak (consecutive days)")
    print(f"   - Signs learned ({len(set(['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J'])))} unique signs)")
    print(f"   - Average accuracy (70-100%)")
    print(f"   - Weekly learning hours")
    print(f"   - Achievements based on performance")
    print("\n" + "="*60 + "\n")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Seed cancelled by user")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
