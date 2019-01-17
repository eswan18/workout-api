from flask import request
from flask_restful import Resource, marshal_with, abort
# Necessary for querying documents by their ID in mongo.
from bson import ObjectId
from safe_document import SafeDocument
response_fields = {
        'resource': SafeDocument 
}

class User(Resource):
    '''A user of the app.'''
    def __init__(self, db):
        self.db = db

    @marshal_with(response_fields)
    def get(self, **kwargs):
        user_id = kwargs.get('user_id')
        # If a user_id was passed, convert it to an ObjectId and query mongo
        # for it.
        if user_id is not None:
            object_id = ObjectId(user_id)
            users = self.db.users.find({'_id': object_id})
            # Check that the ID returned a result.
            if users.count() < 1:
                raise ValueError('No such user ID in database')
            # Assume that only one result was returned, so we can take the first
            # element returned by the cursor.
            response = users.next()
            users.close()
            return {'resource': response}
        # If no user_id was passed, return all users.
        else:
            users = self.db.users.find()
            response = list(users)
            return {'resource': response}


    def delete(self, user_id):
        raise NotImplementedError
        # return a 204 code
        
    def put(self, user_id):
        raise NotImplementedError
        # return a 204 code

    def post(self):
        new_user = request.get_json()
        # Blindly assume the resource is valid.
        new_user_id = self.db.users.insert_one(new_user).inserted_id
        return {'_id': str(new_user_id)}, 201

