#!/bin/bash

# Create required folders if not exist
mkdir -p /app/app/storage/uploads /app/app/storage/results

# Fix ownership for appuser
chown -R appuser:appuser /app/app/storage

# Drop privileges and run Flask app
exec gosu appuser python run.py
