#!/usr/bin/env bash
# Use this script to run our entire project.
printf "Demo Starting..."
printf "Deleting Previous Materialzed Views"
psql -Upostgres -hdatabase -f dropM.psql > dev/null
printf "\nParsing and Creating Materialzed Views"
python3 train.py queries.sql
printf "\nConverting Queries"
python3 testing.py queries.sql
printf "\nRunning Eval"
python3 evalQueries.py 4
