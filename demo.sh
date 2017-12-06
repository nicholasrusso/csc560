#!/usr/bin/env bash
# Use this script to run our entire project.
printf "Demo Starting...\n"
printf "Deleting Previous Materialzed Views\n"
psql -Upostgres -hdatabase -f dropM.psql > /dev/null 2>&1
printf "\nParsing and Creating Materialzed Views\n"
python3 train.py queries.sql
printf "\nConverting Queries\n"
python3 testing.py queries.sql
printf "\nRunning Eval\n"
python3 evalQueries.py 4
