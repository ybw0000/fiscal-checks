#!/bin/bash

# Check docker-compose command
if [ -x "$(command -v docker-compose)" ]; then
  dockercompose="docker-compose"
else
  dockercompose="docker compose"
fi


# Local file
if [ -f "docker-compose.local.yaml" ]; then
  localfile="-f docker-compose.local.yaml"
else
  localfile="" 
fi

$dockercompose -f docker-compose.yaml $localfile --env-file .env "$@"
