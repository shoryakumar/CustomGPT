# Production Deployment Guide
## Deploying to https://gpt.shoryakumar.in

This guide covers deploying the Django health chatbot to production with HTTPS.

---

## Prerequisites

1. **EC2 Instance**: Ubuntu 20.04+ or Amazon Linux 2
2. **Domain**: gpt.shoryakumar.in pointing to EC2 IP
3. **RDS Database**: PostgreSQL instance accessible from EC2
4. **Security Group**: Ports 80, 443, 22 open

---

## Step 1: DNS Configuration

Add an A record in your domain registrar:

```
Type: A
Name: gpt
Value: <YOUR_EC2_PUBLIC_IP>
TTL: 300
```

Verify DNS propagation:
```bash
nslookup gpt.shoryakumar.in
# Should return your EC2 IP address
```

---

## Step 2: Connect to EC2 and Install Dependencies

```bash
# SSH into EC2
ssh -i your-key.pem ubuntu@<EC2_IP>

# Update system
sudo apt update && sudo apt upgrade -y

# Install Python, pip, and system dependencies
sudo apt install -y python3 python3-pip python3-venv
sudo apt install -y postgresql-client nginx certbot python3-certbot-nginx
sudo apt install -y git build-essential libpq-dev

# Verify installations
python3 --version
nginx -v
certbot --version
```

---

## Step 3: Clone and Set Up Project

```bash
# Create app directory
sudo mkdir -p /var/www
sudo chown ubuntu:ubuntu /var/www
cd /var/www

# Clone repository
git clone <YOUR_REPO_URL> health-chatbot
cd health-chatbot

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn
```

---

## Step 4: Configure Environment Variables

Create production `.env` file:

```bash
cat > .env << 'EOF'
# Database Configuration
RDS_HOSTNAME=ft-internal-new.cxok8ouastuu.eu-north-1.rds.amazonaws.com
RDS_PORT=5432
RDS_DB_NAME=postgres
RDS_USERNAME=postgres
RDS_PASSWORD=postgres

# Django Settings - PRODUCTION
DEBUG=False
SECRET_KEY=<GENERATE_A_STRONG_SECRET_KEY>
ALLOWED_HOSTS=gpt.shoryakumar.in

# CORS Settings
CORS_ALLOW_ALL_ORIGINS=True
EOF

# Generate a strong secret key
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# Copy the output and update SECRET_KEY in .env file
```

Secure the `.env` file:
```bash
chmod 600 .env
```

---

## Step 5: Set Up Database

```bash
# Activate virtual environment if not already
source /var/www/health-chatbot/venv/bin/activate

# Test database connection
python3 manage.py check

# Run migrations
python3 manage.py migrate

# Load demo data
python3 manage.py load_demo_data

# Collect static files
python3 manage.py collectstatic --noinput
```

---

## Step 6: Test Gunicorn

```bash
# Test run with Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000

# If successful, press Ctrl+C and continue
```

---

## Step 7: Create Systemd Service

Create service file:

```bash
sudo nano /etc/systemd/system/health-chatbot.service
```

Add this configuration:

```ini
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
```

Create log directory:
```bash
sudo mkdir -p /var/log/gunicorn
sudo chown ubuntu:www-data /var/log/gunicorn
```

Enable and start service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable health-chatbot
sudo systemctl start health-chatbot
sudo systemctl status health-chatbot
```

Check logs if there are issues:
```bash
sudo journalctl -u health-chatbot -f
```

---

## Step 8: Configure Nginx (Without SSL first)

Create Nginx configuration:

```bash
sudo nano /etc/nginx/sites-available/health-chatbot
```

Add this configuration:

```nginx
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
```

Enable the site:
```bash
# Create symbolic link
sudo ln -s /etc/nginx/sites-available/health-chatbot /etc/nginx/sites-enabled/

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

Test HTTP access:
```bash
curl http://gpt.shoryakumar.in/api/health/
```

---

## Step 9: Configure SSL with Let's Encrypt

Install SSL certificate:

```bash
# Run Certbot to install SSL certificate
sudo certbot --nginx -d gpt.shoryakumar.in

# Follow the prompts:
# - Enter your email address
# - Agree to terms of service
# - Choose whether to redirect HTTP to HTTPS (choose 2 for redirect)
```

Certbot will automatically:
- Obtain SSL certificate
- Modify Nginx configuration
- Set up auto-renewal

Verify SSL is working:
```bash
curl https://gpt.shoryakumar.in/api/health/
```

Test auto-renewal:
```bash
sudo certbot renew --dry-run
```

---

## Step 10: Configure Firewall

```bash
# Enable UFW firewall
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw enable

# Check status
sudo ufw status
```

Expected output:
```
Status: active

To                         Action      From
--                         ------      ----
OpenSSH                    ALLOW       Anywhere
Nginx Full                 ALLOW       Anywhere
```

---

## Step 11: EC2 Security Group Configuration

In AWS Console:

1. Go to EC2 → Security Groups
2. Find your EC2 instance's security group
3. Add inbound rules:

```
Type          Protocol  Port Range  Source
SSH           TCP       22          Your IP
HTTP          TCP       80          0.0.0.0/0
HTTPS         TCP       443         0.0.0.0/0
```

4. For RDS security group:
   - Allow inbound PostgreSQL (5432) from EC2 security group

---

## Step 12: Verify Deployment

Test all endpoints:

