import pytest
import requests
import json

# Import the testing data.
import data.data as data

json_header = {'content-type': 'application/json'}

def test_insert_run():
    requests.post('http://localhost:5000/api/workouts',
                  data=json.dumps(data.indoor_run_doc),
                  headers=json_header)
