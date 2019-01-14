import os, functools, copy
from numbers import Number
from flask import Flask
from flask_restful import Resource, Api, fields, marshal_with
from pymongo import MongoClient
# Necessary for querying documents by their ID in mongo.
from bson import ObjectId

app = Flask(__name__)
api = Api(app)

# Make decisions for external connections based on whether we're in production.
if 'WORKOUT_APP_PROD' in os.environ:
    db_name = 'workout_app'
else:
    db_name = 'workout_app_dev'

class SafeDocuments(fields.Raw):
    '''JSON-safe Mongo document or documents.'''
    def format(self, value):
        # See if the object is easily coerced to JSON.
        try:
            j = json.loads(value)
        except:
            # We probably shouldn't alter the original value, which is likely
            # mutable.
            value = copy.deepcopy(value)
            # Define a recursive function for making dicts and lists safe.
            def make_safe(x):
                '''Make a list or dictionary JSON-safe.'''
                # If it isn't an iterable, make sure it's a string or a number.
                if not isinstance(x, list) and not isinstance(x, dict):
                    if isinstance(x, Number):
                        return x
                    else:
                        return str(x)
                # If it's a dictionary, make each value safe.
                if isinstance(x, dict):
                    for key in x.keys():
                       x[key] = make_safe(x[key]) 
                    return x
                # If it's a list, make each element safe.
                if isinstance(x, list):
                    return [make_safe(e) for e in x]
            value = make_safe(value)
        return value

response_fields = {
        'resource': SafeDocuments 
}

class Workout(Resource):
    '''Any kind of workout.'''

    @marshal_with(response_fields)
    def get(self, **kwargs):
        workout_id = kwargs.get('workout_id')
        # If a workout_id was passed, convert the workout_id to an ObjectId and
        # query mongo for it.
        if workout_id is not None:
            object_id = ObjectId(workout_id)
            workouts = db.workouts.find({'_id': object_id})
            # Check that the ID returned a result.
            if workouts.count() < 1:
                raise ValueError('No such ID in workouts database')
            # Assume that only one result was returned, so we can take the first
            # element retrned by the cursor
            response = workouts.next()
            workouts.close()
            return {'resource': response}
        # If no workout_id was passed, return all workouts.
        else:
            workouts = db.workouts.find()
            response = list(workouts)
            return {'resource': response}

    @marshal_with(response_fields)
    def delete(self, workout_id):
        raise NotImplementedError
    @marshal_with(response_fields)
    def put(self, workout_id):
        return NotImplementedError
    @marshal_with(response_fields)
    def post(self):
        return NotImplementedError

class User(Resource):
    '''A user of the app.'''
    @marshal_with(response_fields)
    def get(self, user_id):
        return NotImplementedError
    @marshal_with(response_fields)
    def delete(self, user_id):
        return NotImplementedError
    @marshal_with(response_fields)
    def put(self, user_id):
        return NotImplementedError
    @marshal_with(response_fields)
    def post(self):
        return NotImplementedError


# Add the workout and user resource models to the API.
api.add_resource(Workout, '/workout/', '/workout/<string:workout_id>')
api.add_resource(User, '/user/<string:user_id>')

if __name__ == '__main__':
    # Connect to mongo
    client = MongoClient('rpi3-1')
    db = client[db_name]
    app.run()
