from flask import request
from flask_restful import Resource, marshal_with, abort
# Necessary for querying documents by their ID in mongo.
from bson import ObjectId
from safe_document import SafeDocument

response_fields = {
        'resource': SafeDocument 
}

class Workout(Resource):
    '''Any kind of workout.'''
    def __init__(self, db):
        self.db = db

    @marshal_with(response_fields)
    def get(self, **kwargs):
        workout_id = kwargs.get('workout_id')
        # If a workout_id was passed, convert it to an ObjectId and query mongo
        # for it.
        if workout_id is not None:
            object_id = ObjectId(workout_id)
            workouts = self.db.workouts.find({'_id': object_id})
            # Check that the ID returned a result.
            if workouts.count() < 1:
                return {'message': 'No such workout_id'}, 400
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
        # Unlike in GET requests, the request *must* specify an ID.
        workout_id = ObjectId(workout_id)
        # Delete it from the collection.
        result = self.db.workouts.delete_one({'_id': workout_id})
        if result.deleted_count == 1:
            return {}, 204
        else:
            return {'message': 'No such workout_id'}, 400

    def put(self, workout_id):
        raise NotImplementedError
        # return a 204 code

    def post(self):
        workout = request.get_json()
        # Blindly assume the resource is valid.
        workout_id = self.db.workouts.insert_one(workout).inserted_id
        return {'_id': str(workout_id)}, 201
