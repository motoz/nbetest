all: build

build:
	docker build -t nbetest:latest -f Dockerfile --no-cache=true .
upload:
	docker tag nbetest:latest nulldevil/nbetest:latest
	docker push nulldevil/nbetest:latest
up:
	COMPOSE_PROJECT_NAME=nbetest COMPOSE_IGNORE_ORPHANS=True docker-compose -f docker-compose.yml up -d
down:
	COMPOSE_PROJECT_NAME=nbetest COMPOSE_IGNORE_ORPHANS=True docker-compose -f docker-compose.yml down
