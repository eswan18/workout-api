from . import exercise_types
from . import sets
from . import workouts
from . import workout_types
from . import users
from . import token

# Order matters here: this is the order in which the endpoints will be displayed in docs
routers = {
    "Token": token.router,
    "Users": users.router,
    "Exercise Types": exercise_types.router,
    "Sets": sets.router,
    "Workouts": workouts.router,
    "Workout Types": workout_types.router,
}
