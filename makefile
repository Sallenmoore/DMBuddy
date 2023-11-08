
.PHONY: all build run clean deepclean test tests debug cleandebug

all: test clean run

include .env
export

APP_NAME?=dmbuddy
CONTAINERS=$$(sudo docker ps --filter "name=${APP_NAME}" -q)

###### BUILD and RUN #######
build:
	docker-compose build --no-cache

run:
	docker-compose up --build -d

###### CLEANING #######

clean:
	sudo docker ps -a
	-docker-compose down --remove-orphans
	
deepclean: clean
	-sudo docker kill $(CONTAINERS)
	-sudo docker container prune -f
	-sudo docker image prune -f
	-sudo docker network prune -f
	-sudo docker system prune -a -f --volumes

###### TESTING #######

debug: clean run
	docker-compose logs -f

cleandebug: build debug

tests: 
	docker-compose up --build -d
	docker compose logs --timestamps
	docker exec -it $(APP_NAME) python -m pytest --cov=app -rP -rx -l -x --log-level=INFO --no-cov-on-fail

cleantests: clean build tests
