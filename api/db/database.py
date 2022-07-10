from pymongo import MongoClient


DB_URL = os.environ['DATABASE_URL']

client = MongoClient(DB_URL)
db = client.workout_api  # Fetch the "workout_api" database
