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

def test_delete_user():
    '''Try to delete the first user that comes back from GET.'''
    all_users = requests.get(API_URL).json()['resource']
    first_user_id = all_users[0]['_id']
    response = requests.delete(API_URL + first_user_id)
    assert response.status_code == 204
    # Try to retrieve the id again with GET.
    response = requests.get(API_URL + first_user_id)
    assert response.status_code == 404

def test_put_user():
    '''Update an existing user.'''
    user_id = '5c3c03c7c6666647e3204792'
    user = {'birthdate': '1981-01-12', 'first_name': 'Nathan',
            'last_name': 'Naws'}
    response = requests.put(API_URL + user_id, json=user)
    assert response.status_code == 204
    # Make sure that the record really was updated.
    response = requests.get(API_URL + user_id)
    resource = response.json()['resource']
    del resource['_id']
    assert resource == user

def test_post_user():
    '''Post a new user and then GET it using the returned ID.'''
    user1 = {'first_name': 'Artemis', 'last_name': 'Fowl',
            'birthdate': '2000-01-01'}
    response1 = requests.post(API_URL, json=user1)
    assert response1.status_code == 201
    _id = response1.json()['_id']
    response2 = requests.get(API_URL + _id)
    user2 = response2.json()['resource']
    # Make sure the received resource is the same as the posted one.
    # (This dict equality test feels like it shouldn't work right but it does.)
    del user2['_id']
    assert user1 == user2

def test_post_empty_user():
    '''Attempt to post an empty user.'''
    user = {}
    response = requests.post(API_URL, json=user)
    assert response.status_code == 400
