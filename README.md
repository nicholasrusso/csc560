
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
4. TODO: Need scripts to initialize the database here.
5. From within the Docker container's bash session, run `python3 evalQueries.py <EPOCHS>` to run a quick evaluation of the system with the test data, where <EPOCHS> is a positive integer denoting the number of times to run the set of test queries through the train/test process.
6. To exit the Docker container, run `exit` or press `ctrl + d`.
7. To stop the running Docker container, run `./stop_docker.sh`.