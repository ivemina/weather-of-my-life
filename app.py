from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "<h1>The Weather of My Life</h1><p>My first Flask page is alive.</p>"

if __name__ == "__main__":
    app.run(debug=True)
    