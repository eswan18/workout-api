import pytest
import requests

# Import the testing data.
import data.data as data

API_URL = 'http://localhost:5000/workout/'

def test_get_workout():
    object_id = '5c395e6dc62a663afe045e00'
    response = requests.get(API_URL + object_id)
    data = response.json()
    resource = data['resource']
    assert resource['distance'] == 3.69
    assert resource['title'] == 'Outdoor Run'

def test_get_all_workouts():
    response = requests.get(API_URL)
    data = response.json()
    resource = data['resource']
    assert isinstance(resource, list)
    assert len(resource) > 0
    assert all([x.get('title') is not None for x in resource])

def test_post_workout():
    '''Post a new workout and then GET it using the returned ID.'''
    wkt1 = {'title': 'Lift Push', 'sets':
                [{'exercise': 'Bench Press', 'weight': 135, 'reps': 10}],
            'time': '2019-05-03 10:00:00'}
    response1 = requests.post(API_URL, json=wkt1)
    _id = response1.json()['_id']
    response2 = requests.get(API_URL + _id)
    wkt2 = response2.json()['resource']
    # Make sure the received resource is the same as the posted one.
    # (This dict equality test feels like it shouldn't work right but it does.)
    del wkt2['_id']
    assert wkt1 == wkt2
