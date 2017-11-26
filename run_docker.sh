#!/usr/bin/env bash

CWD=$(pwd)
CONTAINER_ID=$(docker run -d -v "$CWD:/project" csc560)
docker exec -it "$CONTAINER_ID" /bin/bash
docker stop "$CONTAINER_ID"
