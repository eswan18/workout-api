# Workout App

### Trello Boards:
- **API**: [https://trello.com/b/p83BVfus/workout-app-api](https://trello.com/b/p83BVfus/workout-app-api)
- **Front-end**: [https://trello.com/b/mF9YLzlG/workout-app-front-end](https://trello.com/b/mF9YLzlG/workout-app-front-end)

### Running the Restful API
1. Build the image. From within the `api` directory:
    ```bash
    docker build -t workout_app_api .
    ```
2. Then launch the container, mapping port 5000 to the local machine:
    ```bash
    docker run -p 5000:5000 workout_app_api
    ```
The API will then be accessible at `http://localhost:5000`.

### Running Tests
Each component (API and front-end) currently has its own tests.

#### Testing the API
To test the API, first ensure that you have
[pytest](https://docs.pytest.org/en/latest/) installed.
Then start the API service (see above) and run
```bash
pytest
```
from within the `api` directory.
