from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import sqlite3
import os

import warnings

app = Flask(__name__)
_secret_key = os.environ.get("SECRET_KEY")
if not _secret_key:
    warnings.warn(
        "SECRET_KEY is not set. Using a default insecure key. "
        "Set the SECRET_KEY environment variable in production.",
        stacklevel=1,
    )
    _secret_key = "dev-secret-key-change-in-production"
app.secret_key = _secret_key

DATABASE = os.path.join(os.path.dirname(__file__), "visits.db")


def get_db():
    conn = sqlite3.connect(DATABASE, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS visits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guest_name TEXT NOT NULL,
                contact TEXT NOT NULL,
                purpose TEXT NOT NULL,
                host TEXT NOT NULL,
                check_in_time TEXT NOT NULL,
                check_out_time TEXT
            )
        """
        )
        conn.commit()


@app.route("/")
def index():
    with get_db() as conn:
        visits = conn.execute(
            "SELECT * FROM visits ORDER BY check_in_time DESC"
        ).fetchall()
    return render_template("index.html", visits=visits)


@app.route("/checkin", methods=["GET", "POST"])
def checkin():
    if request.method == "POST":
        guest_name = request.form.get("guest_name", "").strip()
        contact = request.form.get("contact", "").strip()
        purpose = request.form.get("purpose", "").strip()
        host = request.form.get("host", "").strip()

        if not all([guest_name, contact, purpose, host]):
            flash("All fields are required.", "danger")
            return render_template("checkin.html")

        check_in_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with get_db() as conn:
            conn.execute(
                "INSERT INTO visits (guest_name, contact, purpose, host, check_in_time) VALUES (?, ?, ?, ?, ?)",
                (guest_name, contact, purpose, host, check_in_time),
            )
            conn.commit()
        flash(f"{guest_name} has been checked in successfully.", "success")
        return redirect(url_for("index"))

    return render_template("checkin.html")


@app.route("/checkout/<int:visit_id>", methods=["POST"])
def checkout(visit_id):
    with get_db() as conn:
        visit = conn.execute(
            "SELECT * FROM visits WHERE id = ?", (visit_id,)
        ).fetchone()
        if visit is None:
            flash("Visit record not found.", "danger")
            return redirect(url_for("index"))
        if visit["check_out_time"]:
            flash("Guest has already checked out.", "warning")
            return redirect(url_for("index"))
        check_out_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn.execute(
            "UPDATE visits SET check_out_time = ? WHERE id = ?",
            (check_out_time, visit_id),
        )
        conn.commit()
    flash(f"{visit['guest_name']} has been checked out.", "success")
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug)
