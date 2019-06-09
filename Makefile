.PHONY: all
all: test

REPO ?= svrakitin/tictactoe
TAG ?= dev

.PHONY: build
build:
	docker build . -t ${REPO}:${TAG}

.PHONY: test
test: build
	docker run --rm -ti ${REPO}:${TAG} python -m pytest

.PHONY: run-dev
run-dev: build
	docker-compose -f docker-compose.dev.yml up