from datetime import date
from flask import Flask, render_template

app = Flask(__name__)

# All the moods live in ONE place. To rename or change one later,
# you only edit this list.
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


@app.route("/")
def today():
    today_date = date.today()
    return render_template(
        "today.html",
        moods=MOODS,
        today_text=today_date.strftime("%A %d %B %Y"),
        today_iso=today_date.isoformat(),
    )


if __name__ == "__main__":
    app.run(debug=True)