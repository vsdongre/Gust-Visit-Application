# Guest Visit Application

A simple web application for managing guest visits. Security staff or receptionists can check guests in, and check them out when they leave. All visits are logged in a searchable dashboard.

## Features

- **Guest Check-In** – record guest name, contact, purpose of visit, and host
- **Guest Check-Out** – mark a guest as having left with a single click
- **Visit Log / Dashboard** – view currently on-site guests and the full history of past visits

## Tech Stack

- **Backend**: Python / Flask
- **Database**: SQLite (file-based, zero configuration)
- **Frontend**: HTML + Bootstrap 5

## Setup & Running

### Prerequisites

- Python 3.8 or newer

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/vsdongre/Gust-Visit-Application.git
cd Gust-Visit-Application

# 2. Create and activate a virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the application
python app.py
```

The app will start on **http://127.0.0.1:5000** by default.

### Environment Variables

| Variable | Default | Description |
|---|---|---|
| `SECRET_KEY` | `dev-secret-key-change-in-production` | Flask session secret. **Change this in production.** |

## Project Structure

```
.
├── app.py              # Flask application & routes
├── requirements.txt    # Python dependencies
├── visits.db           # SQLite database (created automatically on first run)
└── templates/
    ├── base.html       # Shared layout with Bootstrap navbar
    ├── index.html      # Visit log / dashboard
    └── checkin.html    # Guest check-in form
```