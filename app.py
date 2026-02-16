from flask import Flask, render_template

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/universities")
def universities():
    return render_template("index.html")


@app.route("/colleges")
def colleges():
    return render_template("index.html")


@app.route("/courses")
def courses():
    return render_template("index.html")


@app.route("/exams")
def exams():
    return render_template("index.html")


@app.route("/mock-exams")
def mock_exams():
    return render_template("index.html")


@app.route("/epaper")
def epaper():
    return render_template("index.html")


@app.route("/guide")
def guide():
    return render_template("index.html")


@app.route("/blog")
def blog():
    return render_template("index.html")


@app.route("/news")
def news():
    return render_template("index.html")


@app.route("/feedback")
def feedback():
    return render_template("index.html")


@app.errorhandler(404)
def not_found(error):
    return render_template("index.html"), 404


if __name__ == "__main__":
    app.run(debug=True)

