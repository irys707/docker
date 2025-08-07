#!/bin/bash
# Fix permissions before running the app

mkdir -p /app/app/storage/uploads /app/app/storage/results
chown -R appuser:appuser /app/app/storage

exec gosu appuser python run.py
