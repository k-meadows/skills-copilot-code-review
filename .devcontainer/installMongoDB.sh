#!/bin/bash

set -euo pipefail

error() {
	echo "[installMongoDB] ERROR: $1" >&2
	exit 1
}

info() {
	echo "[installMongoDB] $1"
}

if [[ ! -f /etc/os-release ]]; then
	error "Cannot detect OS (/etc/os-release not found)."
fi

source /etc/os-release

if [[ "${ID:-}" != "debian" ]]; then
	error "Unsupported distro '${ID:-unknown}'. This script only supports Debian-based devcontainers."
fi

codename="${VERSION_CODENAME:-}"
if [[ -z "$codename" ]]; then
	error "Could not determine Debian codename from /etc/os-release."
fi

if [[ "$codename" == "trixie" ]]; then
	info "Debian '$codename' detected; using MongoDB Debian 'bookworm' repository for compatibility."
	codename="bookworm"
fi

repo_file="/etc/apt/sources.list.d/mongodb-org-8.0.list"
keyring_file="/usr/share/keyrings/mongodb-server-8.0.gpg"
legacy_repo_file="/etc/apt/sources.list.d/mongodb-org-7.0.list"

if [[ -f "$legacy_repo_file" ]]; then
	info "Removing legacy Ubuntu MongoDB apt source: $legacy_repo_file"
	sudo rm -f "$legacy_repo_file"
fi

if ! command -v curl >/dev/null 2>&1 || ! command -v gpg >/dev/null 2>&1; then
	info "Installing required tooling..."
	sudo apt-get update
	sudo apt-get install -y curl gpg
fi

info "Configuring MongoDB apt key..."
curl -fsSL https://pgp.mongodb.com/server-8.0.asc | sudo gpg --dearmor --yes -o "$keyring_file"

info "Configuring MongoDB apt repository for Debian '$codename'..."
echo "deb [ signed-by=$keyring_file arch=amd64,arm64 ] https://repo.mongodb.org/apt/debian $codename/mongodb-org/8.0 main" | sudo tee "$repo_file" >/dev/null

info "Installing MongoDB packages..."
sudo apt-get update
sudo apt-get install -y mongodb-org

info "Preparing MongoDB data directory..."
sudo mkdir -p /data/db
if id mongodb >/dev/null 2>&1; then
	sudo chown -R mongodb:mongodb /data/db
else
	info "User 'mongodb' not found; skipping ownership change for /data/db."
fi

info "MongoDB installation completed."
