#!/usr/bin/env bash
#things needed: pip, curl, tailscale installation
#MUST BE RUN AS ROOT!
set -e
echo "tailscale install started"
if command -v curl >/dev/null 2>&1; then
    curl -fsSL https://tailscale.com/install.sh | sh
else
    echo "curl is not installed! installing..."
    apt update && apt install -y curl
    curl -fsSL https://tailscale.com/install.sh | sh
fi
apt install -y python3-requests 
#tailscale set --operator=$USER
systemctl start tailscaled
systemctl status tailscaled
echo "tailscale installed."
