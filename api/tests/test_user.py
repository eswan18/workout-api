import pytest
import requests
import pymongo

# Import the testing data that will populate the mongo collection.
from data.data import users as users_collection

API_URL = 'http://localhost:5000/user/'
MONGO_URL = 'rpi3-1'
MONGO_DB = 'workout_app_dev'

db = pymongo.MongoClient(MONGO_URL)[MONGO_DB]

@pytest.fixture(autouse=True)
def reset_collection():
    '''Reset mongo between tests.'''
    db.users.delete_many({})
    db.users.insert_many(users_collection)

def test_get_user():
    object_id = '5c3c03c7c62a6647e3204792'
    response = requests.get(API_URL + object_id)
    data = response.json()
    resource = data['resource']
    assert resource['first_name'] == 'Ethan'
    assert resource['last_name'] == 'Swan'

def test_get_all_users():
    response = requests.get(API_URL)
    data = response.json()
    resource = data['resource']
    assert isinstance(resource, list)
    assert len(resource) == 2
    assert all([x.get('first_name') is not None for x in resource])
