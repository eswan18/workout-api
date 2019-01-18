import pytest
import requests
import pymongo

# Import the testing data that will populate the mongo collection.
from data.data import workouts as workouts_collection

API_URL = 'http://localhost:5000/workout/'
MONGO_URL = 'rpi3-1'
MONGO_DB = 'workout_app_dev'

db = pymongo.MongoClient(MONGO_URL)[MONGO_DB]

@pytest.fixture(autouse=True)
def reset_collection():
    '''Hacky (?) way to reset mongo between tests.'''
    db.workouts.delete_many({})
    db.workouts.insert_many(workouts_collection)

def test_get_workout():
    object_id = '5c40771ac62a666a02ab1910'
    response = requests.get(API_URL + object_id)
    data = response.json()
    resource = data['resource']
    assert resource['distance'] == 3.69
    assert resource['title'] == 'Outdoor Run'
    assert response.status_code == 200

def test_get_all_workouts():
    response = requests.get(API_URL)
    data = response.json()
    resource = data['resource']
    assert isinstance(resource, list)
    assert len(resource) == 8
    assert all([x.get('title') is not None for x in resource])
    assert response.status_code == 200

def test_delete_workout():
    '''Try to delete the first workout that comes back from GET.'''
    all_workouts = requests.get(API_URL).json()['resource']
    first_workout_id = all_workouts[0]['_id']
    response = requests.delete(API_URL + first_workout_id)
    assert response.status_code == 204
    # Try to retrieve the id again with GET.
    response = requests.get(API_URL + first_workout_id)
    assert response.status_code == 404

def test_put_workout():
    '''Update an existing workout.'''
    wkt_id = '5c407631c62a6669baedbf2c'
    wkt = {'time': '2018-12-21 11:53:17', 'title': 'Indoor Run',
           # Here begins new stuff
           'distance': 3.03, 'duration': '21:10', 'distance_unit': 'miles'}
    response = requests.put(API_URL + wkt_id, json=wkt)
    assert response.status_code == 204
    # Make sure that the record really was updated.
    response = requests.get(API_URL + wkt_id)
    resource = response.json()['resource']
    del resource['_id']
    assert resource == wkt

def test_post_workout():
    '''Post a new workout and then GET it using the returned ID.'''
    wkt1 = {'title': 'Lift Push', 'sets':
                [{'exercise': 'Bench Press', 'weight': 135, 'reps': 10}],
            'time': '2019-05-03 10:00:00'}
    response1 = requests.post(API_URL, json=wkt1)
    assert response1.status_code == 201
    _id = response1.json()['_id']
    response2 = requests.get(API_URL + _id)
    wkt2 = response2.json()['resource']
    # Make sure the received resource is the same as the posted one.
    # (This dict equality test feels like it shouldn't work right but it does.)
    del wkt2['_id']
    assert wkt1 == wkt2

def test_post_empty_workout():
    '''Attempt to post an empty workout.'''
    wkt = {}
    response = requests.post(API_URL, json=wkt)
    assert response.status_code == 400
