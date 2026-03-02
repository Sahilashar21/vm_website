from flask import Flask, flash, redirect, render_template, request, url_for

app = Flask(__name__)
app.secret_key = "vidyarthi-mitra-dev-key"


UNIVERSITIES_DATA = [
    {
        "slug": "savitribai-phule-pune-university",
        "name": "Savitribai Phule Pune University",
        "location": "Pune",
        "state": "Maharashtra",
        "type": "Government",
        "stream": "General",
        "nirf": "19",
        "logo_url": "/static/logo.png",
    },
    {
        "slug": "university-of-mumbai",
        "name": "University of Mumbai",
        "location": "Mumbai",
        "state": "Maharashtra",
        "type": "Government",
        "stream": "General",
        "nirf": "45",
        "logo_url": "/static/logo.png",
    },
    {
        "slug": "rtm-nagpur-university",
        "name": "Rashtrasant Tukadoji Maharaj Nagpur University",
        "location": "Nagpur",
        "state": "Maharashtra",
        "type": "Government",
        "stream": "General",
        "nirf": "74",
        "logo_url": "/static/logo.png",
    },
    {
        "slug": "symbiosis-international",
        "name": "Symbiosis International (Deemed University)",
        "location": "Pune",
        "state": "Maharashtra",
        "type": "Deemed",
        "stream": "Management",
        "nirf": "17",
        "logo_url": "/static/logo.png",
    },
    {
        "slug": "mit-wpu",
        "name": "MIT World Peace University",
        "location": "Pune",
        "state": "Maharashtra",
        "type": "Private",
        "stream": "Technology",
        "nirf": "96",
        "logo_url": "/static/logo.png",
    },
    {
        "slug": "nmims-mumbai",
        "name": "NMIMS University",
        "location": "Mumbai",
        "state": "Maharashtra",
        "type": "Private",
        "stream": "Management",
        "nirf": "49",
        "logo_url": "/static/logo.png",
    },
]


COLLEGES_DATA = [
    {
        "name": "COEP Technological University",
        "state": "Maharashtra",
        "city": "Pune",
        "type": "Government",
        "stream": "Engineering",
        "nirf": "73",
        "logo_url": "/static/logo.png",
        "source_url": "https://www.coep.org.in",
    },
    {
        "name": "VJTI Mumbai",
        "state": "Maharashtra",
        "city": "Mumbai",
        "type": "Government",
        "stream": "Engineering",
        "nirf": "101-150",
        "logo_url": "/static/logo.png",
        "source_url": "https://vjti.ac.in",
    },
    {
        "name": "Fergusson College",
        "state": "Maharashtra",
        "city": "Pune",
        "type": "Autonomous",
        "stream": "Arts & Science",
        "nirf": "58",
        "logo_url": "/static/logo.png",
        "source_url": "https://fergusson.edu",
    },
    {
        "name": "St. Xavier's College",
        "state": "Maharashtra",
        "city": "Mumbai",
        "type": "Private",
        "stream": "Arts & Science",
        "nirf": "89",
        "logo_url": "/static/logo.png",
        "source_url": "https://xaviers.edu",
    },
    {
        "name": "KJ Somaiya College of Engineering",
        "state": "Maharashtra",
        "city": "Mumbai",
        "type": "Private",
        "stream": "Engineering",
        "nirf": "151-200",
        "logo_url": "/static/logo.png",
        "source_url": "https://kjsit.somaiya.edu",
    },
    {
        "name": "Ness Wadia College",
        "state": "Maharashtra",
        "city": "Pune",
        "type": "Aided",
        "stream": "Commerce",
        "nirf": "101-150",
        "logo_url": "/static/logo.png",
        "source_url": "https://nesswadia.edu",
    },
]


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
    states = sorted({item["state"] for item in UNIVERSITIES_DATA})
    cities = sorted({item["location"] for item in UNIVERSITIES_DATA})
    types = sorted({item["type"] for item in UNIVERSITIES_DATA})
    streams = sorted({item["stream"] for item in UNIVERSITIES_DATA})
    return render_template(
        "universities.html",
        universities=UNIVERSITIES_DATA,
        states=states,
        cities=cities,
        types=types,
        streams=streams,
    )


@app.route("/universities/<slug>")
def university_detail(slug):
    university = next((item for item in UNIVERSITIES_DATA if item["slug"] == slug), None)
    if university is None:
        return redirect(url_for("universities"))
    return render_template("universities.html", universities=[university], states=[], cities=[], types=[], streams=[])


@app.route("/colleges")
def colleges():
    states = sorted({item["state"] for item in COLLEGES_DATA})
    cities = sorted({item["city"] for item in COLLEGES_DATA})
    types = sorted({item["type"] for item in COLLEGES_DATA})
    streams = sorted({item["stream"] for item in COLLEGES_DATA})
    return render_template(
        "colleges.html",
        colleges=COLLEGES_DATA,
        states=states,
        cities=cities,
        types=types,
        streams=streams,
    )


@app.route("/courses")
def courses():
    return render_template("courses.html")


@app.route("/exams")
@app.route("/entrance_exams")
@app.route("/entrance-exams")
def exams():
    return render_template("exams.html")


@app.route("/mock-exams")
@app.route("/mock_exams")
def mock_exams():
    return render_template("mock_exams.html")


@app.route("/cutoffs")
def cutoffs():
    return render_template("cutoffs.html")


@app.route("/admissions")
def admissions():
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


@app.route("/feedback", methods=["GET", "POST"])
def feedback():
    if request.method == "POST":
        required_fields = [
            "u_name",
            "u_mobile",
            "u_email",
            "u_designation",
            "u_feedback",
        ]
        missing_fields = [field for field in required_fields if not request.form.get(field, "").strip()]

        if missing_fields:
            flash("Please fill all required fields before submitting.", "error")
            return render_template("feedback.html")

        flash("Feedback submitted successfully. Thank you!", "success")
        return redirect(url_for("feedback"))

    return render_template("feedback.html")


@app.route("/chatbot")
def chatbot():
    return render_template("chatbot.html")


@app.route("/guideme", methods=["GET", "POST"])
@app.route("/guide-me", methods=["GET", "POST"])
def guide_me():
    if request.method == "POST":
        required_fields = ["full_name", "whatsapp", "email", "address", "requirement_type"]
        missing_fields = [field for field in required_fields if not request.form.get(field, "").strip()]

        if missing_fields:
            flash("Please complete all required Guide Me form fields.", "error")
            return render_template("GuideMe1.html")

        flash("Guide Me form submitted successfully.", "success")
        return redirect(url_for("guide_me"))

    return render_template("GuideMe1.html")

@app.route('/refund-policy')
def refund_policy():
    return render_template('refund.html')


if __name__ == "__main__":
    app.run(debug=True)
