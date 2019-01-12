from flask import Flask
from flask_restful import Resource, Api

app = Flask(__name__)
api = Api(app)

class Workout(Resource):
    def get(self):
        return NotImplementedError
    def delete(self):
        return NotImplementedError
    def put(self):
        return NotImplementedError
    def post(self):
        return NotImplementedError

class User(Resource):
    def get(self):
        return NotImplementedError
    def delete(self):
        return NotImplementedError
    def put(self):
        return NotImplementedError
    def post(self):
        return NotImplementedError

api.add_resource(Workout, '/workout/<string:workout_id>')
api.add_resource(User, '/user/<string:user_id>')

if __name__ == '__main__':
    app.run()
