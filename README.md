# The Weather of My Life

A weather-inspired journal that turns daily moods and memories into a calendar.
Each day gets a weather symbol, so you can look back on a month and see its shape.

**Live demo:** YOUR-LIVE-ADDRESS-HERE
(Demo entries are made-up samples. Anyone can edit them, and they may be reset.)

![Calendar view](docs/calendar.png)

## Features

- Record how a day felt using six weather moods, plus a memorable moment and an optional journal entry
- Monthly calendar with a weather symbol, colour and text label for every day
- Open, edit or delete any day's memory
- Monthly summary showing how many days of each mood you recorded
- One entry per day: saving again for the same date updates it
- Works on phones and with a keyboard only

## Design decisions

- **Mood is never shown by colour alone.** Every mood has a symbol, a colour and a text label, so the calendar is readable for colour-blind users and screen readers.
- **No medical claims.** The app only reflects what the user recorded. It doesn't interpret moods or draw conclusions about health.
- **Honest summaries.** The summary shows "X of 31 days recorded", so a month with few entries isn't mistaken for a full picture.

## Tech stack

Python, Flask, SQLite, Jinja2 templates, HTML and CSS. Hosted on PythonAnywhere.
Designed first in Figma (wireframes in `docs/`).

## What I built and how it works

- **Database:** one `entries` table with a UNIQUE constraint on the date. Saves use an upsert (`ON CONFLICT DO UPDATE`).
- **Security:** parameterised SQL queries against injection, server-side validation of every field, automatic HTML escaping in templates, POST-only routes with a confirmation for deletion, and the secret key read from an environment variable.
- **Calendar logic:** uses Python's `calendar` module, handles month and year boundaries and leap years, and falls back safely on invalid dates in the address.
- **Accessibility:** skip link, visible focus outlines, labelled form fields, reduced-motion support.

## Run it locally (Windows)

```
git clone https://github.com/ivemina/weather-of-my-life.git
cd weather-of-my-life
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

Then open http://127.0.0.1:5000. To fill it with sample data, run `python seed_demo.py`.

## Limitations and future improvements

- Single user, with no login (the public demo uses sample data only)
- No automated tests yet (all features were tested manually against a written checklist)
- Ideas for later: user accounts, photos, a real-weather API, yearly timeline, data export