#!/bin/bash

./dc.sh exec app alembic revision --autogenerate -m "$@"
