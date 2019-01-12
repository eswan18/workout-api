from datetime import datetime

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
