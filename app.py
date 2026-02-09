from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/blog")
def blog():
    return render_template("index.html")  # Placeholder


@app.route("/epaper")
def epaper():
    return render_template("index.html")  # Placeholder


@app.route("/universities")
def universities():
    return render_template("index.html")  # Placeholder


@app.route("/courses")
def courses():
    return render_template("index.html")  # Placeholder


@app.route("/exams")
def exams():
    return render_template("index.html")  # Placeholder


@app.route("/mock-exams")
def mock_exams():
    return render_template("index.html")  # Placeholder


@app.route("/guide")
def guide():
    return render_template("index.html")  # Placeholder


@app.route("/news")
def news():
    return render_template("index.html")  # Placeholder


@app.route("/articles")
def articles():
    return render_template("index.html")  # Placeholder


@app.route("/stories")
def stories():
    return render_template("index.html")  # Placeholder


@app.route("/feedback")
def feedback():
    return render_template("index.html")  # Placeholder


if __name__ == "__main__":
    app.run(debug=True)
