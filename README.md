# Guest Visit Application

A web-based application to manage guest visits to your facility. Supports guest check-in/check-out, visit logging, and a live dashboard.

## Features

- **Guest Check-In** – Register a visitor with their name, email, phone, host, and purpose of visit.
- **Guest Check-Out** – Record departure time and automatically calculate visit duration.
- **Live Dashboard** – See all currently checked-in visitors at a glance along with today's and total visit counts.
- **Visit Log** – Browse the complete visit history with search and status filters.
- **Visit Detail** – View full details of any individual visit.
- **REST API** – `/api/stats` and `/api/active-visits` endpoints for integration.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3 / Flask |
| Database | SQLite (via Flask-SQLAlchemy) |
| Frontend | Bootstrap 5, Bootstrap Icons |

## Setup

```bash
# 1. Clone the repository
git clone https://github.com/vsdongre/Gust-Visit-Application.git
cd Gust-Visit-Application

# 2. Create and activate a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py
```

Then open http://127.0.0.1:5000 in your browser.

## Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `SECRET_KEY` | `dev-secret-key-change-in-production` | Flask secret key – **change in production** |
| `DATABASE_URL` | `sqlite:///visits.db` | SQLAlchemy database URI |

## Running Tests

```bash
pip install pytest
python -m pytest tests.py -v
```

## Project Structure

```
.
├── app.py              # Flask application, routes, and data model
├── requirements.txt    # Python dependencies
├── tests.py            # Pytest test suite
├── static/
│   ├── css/style.css   # Custom styles
│   └── js/app.js       # Client-side JavaScript
└── templates/
    ├── base.html        # Shared layout (navbar, footer, flash messages)
    ├── index.html       # Dashboard
    ├── checkin.html     # Guest check-in form
    ├── log.html         # Visit log with filters and pagination
    └── visit_detail.html # Individual visit detail page
```
