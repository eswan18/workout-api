import requests

# Import the testing data.
import data.data as data

API_URL = 'http://localhost:5000/user/'

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
    assert len(resource) > 0
    assert all([x.get('first_name') is not None for x in resource])
