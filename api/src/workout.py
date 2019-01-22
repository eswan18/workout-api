from flask import request
from flask_restful import Resource, marshal_with, abort
# Necessary for querying documents by their ID in mongo.
from bson import ObjectId
from safe_document import SafeDocument

response_fields = {
        'resource': SafeDocument 
}
# Mandatory fields in any workout.
request_fields = ['title', 'time']

class Workout(Resource):
    '''Any kind of workout.'''
    def __init__(self, db):
        self.db = db

    @marshal_with(response_fields)
    def get(self, **kwargs):
        '''Retrieve one or all workouts.'''
        workout_id = kwargs.get('workout_id')
        # If a workout_id was passed, convert it to an ObjectId and query mongo
        # for it.
        if workout_id is not None:
            object_id = ObjectId(workout_id)
            workouts = self.db.workouts.find({'_id': object_id})
            # Check that the ID returned a result.
            if workouts.count() < 1:
                return {'message': 'No such workout_id'}, 404
            # Assume that only one result was returned, so we can take the first
            # element returned by the cursor.
            response = workouts.next()
            workouts.close()
            return {'resource': response}, 200
        # If no workout_id was passed, return all workouts.
        else:
            workouts = self.db.workouts.find()
            response = list(workouts)
            return {'resource': response}, 200


    def delete(self, workout_id):
        '''Delete a workout.'''
        workout_id = ObjectId(workout_id)
        # Delete it from the collection.
        result = self.db.workouts.delete_one({'_id': workout_id})
        if result.deleted_count == 1:
            return {}, 204
        else:
            return {'message': 'No such workout_id'}, 400

    def put(self, workout_id):
        '''Update a workout.'''
        workout = request.get_json()
        workout_id = ObjectId(workout_id)
        # Validate the request data.
        if not set(workout.keys()).issuperset(request_fields):
            return {'message': 'Missing required field in passed data'}, 400
        # Check that there is a current version of this workout to delete.
        result = self.db.workouts.delete_one({'_id': workout_id})
        if result.deleted_count != 1:
            return {'message': 'No such workout_id'}, 400
        # With a successful deletion, add the new version of the workout.
        workout['_id'] = workout_id
        result = self.db.workouts.insert_one(workout)
        # It's important that we inserted the new workout under the same ID as
        # as the old one.
        assert workout_id == result.inserted_id
        return {'_id': str(workout_id)}, 204

    def post(self):
        '''Create a new workout.'''
        workout = request.get_json()
        # Validate the request data.
        if not set(workout.keys()).issuperset(request_fields):
            return {'message': 'Missing required field in passed data'}, 400
        # Add the new workout to mongo.
        result = self.db.workouts.insert_one(workout)
        workout_id = result.inserted_id
        return {'_id': str(workout_id)}, 201
