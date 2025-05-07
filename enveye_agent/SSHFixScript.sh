#!/bin/bash

echo "🔧 Configuring SSH for remote collection..."

# 1. Install OpenSSH server if not already installed
if ! command -v sshd >/dev/null; then
  echo "📦 Installing OpenSSH server..."
  if [ -f /etc/debian_version ]; then
    sudo apt update && sudo apt install -y openssh-server
  elif [ -f /etc/redhat-release ]; then
    sudo yum install -y openssh-server
  fi
fi

# 2. Enable and start SSH service
echo "🚀 Enabling SSH service..."
sudo systemctl enable ssh
sudo systemctl start ssh

# 3. Allow password authentication in sshd config
echo "🔐 Enabling password authentication..."
sudo sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
sudo sed -i 's/^#*PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config
sudo systemctl restart ssh

# 4. Open SSH port in firewall
echo "🌐 Opening SSH port in firewall..."
if command -v ufw >/dev/null; then
  sudo ufw allow ssh
elif command -v firewall-cmd >/dev/null; then
  sudo firewall-cmd --permanent --add-service=ssh
  sudo firewall-cmd --reload
fi

# 5. Confirm
echo -e "\n✅ SSH setup completed. You can now connect via SSH using username and password."
