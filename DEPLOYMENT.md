# SinMancha Deployment Guide

## ✅ Pre-Deployment Checklist

- [ ] All environment variables configured in production `.env`
- [ ] SECRET_KEY generated and stored in `.env`
- [ ] DEBUG = False in production
- [ ] ALLOWED_HOSTS set to your domain(s)
- [ ] PostgreSQL database created and credentials in `.env`
- [ ] Stripe live API keys obtained
- [ ] Webhook endpoint configured in Stripe Dashboard
- [ ] SSL/TLS certificate obtained (Let's Encrypt recommended)
- [ ] All migrations applied (`python manage.py migrate`)
- [ ] Static files collected (`python manage.py collectstatic`)
- [ ] Superuser created for admin access

## 🚀 Deployment Methods

### 1. Heroku (Easiest for Small Projects)

#### Setup
```bash
# Install Heroku CLI
# Visit: https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create sinmancha-app

# Add PostgreSQL add-on
heroku addons:create heroku-postgresql:standard-0
```

#### Configure Environment Variables
```bash
heroku config:set SECRET_KEY="$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')"
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=sinmancha-app.herokuapp.com
heroku config:set STRIPE_SECRET_KEY=sk_live_YOUR_KEY
heroku config:set STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_KEY
heroku config:set STRIPE_WEBHOOK_SECRET=whsec_live_YOUR_SECRET
```

#### Deploy
```bash
# Add Heroku remote if not already done
heroku git:remote -a sinmancha-app

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser

# Collect static files (auto on Heroku, but can force)
heroku run python manage.py collectstatic --noinput
```

#### Verify
```bash
heroku open
heroku logs --tail
```

#### Add Stripe Webhook
1. Go to [Stripe Dashboard](https://dashboard.stripe.com/webhooks)
2. Add endpoint: `https://sinmancha-app.herokuapp.com/payments/webhook/`
3. Select events:
   - `payment_intent.succeeded`
   - `payment_intent.payment_failed`
   - `charge.refunded`
4. Copy signing secret and run:
   ```bash
   heroku config:set STRIPE_WEBHOOK_SECRET=whsec_live_YOUR_SECRET
   ```

---

### 2. PythonAnywhere (Simple & Beginner-Friendly)

#### Setup Account
1. Visit https://www.pythonanywhere.com
2. Create free account
3. Go to Web tab → Add a new web app

#### Clone Repository
```bash
# In bash console
cd /home/your_username
git clone https://github.com/your-username/sinmancha.git
cd sinmancha
```

#### Create Virtual Environment
```bash
mkvirtualenv --python=/usr/bin/python3.10 sinmancha
pip install -r requirements.txt
```

#### Configure Django
1. Go to Web tab → Edit WSGI configuration
2. Update path to point to `sinmancha/wsgi.py`
3. Set environment variables in WSGI file:
   ```python
   import os
   os.environ['SECRET_KEY'] = 'your-secret-key'
   os.environ['DEBUG'] = 'False'
   os.environ['STRIPE_SECRET_KEY'] = 'sk_live_...'
   ```

#### Create Database
```bash
python manage.py migrate
python manage.py createsuperuser
```

#### Reload
Visit Web tab → Reload button

#### Add Webhook URL
In Stripe Dashboard: `https://your-username.pythonanywhere.com/payments/webhook/`

---

### 3. AWS EC2 (Full Control & Scalability)

#### Launch EC2 Instance
```bash
# Use Ubuntu 22.04 LTS
# Security Group: Allow ports 80, 443, 22
```

#### Connect & Setup
```bash
ssh -i your-key.pem ubuntu@your-instance-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3.10 python3.10-venv postgresql postgresql-contrib nginx
```

#### Clone & Setup App
```bash
cd /home/ubuntu
git clone https://github.com/your-username/sinmancha.git
cd sinmancha

python3.10 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

#### Create `.env`
```bash
cp .env.example .env
nano .env  # Edit with your secrets
```

#### Configure PostgreSQL
```bash
sudo -u postgres psql

CREATE DATABASE sinmancha;
CREATE USER sinmancha_user WITH PASSWORD 'secure_password';
ALTER ROLE sinmancha_user SET client_encoding TO 'utf8';
ALTER ROLE sinmancha_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE sinmancha_user SET default_transaction_deferrable TO on;
ALTER ROLE sinmancha_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE sinmancha TO sinmancha_user;
\q
```

#### Configure Django
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

#### Setup Gunicorn
Create `/home/ubuntu/sinmancha/gunicorn.service`:
```ini
[Unit]
Description=Gunicorn application server for sinmancha
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/sinmancha
ExecStart=/home/ubuntu/sinmancha/venv/bin/gunicorn \
    --workers 3 \
    --bind unix:/home/ubuntu/sinmancha/gunicorn.sock \
    sinmancha.wsgi:application

[Install]
WantedBy=multi-user.target
```

```bash
sudo cp gunicorn.service /etc/systemd/system/
sudo systemctl start gunicorn
sudo systemctl enable gunicorn
```

#### Configure Nginx
Create `/etc/nginx/sites-available/sinmancha`:
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    location /static/ {
        alias /home/ubuntu/sinmancha/staticfiles/;
    }
    location / {
        include proxy_params;
        proxy_pass http://unix:/home/ubuntu/sinmancha/gunicorn.sock;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/sinmancha /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### Enable SSL with Let's Encrypt
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

#### Add Webhook
In Stripe Dashboard: `https://your-domain.com/payments/webhook/`

---

### 4. Docker + Docker Compose

#### Create `Dockerfile`
```dockerfile
FROM python:3.10

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "sinmancha.wsgi:application"]
```

#### Create `docker-compose.yml`
```yaml
version: '3'
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: sinmancha
      POSTGRES_USER: sinmancha_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    build: .
    command: sh -c "python manage.py migrate && gunicorn --bind 0.0.0.0:8000 sinmancha.wsgi"
    ports:
      - "8000:8000"
    environment:
      - SECRET_KEY=your-secret-key
      - DEBUG=False
      - DATABASE_URL=postgresql://sinmancha_user:secure_password@db:5432/sinmancha
      - STRIPE_SECRET_KEY=sk_live_...
      - STRIPE_PUBLISHABLE_KEY=pk_live_...
    depends_on:
      - db

volumes:
  postgres_data:
```

#### Deploy
```bash
docker-compose build
docker-compose up -d
docker-compose exec web python manage.py createsuperuser
```

---

## 🔧 Post-Deployment Tasks

### Verify Installation
```bash
# Test homepage loads
curl https://your-domain.com

# Check admin access
# Visit https://your-domain.com/admin and login

# Test Stripe integration
# Purchase a membership with test card 4242 4242 4242 4242
```

### Monitor Logs
```bash
# Heroku
heroku logs --tail

# AWS EC2
sudo journalctl -u gunicorn -f

# Docker
docker-compose logs -f web
```

### Enable Email (Optional)
Add to `.env`:
```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

Then in `settings.py`:
```python
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = os.environ.get('EMAIL_HOST')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
```

### Setup Automated Backups
```bash
# Heroku
heroku pg:backups:schedule --at "02:00 UTC" DATABASE

# AWS RDS (if using RDS instead of EC2 PostgreSQL)
# Configure via AWS Console → RDS → Backups
```

### Monitor Performance
- **Heroku:** Use `heroku metrics`
- **AWS:** Use CloudWatch
- **PythonAnywhere:** Built-in monitoring

---

## 🚨 Troubleshooting

### Static Files Not Serving
```bash
python manage.py collectstatic --noinput --clear
# For Heroku:
heroku run python manage.py collectstatic --noinput
```

### Database Migration Errors
```bash
python manage.py showmigrations
python manage.py migrate --fake payments 0001
python manage.py migrate
```

### Stripe Webhook Not Firing
1. Verify endpoint URL in Stripe Dashboard
2. Check webhook secret in `.env`
3. Test webhook: `heroku logs --tail` → simulate payment
4. Ensure `STRIPE_WEBHOOK_SECRET` is set

### 500 Errors
```bash
# Check logs
heroku logs --tail

# SSH into server
heroku run bash

# Check Django errors
python manage.py shell
# Import models and test
```

### SSL Certificate Issues
```bash
# Renew Let's Encrypt certificate
sudo certbot renew --dry-run
sudo certbot renew
```

---

## 📊 Monitoring & Maintenance

### Weekly Tasks
- [ ] Check logs for errors
- [ ] Monitor Stripe payment status
- [ ] Review user feedback

### Monthly Tasks
- [ ] Update dependencies: `pip list --outdated`
- [ ] Review database backups
- [ ] Check server health metrics

### Quarterly Tasks
- [ ] Security audit
- [ ] Performance optimization
- [ ] Update documentation

---

## 🔐 Security Checklist

- [ ] SECRET_KEY is unique and strong
- [ ] DEBUG = False in production
- [ ] ALLOWED_HOSTS configured
- [ ] SSL/TLS enabled
- [ ] STRIPE_WEBHOOK_SECRET configured
- [ ] Database credentials secure
- [ ] No secrets in git history
- [ ] Regular backups enabled
- [ ] Logs monitored for suspicious activity
- [ ] Django admin password strong

---

**Last Updated:** February 2026
**Version:** 1.0.0
