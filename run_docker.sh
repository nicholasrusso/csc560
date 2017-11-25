#!/usr/bin/env bash

CONTAINER_ID=$(docker run -d csc560)
docker exec -it "$CONTAINER_ID" /bin/bash
