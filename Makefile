SRC_DIR = app
SRC_FILES = $(shell find $(SRC_DIR) -type f -name '*.py')
PORT ?= 8000

serve: $(SRC_FILES)
	# Run on port 8000 unless another port is specified
	uvicorn api.main:app --host 0.0.0.0 --port $(PORT)

devserve: $(SRC_FILES)
	uvicorn api.main:app --host 0.0.0.0 --port $(PORT) --reload
