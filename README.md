# Vancouver Minor Baseball – Main Site (https://vancouverminor.com)

This repository contains the primary public-facing site for Vancouver Minor Baseball. It highlights the club’s philosophy, programs, and achievements, and lives alongside other apps that occupy their own subdomains (for example `dev.vancouverminor.com`).

The project now also includes:

- `drafts`: staff-facing draft operations
- `pdp`: a reusable Player Development Platform for evaluations, goals, snapshots, roadmaps, report cards, drills, and future AI integrations

Detailed PDP documentation is in [docs/pdp.md](/Users/eugenelin/dev/vmba0/docs/pdp.md).

The stack is intentionally lightweight:

- **Django** powers templating and routing.
- **Plain HTML/CSS** (no frontend build tooling) keeps the site easy to maintain.
- **Static assets** (images, CSS) live under `static/`.

Because the project is simple, most customization happens through data dictionaries and templates rather than a database.

---

## Project Layout

```
├── README.md                     # You are here
├── home/
│   ├── content.py                # Centralized static content + navigation config
│   ├── urls.py                   # Route definitions, including generated placeholder pages
│   └── views.py                  # Class-based views that feed templates their content
├── scripts/
│   └── generate_placeholders.py  # Utility to generate placeholder images (requires Pillow)
├── static/
│   ├── css/styles.css            # Global styling (baby-blue theme, layout, components)
│   └── images/                   # Hero images, logos, highlight artwork
└── templates/
    ├── base.html                 # Shared HTML skeleton and stylesheet include
    └── home/
        ├── includes/
        │   ├── site_header.html  # Header + navigation
        │   ├── nav.html          # Recursive menu renderer
        │   └── nav_script.html   # Shared navigation behavior script
        ├── index.html            # Home page
        ├── programs.html         # Programs page
        ├── registration.html     # Registration page
        └── page.html             # Placeholder page used for unimplemented routes
```

### How Content Is Managed

- **`home/content.py`** is the single source of truth for navigation items, hero messaging, and card content. Updating the site typically means editing this file rather than the templates.
  - `NAVIGATION` drives the header menu.
  - `HERO`, `PROGRAMS_PAGE`, and `REGISTRATION_PAGE` feed the hero sections and content cards.
  - `ACHIEVEMENTS` supplies the highlight cards on the home page.
- **Templates** read those dictionaries and render markup. Minimal presentation logic lives inside the templates to keep them declarative.
- **CSS** in `static/css/styles.css` controls theme colors, layout, and responsive behavior. It’s safe to extend existing utility classes or add section-specific styles as needed.
- **Placeholder pages**: unknown slugs picked up by navigation automatically render via `templates/home/page.html`, which keeps the navigation functional until bespoke pages are added.
- **Images**: hero assets follow a naming convention (`vmb_hero-banner.jpg`, `programs-hero.jpg`, `registration-hero.jpg`). Update the files under `static/images/` and ensure filenames match what `home/content.py` expects.

---

## Local Development Basics

1. Create and activate a virtual environment (Python 3.10+ recommended).
2. Install dependencies (if you add a `requirements.txt`, install from there).
3. Set a local Django secret key in your shell. Use a development-only value locally, and never commit real secrets:
   ```bash
   export DJANGO_SECRET_KEY="replace-with-a-secure-random-value"
   ```
   You can generate a secure value locally with:
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
   If you use a local `.env` file for your shell tooling, keep it untracked. `.env.example` shows the required variable name without containing a real secret.
4. Run migrations if/when models are introduced.
5. Start the dev server:
   ```bash
   python manage.py runserver
   ```
6. Optional – regenerate placeholder imagery:
   ```bash
   pip install Pillow
   python scripts/generate_placeholders.py
   ```

Because the site is mostly static, productivity comes from editing `content.py` and refreshing the browser.

---

## Project Snapshot Policy

Do not regenerate or update `project_flat_file.txt` during normal work. Treat it as an on-request artifact only.

Prompt archive records should store the user prompt and commit diffs, not full repository snapshots. If a full-project snapshot is explicitly requested, exclude dependency, generated, and cache directories such as `.git`, `.venv`, `__pycache__`, `node_modules`, `dist`, and `build`. Binary files should be represented by metadata and a short description rather than embedding their full contents.

---

## Production Deployment on DigitalOcean (Ubuntu 20.04+)

The following steps assume you already operate other subdomains (e.g. `dev.vancouverminor.com`) on the same Droplet and that this application should serve the apex domain at `https://vancouverminor.com`. Adjust paths and names to suit your environment.

### 1. Prepare the Server

SSH into the Droplet:

```bash
ssh user@your-droplet-ip
```

Update packages:

```bash
sudo apt update && sudo apt upgrade
```

Install required system packages:

```bash
sudo apt install python3-pip python3-venv python3-dev build-essential \
                 nginx git ufw
```

### 2. Clone the Repository

Decide on a base path for web apps, e.g. `/var/www/vancouverminor`.

