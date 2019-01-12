from datetime import datetime

# Example Run Records
outdoor_run_doc = {'title': 'Outdoor Run',
                   'duration_minutes': 24,
                   'duration_seconds': 34,
                   'distance': 2.85,
                   'distance_unit': 'miles',
                   'time': datetime(2018, 1, 1, 3, 30)}
indoor_run_doc =  {'title': 'Treadmill Run',
                   'duration_minutes': 13,
                   'duration_seconds': 32,
                   'distance': 2,
                   'distance_unit': 'miles',
                   'time': datetime(2020, 1, 2, 14, 12)}
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
                 'time': datetime(2015,  3, 4, 5, 46)}
