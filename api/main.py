import os
from flask import Flask
from flask_restful import Api
from pymongo import MongoClient
from resources import Workout, User

app = Flask(__name__)
api = Api(app)

# Make decisions for external connections based on whether we're in production.
if 'WORKOUT_APP_PROD' in os.environ:
    db_name = 'workout_app'
else:
    db_name = 'workout_app_dev'

if __name__ == '__main__':
    # Connect to mongo
    client = MongoClient('rpi3-1')
    db = client[db_name]
    # Add the workout and user resource models to the API.
    api.add_resource(Workout, '/workout/', '/workout/<string:workout_id>',
            resource_class_kwargs={'db': db})
    api.add_resource(User, '/user/', '/user/<string:user_id>',
            resource_class_kwargs={'db': db})
    app.run()
