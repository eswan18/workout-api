import pytest
import requests
import json

# Import the testing data.
import data.data as data

API_URL = 'http://localhost:5000'

#json_header = {'content-type': 'application/json'}

def test_get_workout():
    object_id = '5c395e6dc62a663afe045e00'
    response = requests.get(API_URL + '/workout/' + object_id)
    data = response.json()
    resource = data['resource']
    assert resource['distance'] == 3.69
    assert resource['title'] == 'Outdoor Run'
def test_get_all_workouts():
    pass

#def test_insert_run():
#    requests.post('http://localhost:5000/api/workouts',
#                  data=json.dumps(data.indoor_run_doc),
#                  headers=json_header)
