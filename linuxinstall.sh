#!/usr/bin/env bash
set -e
echo "tailscale install started"
if command -v curl >/dev/null 2>&1; then
    curl -fsSL https://tailscale.com/install.sh | sh
else
    echo "curl is not installed! installing..."
    apt update && apt install -y curl
    curl -fsSL https://tailscale.com/install.sh | sh
fi
echo "Yes this thing is working"
