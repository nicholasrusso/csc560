
# CSC 560 Project
Index Assistant/Materialized View Creator
Sam Hsu, Nick Russo, Brandon Cooper, Daniel Girerd

## Installation requirements
* Docker with Docker Compose (default MacOS Docker installation comes with Docker Compose)

## How to run

NOTE: These instructions assume all commands are run from the top-level project directory.

1. Run `./build_docker.sh` to build the Docker container. This will require an internet connection and may take a few minutes to download and install the container images.
2. Run `./run_docker.sh` to start the Docker container in headless mode.
3. Run `./enter_560_container.sh` to enter a bash session within the Docker container.
4. Run `./db_create.sh` from within Docker container.
5. From within the Docker container's bash session, run `./demo.sh` to run a quick system test and print a comparison between running the given queries without our automated materialized views and with our automated materialized views.
6. To exit the Docker container, run `exit` or press `ctrl + d`.
7. To stop the running Docker container, run `./stop_containers.sh`.
