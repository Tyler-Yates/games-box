#!/usr/bin/env bash

poetry update -v
poetry export --without-hashes -f requirements.txt --output requirements.txt
