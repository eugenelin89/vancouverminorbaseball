# Updating Production

> Historical helper.
> This file preserves an earlier deployment checklist. The authoritative deployment process is [RUNBOOK.md](RUNBOOK.md). Use the runbook for current production deployments and treat this file as historical context only.

## 1. Become the deployment user

```bash
cd /var/www/vancouverminorbaseball
sudo -u django-user -H bash
```

---

## 2. Go to the project

```bash
cd /var/www/vancouverminorbaseball
source venv/bin/activate
```

---

## 3. Update the code

```bash
git fetch origin
git pull --ff-only origin main
```

---

## 4. Install/update Python packages

```bash
pip install -r requirements.txt
```

---

## 5. (Optional but Recommended) Backup before migrations

```bash
mkdir -p ~/deployment-backup

cp db.sqlite3 ~/deployment-backup/db.sqlite3.$(date +%Y%m%d-%H%M%S)

git rev-parse HEAD > ~/deployment-backup/current_commit.txt
```

---

## 6. Run database migrations

```bash
sudo bash -c '
set -a
. /etc/vancouverminorbaseball.env
set +a
cd /var/www/vancouverminorbaseball

runuser -u django-user -- venv/bin/python manage.py migrate
'
```

---

## 7. Collect static files

```bash
sudo bash -c '
set -a
. /etc/vancouverminorbaseball.env
set +a
cd /var/www/vancouverminorbaseball

runuser -u django-user -- venv/bin/python manage.py collectstatic --noinput
'
```

---

## 8. Verify Django

```bash
sudo bash -c '
set -a
. /etc/vancouverminorbaseball.env
set +a
cd /var/www/vancouverminorbaseball

runuser -u django-user -- venv/bin/python manage.py check
'
```

---

## 9. Exit the virtual environment

```bash
deactivate
exit
```

---

## 10. Restart Gunicorn

```bash
sudo systemctl restart vancouverminor.service
```

---

## 11. Verify deployment

```bash
sudo systemctl status vancouverminor.service --no-pager
```

```bash
curl -I https://vancouverminor.com/
curl -I https://vancouverminor.com/accounts/login/
curl -I https://vancouverminor.com/analytics/
```

Expected:

- `/` → 200
- `/accounts/login/` → 200
- `/analytics/` → 302 (redirect to login)

---

## Notes

Do **NOT** run these directly anymore:

```bash
python manage.py migrate
python manage.py collectstatic
```

They will fail because the production environment variables are stored in:

```
/etc/vancouverminorbaseball.env
```

Always use the wrapped commands shown above.
