from datetime import datetime
from bson import ObjectId

# Example Run Records
outdoor_run_doc = {'title': 'Outdoor Run',
                   'duration_minutes': 24,
                   'duration_seconds': 34,
                   'distance': 2.85,
                   'distance_unit': 'miles',
                   'time': '2019-01-11T17:00:00Z'}
indoor_run_doc =  {'title': 'Treadmill Run',
                   'duration_minutes': 13,
                   'duration_seconds': 32,
                   'distance': 2,
                   'distance_unit': 'miles',
                   'time': '2020-01-02T14:12:00Z'}
run_docs = [indoor_run_doc, indoor_run_doc, outdoor_run_doc, indoor_run_doc]
# Example Lift Records
push_lift_doc = {'title': 'Lift Push',
                 'sets': [{'exercise': 'Bench Press', 'weight': 135, 'reps':  8, 'rest': 50},
                          {'exercise': 'Bench Press', 'weight': 135, 'reps':  8, 'rest': 50},
                          {'exercise': 'Bench Press', 'weight': 135, 'reps': 10, 'rest': 50},
                          {'exercise': 'Bench Press', 'weight': 135, 'reps': 14, 'rest': 55},
                          {'exercise':   'Lat Raise', 'weight':  12, 'reps':  9, 'rest': 50},
                          {'exercise':   'Lat Raise', 'weight':  12, 'reps':  9, 'rest': 50},
                          {'exercise':   'Lat Raise', 'weight':  12, 'reps':  8, 'rest': 50},
                          {'exercise':   'Lat Raise', 'weight':  12, 'reps':  7, 'rest': 50}],
                 'time': '2015-03-04T05:46:00Z'}

workouts = [
        {'_id': ObjectId('5c40713dc62a66697a702bf8'),
         'sets': [{'exercise': 'Bench Press', 'reps': 10, 'weight': 135}],
         'time': '2019-05-03 10:00:00',
         'title': 'Lift Push'},
        {'_id': ObjectId('5c407617c62a6669baedbf2b'),
         'sets': [{'exercise': 'Bench Press', 'reps': 10, 'weight': 135}],
         'time': '2019-05-03 10:00:00',
         'title': 'Lift Push'},
        {'_id': ObjectId('5c407631c62a6669baedbf2c'),
         'sets': [{'exercise': 'Bench Press', 'reps': 10, 'weight': 135}],
         'time': '2019-05-03 10:00:00',
         'title': 'Lift Push'},
        {'_id': ObjectId('5c407641c62a6669baedbf2d'),
         'sets': [{'exercise': 'Bench Press', 'reps': 10, 'weight': 135}],
         'time': '2019-05-03 10:00:00',
         'title': 'Lift Push'},
        {'_id': ObjectId('5c407654c62a6669baedbf2e'),
         'sets': [{'exercise': 'Bench Press', 'reps': 10, 'weight': 135}],
         'time': '2019-05-03 10:00:00',
         'title': 'Lift Push'},
        {'_id': ObjectId('5c4076fdc62a6669baedbf2f'),
         'sets': [{'exercise': 'Bench Press', 'reps': 10, 'weight': 135}],
         'time': '2019-05-03 10:00:00',
         'title': 'Lift Push'},
        {'_id': ObjectId('5c407710c62a6669baedbf30'),
         'sets': [{'exercise': 'Bench Press', 'reps': 10, 'weight': 135}],
         'time': '2019-05-03 10:00:00',
         'title': 'Lift Push'},
        {'_id': ObjectId('5c40771ac62a666a02ab1910'),
         'title': 'Outdoor Run',
         'distance': 3.69,
         'distance_unit': 'miles',
         'duration': '28:35',
         'time': '2019-05-03 10:00:00'}
        ]
users = [
    {'_id': ObjectId('5c3c03c7c62a6647e3204792'),
     'birthdate': '1993-03-23',
     'first_name': 'Ethan',
     'last_name': 'Swan'},
    {'_id': ObjectId('5c3c03c7c6666647e3204792'),
     'birthdate': '1981-01-12',
     'first_name': 'Nate',
     'last_name': 'Naws'},
    ]
