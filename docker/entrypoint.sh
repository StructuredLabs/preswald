#!/bin/bash
set -e

if [ -d "/app/project" ]; then
    echo "Using mounted project files from /app/project"
    cd /app/project
else
    echo "No project files mounted. Please mount your project files at /app/project"
    exit 1
fi

if [ ! -f "preswald.toml" ]; then
    echo "No project files mounted. Please mount your project files at /app/project"
    exit 1
fi

exec preswald run --port "${PORT:-8501}"
