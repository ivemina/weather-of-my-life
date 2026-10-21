import calendar
import sqlite3
from datetime import date, datetime
from flask import Flask, render_template, request, redirect, url_for, flash, g, abort 

app = Flask(__name__)
# Needed for flash messages. Fine for local use; we'll move it to a
# hidden setting before deploying.
app.secret_key = "dev-only-change-me"

DATABASE = "weather.db"

MOODS = [
    {"key": "sunny", "emoji": "☀️", "label": "Sunny",
     "meaning": "Happy, energised, or content"},
    {"key": "partly_cloudy", "emoji": "⛅", "label": "Partly cloudy",
     "meaning": "Calm, okay, a normal day"},
    {"key": "cloudy", "emoji": "☁️", "label": "Cloudy",
     "meaning": "Tired, uncertain, or reflective"},
    {"key": "rainy", "emoji": "🌧️", "label": "Rainy",
     "meaning": "Sad, lonely, or a hard day"},
    {"key": "stormy", "emoji": "⛈️", "label": "Stormy",
     "meaning": "Overwhelmed, angry, or stressed"},
    {"key": "rainbow", "emoji": "🌈", "label": "Rainbow",
     "meaning": "Relief, hope, or things getting better"},
]
VALID_MOODS = {m["key"] for m in MOODS}


# ---------- Database helpers ----------

def get_db():
    """Open one database connection per request and reuse it."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # lets us read columns by name
    return g.db


@app.teardown_appcontext
def close_db(exception):
    """Close the connection when the request finishes."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the table if it doesn't exist yet."""
    db = sqlite3.connect(DATABASE)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS entries (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_date TEXT NOT NULL UNIQUE,
            mood       TEXT NOT NULL,
            moment     TEXT NOT NULL,
            journal    TEXT NOT NULL DEFAULT '',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    db.commit()
    db.close()


# ---------- Pages ----------

@app.route("/")
def today():
    today_date = date.today()
    existing = get_db().execute(
        "SELECT * FROM entries WHERE entry_date = ?",
        (today_date.isoformat(),),
    ).fetchone()
    return render_template(
        "today.html",
        moods=MOODS,
        today_text=today_date.strftime("%A %d %B %Y"),
        today_iso=today_date.isoformat(),
        existing=existing,
    )


@app.route("/save", methods=["POST"])
def save():
    entry_date = request.form.get("entry_date", "")
    mood = request.form.get("mood", "")
    moment = request.form.get("moment", "").strip()
    journal = request.form.get("journal", "").strip()

    # Never trust the browser: check the data again on the server.
    try:
        datetime.strptime(entry_date, "%Y-%m-%d")
    except ValueError:
        flash("That date doesn't look right.", "error")
        return redirect(url_for("today"))

    if mood not in VALID_MOODS:
        flash("Please choose how the day felt.", "error")
        return redirect(url_for("today"))
    if not moment or len(moment) > 200:
        flash("Add a memorable moment (up to 200 characters).", "error")
        return redirect(url_for("today"))

    now = datetime.now().isoformat(timespec="seconds")
    db = get_db()
    db.execute(
        """
        INSERT INTO entries (entry_date, mood, moment, journal, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(entry_date) DO UPDATE SET
            mood = excluded.mood,
            moment = excluded.moment,
            journal = excluded.journal,
            updated_at = excluded.updated_at
        """,
        (entry_date, mood, moment, journal, now, now),
    )
    db.commit()
    flash("Saved. Your day has been added to your weather.", "success")
    if entry_date == date.today().isoformat():
     return redirect(url_for("today"))
    return redirect(url_for("day_details", entry_date=entry_date))

@app.route("/calendar")
def calendar_page():
    today_date = date.today()

    try:
        year = int(request.args.get("year", today_date.year))
        month = int(request.args.get("month", today_date.month))
        date(year, month, 1)
    except ValueError:
        year, month = today_date.year, today_date.month

    prev_year, prev_month = (year - 1, 12) if month == 1 else (year, month - 1)
    next_year, next_month = (year + 1, 1) if month == 12 else (year, month + 1)

    prefix = f"{year:04d}-{month:02d}-"
    rows = get_db().execute(
        "SELECT * FROM entries WHERE entry_date LIKE ?",
        (prefix + "%",),
    ).fetchall()
    entries_by_day = {int(r["entry_date"][-2:]): r for r in rows}

    moods_by_key = {m["key"]: m for m in MOODS}

    weeks = []
    for week in calendar.Calendar(firstweekday=0).monthdayscalendar(year, month):
        cells = []
        for day in week:
            if day == 0:
                cells.append(None)
            else:
                entry = entries_by_day.get(day)
                cells.append({
                    "day": day,
                    "iso": f"{year:04d}-{month:02d}-{day:02d}",
                    "entry": entry,
                    "mood": moods_by_key.get(entry["mood"]) if entry else None,
                    "is_today": date(year, month, day) == today_date,
                })
        weeks.append(cells)

    return render_template(
        "calendar.html",
        weeks=weeks,
        month_title=date(year, month, 1).strftime("%B %Y"),
        prev_year=prev_year, prev_month=prev_month,
        next_year=next_year, next_month=next_month,
        moods=MOODS,
    )

@app.route("/day/<entry_date>")
def day_details(entry_date):
    # Check the date in the address is a real date
    try:
        parsed = datetime.strptime(entry_date, "%Y-%m-%d").date()
    except ValueError:
        abort(404)

    entry = get_db().execute(
        "SELECT * FROM entries WHERE entry_date = ?",
        (entry_date,),
    ).fetchone()

    mood = next((m for m in MOODS if entry and m["key"] == entry["mood"]), None)

    return render_template(
        "day.html",
        entry=entry,
        mood=mood,
        entry_date=entry_date,
        date_text=parsed.strftime("%A %d %B %Y"),
        month_year=parsed.year,
        month_number=parsed.month,
    )
@app.route("/day/<entry_date>/delete", methods=["POST"])
def delete_entry(entry_date):
    try:
        parsed = datetime.strptime(entry_date, "%Y-%m-%d").date()
    except ValueError:
        abort(404)

    db = get_db()
    db.execute("DELETE FROM entries WHERE entry_date = ?", (entry_date,))
    db.commit()
    flash("That memory has been deleted.", "success")
    return redirect(url_for("calendar_page", year=parsed.year, month=parsed.month))
@app.route("/day/<entry_date>/edit")
def edit_entry(entry_date):
    try:
        parsed = datetime.strptime(entry_date, "%Y-%m-%d").date()
    except ValueError:
        abort(404)

    existing = get_db().execute(
        "SELECT * FROM entries WHERE entry_date = ?",
        (entry_date,),
    ).fetchone()

    return render_template(
        "today.html",
        moods=MOODS,
        today_text=parsed.strftime("%A %d %B %Y"),
        today_iso=entry_date,
        existing=existing,
        page_title="Edit memory" if existing else "Add memory",
    )

init_db()

if __name__ == "__main__":
    app.run(debug=True)