```bash
sudo mkdir -p /var/www/vancouverminor
sudo chown $USER:$USER /var/www/vancouverminor
cd /var/www/vancouverminor
git clone <your-repo-url> website
```

### 3. Set Up the Virtual Environment

```bash
cd website
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt   # create this file if it doesn't already exist
```

Collect static files (configure `STATIC_ROOT` in `settings.py` first):

```bash
python manage.py collectstatic
```

Run database migrations when applicable:

```bash
python manage.py migrate
```

Create an admin user if needed:

```bash
python manage.py createsuperuser
```

### 4. Configure Gunicorn

Install Gunicorn inside the virtual environment:

```bash
pip install gunicorn
```

Test that Gunicorn can serve the project:

```bash
gunicorn --bind 0.0.0.0:8000 vancouverminor.wsgi
```

If successful, stop the test with `Ctrl+C`.

Create a systemd service file, e.g. `/etc/systemd/system/vancouverminor.service`:

```ini
[Unit]
Description=Gunicorn instance for vancouverminor.com
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/vancouverminor/website
Environment="PATH=/var/www/vancouverminor/website/venv/bin"
Environment="DJANGO_SECRET_KEY=replace-with-a-secure-random-value"
ExecStart=/var/www/vancouverminor/website/venv/bin/gunicorn \
          --workers 3 \
          --bind unix:/var/www/vancouverminor/website/vancouverminor.sock \
          vancouverminor.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
```

Reload systemd and enable the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now vancouverminor
sudo systemctl status vancouverminor
```

Use a real secure random value for `DJANGO_SECRET_KEY` in production. The previously committed development key must be treated as exposed and rotated in any deployed environment that used it. Do not commit production secrets to Git.

### 5. Configure Nginx

Create a new server block `/etc/nginx/sites-available/vancouverminor.com`:

```nginx
server {
    listen 80;
    server_name vancouverminor.com www.vancouverminor.com;

    location = /favicon.ico { access_log off; log_not_found off; }

    location /static/ {
        alias /var/www/vancouverminor/website/static/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/vancouverminor/website/vancouverminor.sock;
    }
}
```

Enable the site and test:

```bash
sudo ln -s /etc/nginx/sites-available/vancouverminor.com /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```


### 6. Obtain HTTPS with Let’s Encrypt

Ensure the `snapd` version of Certbot is installed:

```bash
sudo snap install core
sudo snap refresh core
sudo snap install --classic certbot
sudo ln -s /snap/bin/certbot /usr/bin/certbot
```

Run Certbot using the Nginx plugin (this will edit the server block to listen on 443 and configure redirects):

```bash
sudo certbot --nginx -d vancouverminor.com -d www.vancouverminor.com
```

Follow the prompts. Certbot will create the necessary certificates and update the Nginx config.

Automatic renewal runs via systemd. Test renewal:

```bash
sudo certbot renew --dry-run
```

### 7. Integrate with Existing Subdomains

Because the apex domain shares infrastructure with other subdomains:

- Each app should have its own systemd service, socket, static root, and Nginx server block.
- Ensure DNS has `A` / `CNAME` records for both `vancouverminor.com` and `www.vancouverminor.com` pointing to the Droplet’s IP. Keep existing records for subdomains like `dev.vancouverminor.com`.
- To avoid certificate rate limits, only request certificates for subdomains that will serve traffic.
- Keep firewall rules permissive for HTTP/HTTPS (e.g. `sudo ufw allow 'Nginx Full'`).

### 8. Ongoing Maintenance

- **Deploy updates**: pull latest changes, reinstall dependencies if needed, re-run `collectstatic`, then restart Gunicorn:
  ```bash
  cd /var/www/vancouverminor/website
  source venv/bin/activate
  git pull origin main
  pip install -r requirements.txt
  python manage.py collectstatic
  sudo systemctl restart home-site
  ```
- **Monitor logs**:
  ```bash
  sudo journalctl -u home-site -f
  sudo tail -f /var/log/nginx/home.vancouverminor.com.error.log
  ```
- **Rotate assets**: update hero images under `static/images/` and re-run `collectstatic`.

---

## Contributing Guidelines

1. Work from feature branches, keep PRs focused.
2. Update `home/content.py` for text/navigation changes; reflect any structural modifications in templates.
3. Run through the site on mobile and desktop whenever you touch CSS.
4. Document any new deployment steps in this README so future developers stay aligned.

## Prompt Registry

Reusable project prompts live in `prompts/`.

- Store each prompt as a Markdown file.
- Name prompt files with the format `[new app name]_prompt_[id].md`.
- Use lowercase app names and underscores when the app name has multiple words.
- Start prompt IDs at `0` and increment by `1` for each new prompt.
- Use the next unused integer ID when creating a new prompt.

Example: `analytics_prompt_0.md`

Current analytics prompt session:

```bash
codex resume 019f15b0-39b4-75a2-97ff-26808c125814
```

With this structure and deployment workflow, future developers can confidently maintain the `home.vancouverminor.com` subdomain alongside the organization’s other applications. 