```bash
# Health check
curl https://gpt.shoryakumar.in/api/health/

# Chat endpoint
curl -X POST https://gpt.shoryakumar.in/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "What did I eat today?"}'

# List meals
curl https://gpt.shoryakumar.in/api/meals/

# Get summary
curl https://gpt.shoryakumar.in/api/summary/?period=week
```

---

## Maintenance Commands

### View Application Logs
```bash
# Gunicorn logs
sudo tail -f /var/log/gunicorn/access.log
sudo tail -f /var/log/gunicorn/error.log

# Systemd service logs
sudo journalctl -u health-chatbot -f

# Nginx logs
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### Restart Services
```bash
# Restart application
sudo systemctl restart health-chatbot

# Restart Nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status health-chatbot
sudo systemctl status nginx
```

### Update Application
```bash
cd /var/www/health-chatbot
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install new dependencies if any
pip install -r requirements.txt

# Run migrations
python3 manage.py migrate

# Collect static files
python3 manage.py collectstatic --noinput

# Restart application
sudo systemctl restart health-chatbot
```

### Database Operations
```bash
# Connect to Django shell
cd /var/www/health-chatbot
source venv/bin/activate
python3 manage.py shell

# Backup database
python3 manage.py dumpdata > backup_$(date +%Y%m%d).json

# Reset demo data
python3 manage.py load_demo_data
```

### SSL Certificate Renewal
```bash
# Renew certificate (automatic via cron)
sudo certbot renew

# Force renewal for testing
sudo certbot renew --force-renewal

# Check certificate expiry
sudo certbot certificates
```

---

## Monitoring & Health Checks

### Set Up Monitoring Script

Create monitoring script:
```bash
nano ~/monitor.sh
```

Add:
```bash
#!/bin/bash
ENDPOINT="https://gpt.shoryakumar.in/api/health/"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $ENDPOINT)

if [ $RESPONSE -eq 200 ]; then
    echo "✓ Health check passed: $RESPONSE"
else
    echo "✗ Health check failed: $RESPONSE"
    sudo systemctl restart health-chatbot
fi
```

Make executable and add to cron:
```bash
chmod +x ~/monitor.sh

# Add to crontab (runs every 5 minutes)
crontab -e
# Add this line:
# */5 * * * * /home/ubuntu/monitor.sh >> /var/log/health-check.log 2>&1
```

---

## Troubleshooting

### Issue: 502 Bad Gateway

**Check:**
```bash
# Is Gunicorn running?
sudo systemctl status health-chatbot

# Check socket file exists
ls -la /var/www/health-chatbot/gunicorn.sock

# Check logs
sudo journalctl -u health-chatbot -n 50
```

**Fix:**
```bash
sudo systemctl restart health-chatbot
```

### Issue: Static files not loading

**Fix:**
```bash
cd /var/www/health-chatbot
source venv/bin/activate
python3 manage.py collectstatic --noinput
sudo systemctl restart nginx
```

### Issue: Database connection error

**Check:**
```bash
# Test RDS connection
psql -h ft-internal-new.cxok8ouastuu.eu-north-1.rds.amazonaws.com \
     -U postgres -d postgres

# Check .env file
cat /var/www/health-chatbot/.env

# Verify security group allows EC2 → RDS connection
```

### Issue: SSL certificate issues

**Fix:**
```bash
# Check certificate status
sudo certbot certificates

# Force renewal
sudo certbot renew --force-renewal

# Check Nginx config
sudo nginx -t
```

---

## Security Best Practices

1. **Keep system updated:**
   ```bash
   sudo apt update && sudo apt upgrade -y
   ```

2. **Regular backups:**
   ```bash
   # Backup database weekly
   python3 manage.py dumpdata > backup.json
   ```

3. **Monitor logs:**
   ```bash
   # Check for errors daily
   sudo journalctl -u health-chatbot --since "1 day ago" | grep -i error
   ```

4. **Rotate secrets:**
   - Change SECRET_KEY periodically
   - Update RDS password regularly

5. **Firewall rules:**
   - Only allow necessary ports
   - Restrict SSH to your IP

---

## Performance Optimization

### Increase Gunicorn Workers

Edit `/etc/systemd/system/health-chatbot.service`:

```ini
# Change --workers based on CPU cores
# Formula: (2 x CPU cores) + 1
--workers 5  # For 2 CPU cores
```

### Enable Nginx Caching

Add to Nginx config:
```nginx
location /static/ {
    alias /var/www/health-chatbot/staticfiles/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

### Database Connection Pooling

Add to `settings.py`:
```python
DATABASES['default']['CONN_MAX_AGE'] = 600
```

---

## Success Checklist

- [x] DNS points to EC2 IP
- [x] Django settings updated for production
- [x] SSL certificate installed
- [x] Gunicorn service running
- [x] Nginx configured and running
- [x] Firewall configured
- [x] API accessible at https://gpt.shoryakumar.in
- [x] Auto-renewal set up for SSL

---

## Next Steps

1. **Add monitoring:**
   - Set up CloudWatch alarms
   - Configure uptime monitoring (UptimeRobot, Pingdom)

2. **Implement rate limiting:**
   - Use Django rate limiting middleware
   - Configure Nginx rate limiting

3. **Add authentication:**
   - JWT tokens
   - API keys

4. **Set up CI/CD:**
   - GitHub Actions for automated deployment
   - Automated testing

---

## Support

If you encounter issues:

1. Check logs: `sudo journalctl -u health-chatbot -f`
2. Verify services: `sudo systemctl status health-chatbot nginx`
3. Test connectivity: `curl https://gpt.shoryakumar.in/api/health/`

Your application is now live at: **https://gpt.shoryakumar.in**
