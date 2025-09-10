# Deployment Guide for Duplicate Log Finder Application

## Preparing for Deployment

### 1. Repository Preparation

Before deployment, ensure all changes are committed:

```bash
# Check repository status
git status

# Add all changes
git add .

# Create commit
git commit -m "Preparing for server deployment"

# Push changes to remote repository
git push origin master
```

### 2. Project Structure for Deployment

The project already has the correct structure:
- `api.py` - main file for running REST API
- `controller.py` - for running CLI version
- `model.py` - business logic
- `view.py` - result display
- `requirements.txt` - dependencies
- `res/` - sample data

### 3. Dependencies

Ensure requirements.txt contains only necessary dependencies:
```
fastapi
uvicorn[standard]
python-multipart
```

## Server Deployment

### Option 1: Deploy as systemd service (Linux)

1. Copy project to server:
```bash
scp -r . user@server:/path/to/deployment/
```

2. Create virtual environment and install dependencies:
```bash
cd /path/to/deployment/
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. Create systemd unit file `/etc/systemd/system/duplicate-finder.service`:
```ini
[Unit]
Description=Duplicate Log Finder API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/deployment
ExecStart=/path/to/deployment/venv/bin/python api.py
Environment=PATH=/path/to/deployment/venv/bin
Restart=always

[Install]
WantedBy=multi-user.target
```

4. Start the service:
```bash
sudo systemctl daemon-reload
sudo systemctl start duplicate-finder
sudo systemctl enable duplicate-finder
```

### Option 2: Using Uvicorn (recommended for production)

1. Install dependencies (already installed via requirements.txt):
```bash
pip install fastapi uvicorn[standard]
```

2. Run application through Uvicorn:
```bash
uvicorn api:app --host 0.0.0.0 --port 5000
```

3. To run as service, create systemd unit file:
```ini
[Unit]
Description=Duplicate Log Finder API
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/path/to/deployment
ExecStart=/path/to/deployment/venv/bin/uvicorn api:app --host 0.0.0.0 --port 5000
Environment=PATH=/path/to/deployment/venv/bin
Restart=always

[Install]
WantedBy=multi-user.target
```

## Reverse Proxy Setup (nginx)

For production, it's recommended to use nginx as reverse proxy:

1. Install nginx:
```bash
sudo apt install nginx
```

2. Create configuration file `/etc/nginx/sites-available/duplicate-finder`:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

3. Activate site:
```bash
sudo ln -s /etc/nginx/sites-available/duplicate-finder /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

## Monitoring and Logging

1. Check service status:
```bash
systemctl status duplicate-finder
```

2. View logs:
```bash
journalctl -u duplicate-finder -f
```

3. Application logs are located in `/var/log/duplicate-finder/`

## Application Updates

1. Stop service:
```bash
sudo systemctl stop duplicate-finder
```

2. Update code:
```bash
cd /path/to/deployment
git pull origin master
```

3. Update dependencies if needed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

4. Restart service:
```bash
sudo systemctl start duplicate-finder
```

## Security

1. Use HTTPS (Let's Encrypt):
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

2. Restrict API access if needed through nginx:
```nginx
location / {
    allow 192.168.1.0/24;
    deny all;
    proxy_pass http://127.0.0.1:5000;
    # ... other settings
}
```

## Backup

Regularly create backups:
```bash
tar -czf backup-$(date +%Y%m%d).tar.gz /path/to/deployment/
```