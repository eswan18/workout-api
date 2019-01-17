import pytest
import requests

# Import the testing data.
import data.data as data

API_URL = 'http://localhost:5000/workout/'

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
    assert len(resource) > 0
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
    assert response.status_code == 400

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
