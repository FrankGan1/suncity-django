# Suncity Django — Internet and IP Services Enterprise

A simple Django site with:

- **Public pages** — Home (hero: *Internet and IP Services Enterprise* with
  **Get Started** / **Sign In** buttons), Services (one service, kept
  simple), Contact Us.
- **Auth pages** — Sign Up, Sign In, Forgot Password / Reset Password,
  styled to match the reference screenshots (green brand, gradient
  auth background, card layout).
- **Client accounts** — anyone who signs up becomes a *Client*
  (`accounts.Client`, linked to Django's built-in `User`).
- **Admin dashboard** (`/dashboard/`, staff-only) — Client Management:
  list/search clients, **Add Client**, **Delete Client**,
  **Send Reset Password** (emails a secure reset link).
- **Database:** MySQL (not MongoDB).

---

## 1. Project layout

```
suncity_django/
├── manage.py
├── passenger_wsgi.py        # entry point for CyberPanel (OpenLiteSpeed) deployment
├── requirements.txt
├── .env.example              # copy to .env and fill in
├── suncity_django/           # project settings/urls/wsgi/asgi
├── core/                     # Home / Services / Contact
├── accounts/                 # Sign up / Sign in / Forgot & reset password / Client model
├── dashboard/                 # Staff-only client management
├── templates/base.html        # shared header/nav/footer
└── static/css/style.css       # site styling
```

---

## 2. Local setup (development machine)

### 2.1 Prerequisites

- Python 3.11+ (3.12 is fine)
- MySQL Server 8.x running locally (or MariaDB 10.6+)
- `pip`, and ideally a virtual environment tool (`venv`)

On Ubuntu/Debian, the MySQL client dev headers are needed to build
`mysqlclient`:

```bash
sudo apt update
sudo apt install -y python3-venv python3-dev default-libmysqlclient-dev build-essential pkg-config
```

On macOS (Homebrew):

```bash
brew install mysql pkg-config
```

### 2.2 Create the MySQL database

```bash
mysql -u root -p
```

```sql
CREATE DATABASE suncity_django CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'suncity_user'@'localhost' IDENTIFIED BY 'change-me';
GRANT ALL PRIVILEGES ON suncity_django.* TO 'suncity_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 2.3 Python environment

```bash
cd suncity_django
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2.4 Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` and set at minimum:

```
DJANGO_SECRET_KEY=<generate a long random string>
DB_NAME=suncity_django
DB_USER=suncity_user
DB_PASSWORD=change-me
DB_HOST=127.0.0.1
DB_PORT=3306
```

Leave `DJANGO_EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend`
for local dev — password-reset emails will simply print to your terminal
(and the "Forgot Password" and admin "Send Reset Password" pages will also
show the link directly on screen as a dev convenience).

### 2.5 Migrate & create your admin account

```bash
python manage.py migrate
python manage.py createsuperuser
```

> When prompted, it's fine to use any username, but **use the same value
> for username and email** (or just remember the email) — you sign in to
> `/accounts/login/` using your **email address**, which works for both
> staff/admin and clients thanks to the built-in email login backend.

### 2.6 Run it

```bash
python manage.py runserver
```

Visit:

- **http://127.0.0.1:8000/** — public site
- **http://127.0.0.1:8000/accounts/login/** — sign in (admins land on
  `/dashboard/`, clients land on `/accounts/my-account/`)
- **http://127.0.0.1:8000/accounts/register/** — client sign up
- **http://127.0.0.1:8000/dashboard/** — admin client management
  (staff only)
- **http://127.0.0.1:8000/django-admin/** — Django's built-in admin
  (superusers)

---

## 3. Deploying to CyberPanel (Ubuntu)

CyberPanel (OpenLiteSpeed) has a built-in **"Python App"** feature that
runs Django via Passenger — this is the easiest path and is what
`passenger_wsgi.py` in this project is for.

### 3.1 Create the website & database in CyberPanel

1. **Websites → Create Website** — create your domain (e.g.
   `suncity.example.com`).
2. **Databases → Create Database** — create a MySQL database and user
   (note the DB name, username, password, host — usually `localhost`).

### 3.2 Upload the project

Upload the whole `suncity_django/` folder to your site, e.g. via SFTP into:

```
/home/suncity.example.com/public_html/
```

(You can also `git clone` it there if you push this project to a repo.)

### 3.3 Create the Python App

1. **Websites → your site → Manage → Python App** (or **App Manager →
   Python App** depending on CyberPanel version).
2. **Create Python App**, choose:
   - **Application Path** → the folder where you uploaded the project
     (containing `manage.py` and `passenger_wsgi.py`)
   - **Python Version** → 3.11 or 3.12
   - **Application startup file** → `passenger_wsgi.py`
   - **Application Entry point** → `application`
3. CyberPanel creates a dedicated virtualenv for the app — note the path
   it gives you (something like
   `/home/suncity.example.com/public_html/venv`).

### 3.4 Install dependencies into that virtualenv

SSH into the server:

```bash
sudo apt update
sudo apt install -y python3-dev default-libmysqlclient-dev build-essential pkg-config

source /home/suncity.example.com/public_html/venv/bin/activate
cd /home/suncity.example.com/public_html
pip install -r requirements.txt
```

### 3.5 Configure `.env` for production

```bash
cp .env.example .env
nano .env
```

Set:

```
DJANGO_SECRET_KEY=<long random string>
DJANGO_DEBUG=False
DJANGO_ALLOWED_HOSTS=suncity.example.com,www.suncity.example.com
DJANGO_CSRF_TRUSTED_ORIGINS=https://suncity.example.com,https://www.suncity.example.com

DB_NAME=<db name from CyberPanel>
DB_USER=<db user from CyberPanel>
DB_PASSWORD=<db password from CyberPanel>
DB_HOST=localhost
DB_PORT=3306

# Real email delivery for password-reset links:
DJANGO_EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
SMTP_HOST=<your SMTP host, e.g. smtp.gmail.com or CyberPanel's mail server>
SMTP_PORT=587
SMTP_USER=<smtp username>
SMTP_PASSWORD=<smtp password>
SMTP_USE_TLS=True
DEFAULT_FROM_EMAIL=no-reply@suncity.example.com

DJANGO_SECURE_SSL_REDIRECT=True
DJANGO_SESSION_COOKIE_SECURE=True
DJANGO_CSRF_COOKIE_SECURE=True
```

> CyberPanel can also create a mailbox for your domain
> (**Email → Create Email**) that you can use as the SMTP account above.

### 3.6 Migrate, collect static files, create the admin account

Still inside the activated virtualenv:

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### 3.7 Serve static files & restart

- In the CyberPanel Python App settings, add a **static file mapping**
  (or "External App" static mapping) from URL `/static/` to the
  `staticfiles/` folder inside your app (this project already uses
  WhiteNoise as a fallback, so static files will still work even
  without an explicit mapping — the mapping is just faster).
- Click **Restart Application** in the Python App panel (or run
  `touch tmp/restart.txt` if your CyberPanel version uses that
  convention — check the panel's own restart button first).

### 3.8 Enable HTTPS

**SSL → Manage SSL** in CyberPanel → issue a free Let's Encrypt
certificate for your domain, then make sure `DJANGO_SECURE_SSL_REDIRECT`
stays `True` in `.env`.

### 3.9 Verify

Visit `https://suncity.example.com/` and confirm:

- Home page loads with the hero and **Get Started** / **Sign In** buttons.
- `/accounts/register/` lets a client sign up.
- `/accounts/login/` lets both clients and your superuser sign in.
- `/dashboard/` (as your admin) shows Client Management with **Add
  Client**, **Delete**, and **Send Reset Password** working — and that
  reset emails are actually delivered (since email backend is now SMTP,
  not console).

---

## 4. Alternative: Gunicorn + systemd (if you'd rather not use CyberPanel's Python App)

If you prefer running Gunicorn behind OpenLiteSpeed/Nginx as a reverse
proxy instead of Passenger, use `suncity_django/wsgi.py` (not
`passenger_wsgi.py`):

```bash
source venv/bin/activate
gunicorn suncity_django.wsgi:application --bind 127.0.0.1:8001 --workers 3
```

Then set up a systemd service and a proxy rule pointing your domain to
`127.0.0.1:8001`. This is optional — the CyberPanel Python App method
above is simpler and doesn't require managing systemd yourself.

---

## 5. Notes

- **No MongoDB anywhere** — this project uses MySQL exclusively
  (`django.db.backends.mysql`), per the request.
- Password reset links use Django's built-in secure token generator
  (`default_token_generator`) — links expire automatically and are
  single-use.
- The **admin dashboard** (`/dashboard/`) is separate from Django's
  built-in `/django-admin/` — it's a simplified, purpose-built client
  management screen, while `/django-admin/` remains available for
  full data admin access.
- To make an existing user a dashboard admin, set `is_staff = True` on
  their `User` record (via `/django-admin/` or `python manage.py shell`).
