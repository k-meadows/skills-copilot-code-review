#!/bin/bash

set -euo pipefail

error() {
	echo "[startMongoDB] ERROR: $1" >&2
	exit 1
}

info() {
	echo "[startMongoDB] $1"
}

if ! command -v mongod >/dev/null 2>&1; then
	error "'mongod' not found. Run ./.devcontainer/installMongoDB.sh first and confirm installation succeeded."
fi

log_dir="/var/log/mongodb"
log_file="$log_dir/mongod.log"

sudo mkdir -p "$log_dir"

if pgrep -x mongod >/dev/null 2>&1; then
	info "MongoDB is already running."
else
	info "Starting MongoDB..."
	sudo mongod --fork --logpath "$log_file" --bind_ip 127.0.0.1 --dbpath /data/db
fi

if ! pgrep -x mongod >/dev/null 2>&1; then
	error "MongoDB did not start. Check $log_file for details."
fi

info "MongoDB started successfully."
mongod --version

if command -v mongosh >/dev/null 2>&1; then
	echo "Current databases:"
	mongosh --quiet --eval "db.getMongo().getDBNames()"
else
	info "'mongosh' not found; skipping database listing."
fi