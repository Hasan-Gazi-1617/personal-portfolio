# Hasan | Personal Portfolio

A Django-powered personal portfolio showcasing my work across **Network Engineering, ISP Infrastructure, NOC Operations, and Software Development**.

<p align="left">
  <a href="https://personal-portfolio-069p.onrender.com/"><strong>Visit Live Portfolio</strong></a>
  ·
  <a href="https://github.com/Hasan-Gazi-1617">GitHub Profile</a>
</p>

---

## About

This project is my personal portfolio and a practical Django application. It brings together my professional profile, technical experience, selected projects, interactive tools, and a book library.

My work focuses on network operations and infrastructure, ISP/NOC troubleshooting, MikroTik technologies, and building useful web applications with Python and Django.

## Features

- **Personal portfolio:** professional introduction, experience, skills, projects, and contact information.
- **Responsive interface:** layouts designed for desktop and mobile screens.
- **Light and dark themes:** user-selectable display themes.
- **Project showcase:** dedicated entries for selected technical projects.
- **MikroTik Configuration Generator:** an interactive tool for building and previewing RouterOS configuration scripts.
- **Algorithm Visual Studio:** an interactive environment for exploring data structures and algorithms.
- **Book Library:** book details, preview pages, order submission, payment review, and controlled PDF delivery.
- **Private owner tools:** protected operational pages and OLT-related monitoring/ingestion endpoints.
- **TKI operations area:** ticket tracking, updates, reporting, and Excel export for authorized users.

> Some operational tools are access-controlled and are not intended for public use. Access depends on server-side configuration and authorization.

## Selected Projects

| Project | Description |
|---|---|
| Django Portfolio System | This portfolio website, built with Django. |
| MikroTik Configuration Generator | RouterOS configuration builder with validation and script preview. |
| Algorithm Visual Studio | Interactive data-structure and algorithm visualizer. |

## Technology Stack

- **Backend:** Python, Django
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5
- **Database:** SQLite by default; PostgreSQL can be configured through `DATABASE_URL`
- **Static files:** WhiteNoise
- **Application server:** Gunicorn
- **Other libraries:** Pillow, OpenPyXL, dj-database-url
- **Hosting configuration:** Render Blueprint (`render.yaml`)

## Run Locally

### 1. Clone the repository

```bash
git clone https://github.com/Hasan-Gazi-1617/personal-portfolio.git
cd personal-portfolio
```

### 2. Create and activate a virtual environment

**Linux / macOS**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows PowerShell**

```powershell
py -m venv .venv
.venv\\Scripts\\Activate.ps1
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

For local development, Django can run with its local development defaults. For a production-like setup, configure a secure `SECRET_KEY` and the appropriate environment variables in your shell or local `.env` workflow.

Common settings:

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django secret key. Keep it private. |
| `DEBUG` | Enable or disable Django debug mode. Use `False` in production. |
| `DATABASE_URL` | Optional database connection URL. If omitted, SQLite is used. |
| `OWNER_ACCESS_KEY` | Secret used for protected owner access. |
| `OLT_INGEST_TOKEN` | Separate secret for the trusted OLT data collector. |
| `EMAIL_HOST`, `EMAIL_PORT` | SMTP server settings, if email delivery is configured. |
| `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` | SMTP credentials. Keep them private. |
| `EMAIL_USE_TLS` | Whether SMTP TLS is enabled. |

Never commit real credentials, API keys, tokens, or production environment files to Git.

### 5. Apply migrations and start the server

```bash
python manage.py migrate
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

## Deployment on Render

The repository includes:

- `render.yaml` for the Render web service configuration.
- `build.sh` to install dependencies, collect static files, and apply database migrations.
- Gunicorn as the production application server.
- WhiteNoise for serving collected static assets.

To deploy, connect the repository to Render and use the included Blueprint configuration. Set the required secret environment variables in the Render Dashboard. Do not put secrets in `render.yaml` or commit them to the repository.

**Database note:** SQLite is the default when `DATABASE_URL` is not set. A SQLite database stored on an ephemeral filesystem can be lost when a service is replaced or redeployed. Before relying on production records, configure and verify persistent storage or use a suitable managed database.

## Project Structure

```text
personal-portfolio/
├── books/          # Book Library application
├── config/         # Django project settings and URL configuration
├── portfolio/      # Portfolio pages, tools, and operational features
├── static/          # CSS, JavaScript, images, and other static assets
├── templates/       # Shared and page templates
├── tools/           # Project utility scripts
├── build.sh         # Render build script
├── manage.py        # Django management entry point
├── render.yaml      # Render deployment configuration
└── requirements.txt # Python dependencies
```

## Useful Commands

```bash
# Run Django system checks
python manage.py check

# Create database migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Collect static assets
python manage.py collectstatic --no-input

# Run tests
python manage.py test
```

## Security & Data Notes

- Keep `SECRET_KEY`, owner access keys, OLT tokens, SMTP credentials, and database credentials private.
- Use separate, strong secrets for separate integrations.
- Do not expose private operational dashboards or customer information.
- Review database persistence and backup arrangements before storing important production data.
- Keep `DEBUG=False` in production.

## Contact

- **Portfolio:** [personal-portfolio-069p.onrender.com](https://personal-portfolio-069p.onrender.com/)
- **GitHub:** [Hasan-Gazi-1617](https://github.com/Hasan-Gazi-1617)

---

<p align="center">
  Built with Python & Django.
</p>
