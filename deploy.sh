#!/bin/bash
# Deployment script for Health Chatbot
# Usage: ./deploy.sh

set -e  # Exit on error

echo "🚀 Starting deployment for gpt.shoryakumar.in..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# Check if running on EC2
if [ ! -f /etc/cloud/cloud.cfg ]; then
    print_error "This script should be run on an EC2 instance"
    exit 1
fi

# Update system
print_info "Updating system packages..."
sudo apt update && sudo apt upgrade -y
print_success "System updated"

# Install dependencies
print_info "Installing dependencies..."
sudo apt install -y python3 python3-pip python3-venv \
    postgresql-client nginx certbot python3-certbot-nginx \
    git build-essential libpq-dev
print_success "Dependencies installed"

# Create app directory
print_info "Setting up application directory..."
sudo mkdir -p /var/www
sudo chown ubuntu:ubuntu /var/www
cd /var/www

# Clone repository (if not already cloned)
if [ ! -d "health-chatbot" ]; then
    print_info "Enter your repository URL:"
    read REPO_URL
    git clone $REPO_URL health-chatbot
    print_success "Repository cloned"
else
    print_info "Repository already exists, pulling latest changes..."
    cd health-chatbot
    git pull
fi

cd /var/www/health-chatbot

# Create virtual environment
if [ ! -d "venv" ]; then
    print_info "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Activate virtual environment and install dependencies
print_info "Installing Python packages..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
print_success "Python packages installed"

# Create .env file
if [ ! -f ".env" ]; then
    print_info "Creating .env file..."
    cat > .env << 'EOF'
# Database Configuration
RDS_HOSTNAME=ft-internal-new.cxok8ouastuu.eu-north-1.rds.amazonaws.com
RDS_PORT=5432
RDS_DB_NAME=postgres
RDS_USERNAME=postgres
RDS_PASSWORD=postgres

# Django Settings - PRODUCTION
DEBUG=False
SECRET_KEY=REPLACE_WITH_GENERATED_KEY
ALLOWED_HOSTS=gpt.shoryakumar.in

# CORS Settings
CORS_ALLOW_ALL_ORIGINS=True
EOF

    # Generate secret key
    SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    sed -i "s/REPLACE_WITH_GENERATED_KEY/$SECRET_KEY/" .env
    chmod 600 .env
    print_success ".env file created with generated SECRET_KEY"
else
    print_info ".env file already exists, skipping..."
fi

# Database setup
print_info "Setting up database..."
python3 manage.py migrate
python3 manage.py load_demo_data
python3 manage.py collectstatic --noinput
print_success "Database setup complete"

# Create log directory
sudo mkdir -p /var/log/gunicorn
sudo chown ubuntu:www-data /var/log/gunicorn

# Create systemd service
print_info "Creating systemd service..."
sudo tee /etc/systemd/system/health-chatbot.service > /dev/null << 'EOF'
[Unit]
Description=Health Chatbot Gunicorn daemon
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/health-chatbot
Environment="PATH=/var/www/health-chatbot/venv/bin"
EnvironmentFile=/var/www/health-chatbot/.env
ExecStart=/var/www/health-chatbot/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/var/www/health-chatbot/gunicorn.sock \
          --access-logfile /var/log/gunicorn/access.log \
          --error-logfile /var/log/gunicorn/error.log \
          config.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable health-chatbot
sudo systemctl start health-chatbot
print_success "Systemd service created and started"

# Configure Nginx
print_info "Configuring Nginx..."
sudo tee /etc/nginx/sites-available/health-chatbot > /dev/null << 'EOF'
server {
    listen 80;
    server_name gpt.shoryakumar.in;

    client_max_body_size 100M;

    location = /favicon.ico {
        access_log off;
        log_not_found off;
    }

    location /static/ {
        alias /var/www/health-chatbot/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/health-chatbot/gunicorn.sock;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/health-chatbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
print_success "Nginx configured"

# Configure firewall
print_info "Configuring firewall..."
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
echo "y" | sudo ufw enable
print_success "Firewall configured"

# Test HTTP
print_info "Testing HTTP connection..."
sleep 2
HTTP_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://gpt.shoryakumar.in/api/health/)
if [ "$HTTP_STATUS" -eq 200 ]; then
    print_success "HTTP working correctly (Status: $HTTP_STATUS)"
else
    print_error "HTTP test failed (Status: $HTTP_STATUS)"
fi

# SSL Setup
print_info ""
print_info "======================================"
print_info "HTTP deployment complete!"
print_info "======================================"
print_info ""
print_info "Next step: Install SSL certificate"
print_info "Run the following command:"
print_info ""
echo "  sudo certbot --nginx -d gpt.shoryakumar.in"
print_info ""
print_info "Follow the prompts to:"
print_info "1. Enter your email"
print_info "2. Agree to terms"
print_info "3. Choose option 2 to redirect HTTP to HTTPS"
print_info ""
print_success "Deployment script completed!"
print_info ""
print_info "Service status:"
sudo systemctl status health-chatbot --no-pager -l
