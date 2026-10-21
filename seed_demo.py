"""Fill the database with made-up demo entries for the last 40 days.
Existing entries are never overwritten."""
import random
import sqlite3
from datetime import date, datetime, timedelta

MOODS = ["sunny", "partly_cloudy", "cloudy", "rainy", "stormy", "rainbow"]
MOMENTS = {
    "sunny": ["Long walk by the river", "Finished a project I was proud of",
              "Lunch with an old friend"],
    "partly_cloudy": ["Quiet day, got a few things done", "Tried a new recipe",
                      "Caught up on emails"],
    "cloudy": ["Felt tired and slow", "Not sure what I want to do next",
               "Stayed in and reflected"],
    "rainy": ["Missed someone today", "A hard conversation", "Everything felt heavy"],
    "stormy": ["Too many deadlines at once", "Argued over something small",
               "Overwhelmed by my to-do list"],
    "rainbow": ["Good news after a long wait", "Things finally started to improve",
                "Felt relief after a stressful week"],
}

random.seed(42)  # same demo data every time
db = sqlite3.connect("weather.db")
db.execute(
    """CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entry_date TEXT NOT NULL UNIQUE,
        mood TEXT NOT NULL,
        moment TEXT NOT NULL,
        journal TEXT NOT NULL DEFAULT '',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL)"""
)

now = datetime.now().isoformat(timespec="seconds")
added = 0
for days_ago in range(40):
    if random.random() < 0.25:      # leave some days empty, like real life
        continue
    day = (date.today() - timedelta(days=days_ago)).isoformat()
    mood = random.choice(MOODS)
    moment = random.choice(MOMENTS[mood])
    cur = db.execute(
        "INSERT OR IGNORE INTO entries "
        "(entry_date, mood, moment, journal, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (day, mood, moment, "Sample entry for the demo.", now, now),
    )
    added += cur.rowcount
db.commit()
db.close()
print(f"Added {added} demo entries.")