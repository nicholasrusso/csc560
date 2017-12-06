#!/usr/bin/env bash
# Use this script to create the original database
printf "\nCreating Database\n"
createdb -Upostgres -hdatabase test
printf "\nImporting database, please wait.\n"
psql -Upostgres -hdatabase test < final_db.sql > /dev/null 2>&1
printf "\nDatabase Finished\n"
