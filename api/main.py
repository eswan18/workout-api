import os, functools
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

#client = None

# Define a wrapper we'll need for our class methods.
def prepare_for_json(f):
    '''Make a returned list or dict safe to jsonify.'''
    unsafe_keys = ['_id', 'time']
    @functools.wraps(f)
    def make_dict_safe(d):
        for key in unsafe_keys:
            if key in d.keys():
                d[key] = str(d[key])
        return d
    def wrapper(*args, **kwargs):
        result = f(*args, **kwargs)
        # Assume the result is a dict, but if that fails, assume it's a list.
        try:
            result = make_dict_safe(result)
        except AttributeError:
            result = list(map(make_dict_safe, result))
        return result
    return wrapper


class Workout(Resource):
    '''An instance of any kind of workout.'''

    @prepare_for_json
    def get(self, workout_id):
        # Convert the workout_id to an ObjectId and query mongo for it.
        object_id = ObjectId(workout_id)
        workouts = db.workouts.find({'_id': object_id})
        # Check that the ID returned a result.
        if workouts.count() < 1:
            raise ValueError('No such ID in workouts database')
        # Assume that only one result was returned, so we can take the first
        # element retrned by the cursor
        response = workouts.next()
        workouts.close()
        return response

    def delete(self, workout_id):
        raise NotImplementedError
    def put(self, workout_id):
        return NotImplementedError
    def post(self):
        return NotImplementedError

class User(Resource):
    '''A user of the app.'''
    def get(self, user_id):
        return NotImplementedError
    def delete(self, user_id):
        return NotImplementedError
    def put(self, user_id):
        return NotImplementedError
    def post(self):
        return NotImplementedError


api.add_resource(Workout, '/workout/<string:workout_id>')
api.add_resource(User, '/user/<string:user_id>')

if __name__ == '__main__':
    # Connect to mongo
    client = MongoClient('rpi3-1')
    db = client[db_name]
    app.run()
