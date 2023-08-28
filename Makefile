SRC_DIR = app
TEST_DIR = tests
SRC_FILES = $(shell find $(SRC_DIR) -type f -name '*.py')
PORT ?= 8000

serve: $(SRC_FILES)
	# Run on port 8000 unless another port is specified
	uvicorn app.main:app --host 0.0.0.0 --port $(PORT)

devserve: $(SRC_FILES)
	uvicorn app.main:app --host 0.0.0.0 --port $(PORT) --reload

lint:
	ruff check $(SRC_DIR) $(TEST_DIR)

typecheck:
	mypy $(SRC_DIR)

test:
	coverage run --source $(SRC_DIR) -m pytest

check: lint typecheck test

docker-build:
	docker build --target=runtime . -t workout-api:latest

docker-run:
	docker-compose up
