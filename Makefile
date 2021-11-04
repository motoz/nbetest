all: build

build:
	docker build -t nbetest:latest -f Dockerfile --no-cache=true .
