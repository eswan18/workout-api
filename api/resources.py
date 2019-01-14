from flask_restful import Resource, marshal_with
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
        # If a workout_id was passed, convert the workout_id to an ObjectId and
        # query mongo for it.
        if workout_id is not None:
            object_id = ObjectId(workout_id)
            workouts = self.db.workouts.find({'_id': object_id})
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
            workouts = self.db.workouts.find()
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

