#!/bin/bash

DATABASE_HOST=$(grep -e "^DATABASE_HOST" ./app/src/.env | cut -d '=' -f2 | xargs)
DATABASE_PORT=$(grep -e "^DATABASE_PORT" ./app/src/.env | cut -d '=' -f2 | xargs)
DATABASE_NAME=$(grep -e "^DATABASE_NAME" ./app/src/.env | cut -d '=' -f2 | xargs)
DATABASE_USER=$(grep -e "^DATABASE_USER" ./app/src/.env | cut -d '=' -f2 | xargs)
DATABASE_PASSWORD=$(grep -e "^DATABASE_PASSWORD" ./app/src/.env | cut -d '=' -f2 | xargs)

# Run
./dc.sh exec -e "PGPASSWORD=$DATABASE_PASSWORD" postgres psql \
  -h "$DATABASE_HOST" -p "$DATABASE_PORT" \
  -U "$DATABASE_USER" -d "$DATABASE_NAME"
