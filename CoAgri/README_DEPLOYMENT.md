# CoAgri Django Deployment Guide

## Prerequisites
- Ubuntu VPS with sudo access
- Domain name (optional but recommended)
- Git repository with your code

## Quick Deployment

1. **Clone and run deployment script:**
```bash
git clone https://github.com/yourusername/CoAgri.git
cd CoAgri/CoAgri/CoAgri
chmod +x deploy.sh
./deploy.sh
```

2. **Configure environment variables:**
```bash
cd /var/www/coagri/CoAgri/CoAgri
sudo nano .env
```

Update with your settings:
```
SECRET_KEY=your-new-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com,your-server-ip
```

3. **Generate new SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

4. **PostgreSQL is automatically configured during deployment**

The deployment script automatically:
- Installs PostgreSQL
- Creates database and user with secure password
- Updates .env file with database credentials

To manually setup PostgreSQL:
```bash
chmod +x setup_postgresql.sh
./setup_postgresql.sh
```

5. **Configure Nginx:**
```bash
sudo cp nginx.conf /etc/nginx/sites-available/coagri
sudo ln -s /etc/nginx/sites-available/coagri /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

6. **Setup Supervisor:**
```bash
sudo cp supervisor.conf /etc/supervisor/conf.d/coagri.conf
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start coagri
```

7. **Final Django setup:**
```bash
cd /var/www/coagri/CoAgri/CoAgri
source /var/www/coagri/venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

## SSL Certificate (Optional)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## Useful Commands

- **Restart application:** `sudo supervisorctl restart coagri`
- **View logs:** `sudo tail -f /var/log/supervisor/coagri.log`
- **Database backup:** `./backup_db.sh`
- **Database restore:** `./restore_db.sh /path/to/backup.sql.gz`
- **Connect to database:** `psql -h localhost -U coagri_user -d coagri_db`
- **Update code:** 
  ```bash
  cd /var/www/coagri
  git pull origin main
  cd CoAgri/CoAgri
  source /var/www/coagri/venv/bin/activate
  pip install -r requirements.txt
  python manage.py migrate
  python manage.py collectstatic --noinput
  sudo supervisorctl restart coagri
  ```

## Security Checklist

- [ ] Changed SECRET_KEY
- [ ] Set DEBUG=False
- [ ] Configured proper ALLOWED_HOSTS
- [ ] PostgreSQL configured with secure password
- [ ] Configured SSL certificate
- [ ] Setup firewall (ufw)
- [ ] Regular backups configured (cron job for backup_db.sh)
- [ ] Database user has minimal required privileges

## Troubleshooting

- **502 Bad Gateway:** Check Gunicorn logs and ensure it's running
- **Static files not loading:** Run `collectstatic` and check Nginx config
- **Database connection errors:** 
  - Check PostgreSQL is running: `sudo systemctl status postgresql`
  - Verify credentials in .env file
  - Test connection: `psql -h localhost -U coagri_user -d coagri_db`
- **Permission errors:** Check file ownership (`chown www-data:www-data`)
- **Migration errors:** Ensure database user has proper privileges