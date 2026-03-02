import html
import re
import time
import os
import json
from urllib.parse import unquote, urljoin, urlparse
from urllib.request import Request, urlopen
from dotenv import load_dotenv
from functools import wraps

from flask import Flask, render_template, request, jsonify, session, redirect, url_for

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')


UNIVERSITY_STATES = [
    "Andaman and Nicobar Islands",
    "Andhra Pradesh",
    "Assam",
    "Bihar",
    "Chandigarh",
    "Delhi",
    "Goa",
    "Gujarat",
    "Haryana",
    "Karnataka",
    "Maharashtra",
    "Tamil Nadu",
    "Uttar Pradesh",
    "West Bengal",
]


TOP_UNIVERSITIES = [
    {
        "name": "Indian Institute of Science, Bangalore",
        "slug": "INDIAN-INSTITUTE-OF-SCIENCE,-BANGALORE",
        "location": "Bengaluru",
        "type": "Deemed University - Government",
        "nirf": "1",
        "logo_url": "/static/logo.png",
    },
    {
        "name": "University of Delhi",
        "slug": "UNIVERSITY-OF-DELHI",
        "location": "Delhi",
        "type": "Central University",
        "nirf": "6",
        "logo_url": "/static/IITDELHI.jpg",
    },
    {
        "name": "Anna University, Chennai",
        "slug": "ANNA-UNIVERSITY,-CHENNAI",
        "location": "Chennai",
        "type": "State University",
        "nirf": "14",
        "logo_url": "/static/COEP_Pune_logo.jpeg",
    },
    {
        "name": "Jadavpur University, Kolkata",
        "slug": "JADAVPUR-UNIVERSITY,-KOLKATA",
        "location": "Kolkata",
        "type": "State University",
        "nirf": "9",
        "logo_url": "/static/IIIT PUNE.jpeg",
    },
]

DEFAULT_UNIVERSITY_STREAMS = [
    "Engineering",
    "Management",
    "Medical",
    "Law",
    "Commerce",
    "Arts",
    "Architecture",
    "Computer Applications",
]


LIVE_UNIVERSITIES_URL = "https://vidyarthimitra.org/universities"
UNIVERSITY_CACHE_SECONDS = 900
UNIVERSITY_CACHE = {
    "fetched_at": 0,
    "universities": TOP_UNIVERSITIES,
}

UNIVERSITY_DETAIL_CACHE_SECONDS = 1800
UNIVERSITY_DETAIL_CACHE = {}


LIVE_COLLEGES_URL = "https://vidyarthimitra.org/colleges"
COLLEGE_CACHE_SECONDS = 900
TOP_COLLEGES = [
    {
        "name": "Indian Institute of Technology, Madras",
        "slug": "Indian-Institute-Of-Technology,-Madras",
        "city": "Chennai",
        "type": "Government",
        "nirf": "1",
        "logo_url": "/static/logo.png",
        "source_url": "https://vidyarthimitra.org/colleges/Indian-Institute-Of-Technology,-Madras",
    },
    {
        "name": "Indian Institute of Technology, Delhi",
        "slug": "Indian-institute-of-technology-delhi",
        "city": "Delhi",
        "type": "Government",
        "nirf": "2",
        "logo_url": "/static/logo.png",
        "source_url": "https://vidyarthimitra.org/colleges/Indian-institute-of-technology-delhi",
    },
    {
        "name": "Indian Institute of Technology, Bombay",
        "slug": "Indian-Institute-Of-Technology,-Bombay",
        "city": "Mumbai City",
        "type": "Government",
        "nirf": "3",
        "logo_url": "/static/logo.png",
        "source_url": "https://vidyarthimitra.org/colleges/Indian-Institute-Of-Technology,-Bombay",
    },
]

DEFAULT_COLLEGE_STREAMS = [
    "Engineering",
    "Management",
    "Medical",
    "Commerce",
    "Arts",
    "Architecture",
    "Pharmacy",
    "Computer Applications",
]

COLLEGE_CACHE = {
    "fetched_at": 0,
    "colleges": TOP_COLLEGES,
    "states": UNIVERSITY_STATES,
    "cities": ["Chennai", "Delhi", "Mumbai City"],
    "types": ["Government", "Public", "Private"],
    "streams": DEFAULT_COLLEGE_STREAMS,
}


LIVE_COURSES_URL = "https://vidyarthimitra.org/courses"
COURSE_CACHE_SECONDS = 900
TOP_COURSES = [
    {
        "name": "Bachelor of Technology",
        "slug": "Bachelor-of-Technology",
        "stream": "Engineering",
        "logo_url": "/static/logo.png",
        "source_url": "https://vidyarthimitra.org/courses/Bachelor-of-Technology",
    },
    {
        "name": "Bachelor of Medicine",
        "slug": "Bachelor-of-Medicine-Bachelor-of-Surgery",
        "stream": "Medical",
        "logo_url": "/static/logo.png",
        "source_url": "https://vidyarthimitra.org/courses/Bachelor-of-Medicine-Bachelor-of-Surgery",
    },
    {
        "name": "Bachelor of Law",
        "slug": "Integrated-BA-LLB",
        "stream": "Law",
        "logo_url": "/static/logo.png",
        "source_url": "https://vidyarthimitra.org/courses/Integrated-BA-LLB",
    },
]

DEFAULT_COURSE_STREAMS = [
    "Engineering",
    "Medical",
    "Law",
    "Commerce",
    "Arts",
    "Architecture",
    "Management",
    "Computer Applications",
    "Pharmacy",
    "Design",
    "Aviation",
    "Banking",
]

COURSE_CACHE = {
    "fetched_at": 0,
    "courses": TOP_COURSES,
    "streams": sorted(DEFAULT_COURSE_STREAMS),
}


def _clean_html_text(value):
    text = re.sub(r"<[^>]+>", " ", value)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_universities_from_html(page_html):
    anchor_pattern = re.compile(
        r"<a[^>]+href=[\"\'](?P<href>[^\"\']*?/universities/[^\"\']+)[\"\'][^>]*>(?P<label>.*?)</a>",
        re.IGNORECASE | re.DOTALL,
    )

    universities = []
    seen = set()

    for match in anchor_pattern.finditer(page_html):
        href = match.group("href")
        slug = href.rstrip("/").split("/")[-1].strip()
        if not slug or slug.lower() == "universities":
            continue

        slug_name = re.sub(r"\s+", " ", unquote(slug).replace("-", " ")).strip(" ,")
        label_text = _clean_html_text(match.group("label"))

        name = slug_name
        if label_text and "nirf" not in label_text.lower() and len(label_text.split()) <= 12:
            name = label_text

        name = re.sub(r"\s+", " ", name).strip(" -|,")
        if not name:
            continue

        key = name.lower()
        if key in seen:
            continue
        seen.add(key)

        snippet_start = max(0, match.start() - 1400)
        snippet_end = min(len(page_html), match.end() + 1400)
        snippet = page_html[snippet_start:snippet_end]

        image_match = re.search(r"<img[^>]+src=[\"\']([^\"\']+)[\"\']", snippet, re.IGNORECASE)
        nirf_match = re.search(r"NIRF\s*[:\-]?\s*(\d{1,3})", snippet, re.IGNORECASE)

        university_type = "Updated Live"
        type_match = re.search(
            r"(Central University|State University|Deemed University|Private University|Government University)",
            snippet,
            re.IGNORECASE,
        )
        if type_match:
            university_type = type_match.group(1).title()

        location = "India"
        location_match = re.search(
            r"(?:fa-map-marker|fa-location-dot)[^<]{0,40}<[^>]*>\s*([^<]{2,50})\s*<",
            snippet,
            re.IGNORECASE,
        )
        if location_match:
            location = _clean_html_text(location_match.group(1)).title()

        universities.append(
            {
                "name": name,
                "slug": slug,
                "location": location,
                "type": university_type,
                "nirf": nirf_match.group(1) if nirf_match else "-",
                "logo_url": urljoin(LIVE_UNIVERSITIES_URL, image_match.group(1)) if image_match else "/static/logo.png",
            }
        )

        if len(universities) >= 60:
            break

    return universities


def get_live_universities():
    now = time.time()
    if now - UNIVERSITY_CACHE["fetched_at"] < UNIVERSITY_CACHE_SECONDS:
        return UNIVERSITY_CACHE["universities"]

    try:
        request = Request(
            LIVE_UNIVERSITIES_URL,
            headers={"User-Agent": "Mozilla/5.0"},
        )
        with urlopen(request, timeout=15) as response:
            page_html = response.read().decode("utf-8", errors="ignore")

        universities = _extract_universities_from_html(page_html)
        if universities:
            UNIVERSITY_CACHE["fetched_at"] = now
            UNIVERSITY_CACHE["universities"] = universities
            return universities
    except Exception:
        pass

    return UNIVERSITY_CACHE["universities"]


def _extract_colleges_from_html(page_html):
    anchor_pattern = re.compile(
        r"<a[^>]+href=[\"\'](?P<href>[^\"\']*?/colleges/[^\"\']+)[\"\'][^>]*>(?P<label>.*?)</a>",
        re.IGNORECASE | re.DOTALL,
    )

    colleges = []
    seen = set()

    type_pattern = re.compile(
        r"(UNIVERSITY MANAGED-GOVT|UNIVERSITY MANAGED|GOVERNMENT-AIDED|DEEMED UNIVERSITY|UNAIDED PRIVATE|PRIVATE-AIDED|GOVERNMENT|PUBLIC|PRIVATE)",
        re.IGNORECASE,
    )

    for match in anchor_pattern.finditer(page_html):
        href = match.group("href")
        slug = href.rstrip("/").split("/")[-1].strip()
        if not slug or slug.lower() in {"colleges", "index"}:
            continue

        key = slug.lower()
        if key in seen:
            continue
        seen.add(key)

        slug_name = re.sub(r"\s+", " ", unquote(slug).replace("-", " ")).strip(" ,")
        label_text = _clean_html_text(match.group("label"))

        name = slug_name
        city = "India"
        college_type = "Updated Live"

        type_match = type_pattern.search(label_text)
        if type_match:
            college_type = type_match.group(1).title()

            prefix = label_text[: type_match.start()].strip(" ,-|")
            if prefix:
                if slug_name.lower() in prefix.lower():
                    suffix = re.sub(re.escape(slug_name), "", prefix, flags=re.IGNORECASE).strip(" ,-|")
                    if suffix:
                        city = suffix.title()
                        name = prefix[: prefix.lower().find(suffix.lower())].strip(" ,-|") or slug_name
                    else:
                        name = prefix
                else:
                    name = prefix

        nirf_match = re.search(r"NIRF\s*[:\-]?\s*(\d{1,3})", label_text, re.IGNORECASE)

        snippet_start = max(0, match.start() - 1200)
        snippet_end = min(len(page_html), match.end() + 1200)
        snippet = page_html[snippet_start:snippet_end]
        image_match = re.search(r"<img[^>]+src=[\"\']([^\"\']+)[\"\']", snippet, re.IGNORECASE)

        name = re.sub(r"\s+", " ", name).strip(" -|,") or slug_name
        if len(name) < 4:
            continue

        city = re.sub(r"\s+", " ", city).strip(" -|,")
        if not city or len(city) > 40:
            city = "India"

        colleges.append(
            {
                "name": name,
                "slug": slug,
                "city": city,
                "type": college_type,
                "nirf": nirf_match.group(1) if nirf_match else "-",
                "logo_url": urljoin(LIVE_COLLEGES_URL, image_match.group(1)) if image_match else "/static/logo.png",
                "source_url": urljoin(LIVE_COLLEGES_URL, href),
            }
        )

        if len(colleges) >= 90:
            break

    return colleges


def get_live_colleges():
    now = time.time()
    if now - COLLEGE_CACHE["fetched_at"] < COLLEGE_CACHE_SECONDS:
        return COLLEGE_CACHE

    try:
        request = Request(LIVE_COLLEGES_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(request, timeout=20) as response:
            page_html = response.read().decode("utf-8", errors="ignore")

        colleges = _extract_colleges_from_html(page_html)
        if colleges:
            city_options = sorted({college["city"] for college in colleges if college["city"] != "India"})
            type_options = sorted({college["type"] for college in colleges if college["type"]})

            COLLEGE_CACHE.update(
                {
                    "fetched_at": now,
                    "colleges": colleges,
                    "states": UNIVERSITY_STATES,
                    "cities": city_options[:120],
                    "types": type_options,
                    "streams": DEFAULT_COLLEGE_STREAMS,
                }
            )
    except Exception:
        pass

    return COLLEGE_CACHE


def _extract_courses_from_html(page_html):
    stream_pattern = re.compile(
        r"<a[^>]+href=[\"\']([^\"\']*?/stream/courses/([^\"\']+))[\"\'][^>]*>\+more</a>",
        re.IGNORECASE | re.DOTALL,
    )

    course_in_section_pattern = re.compile(
        r"<a[^>]+href=[\"\'](?P<href>https?://vidyarthimitra\.org/courses/[^\"\']+)[\"\'][^>]*>(?P<name>[^<]+?)</a>(?!\s*/stream)",
        re.IGNORECASE,
    )

    courses = []
    seen = set()
    pos = 0

    for stream_match in stream_pattern.finditer(page_html):
        stream_href = stream_match.group(1)
        stream_name = stream_match.group(2)
        stream_name = stream_name.replace("-", " ").title()

        section_start = pos
        section_end = stream_match.start()
        section_html = page_html[section_start:section_end]

        for course_match in course_in_section_pattern.finditer(section_html):
            href = course_match.group("href")
            name = course_match.group("name").strip()

            slug = href.split("/")[-1]
            key = slug.lower()

            if key in seen or not name or len(name) < 2:
                continue

            seen.add(key)

            snippet_start = max(0, course_match.start() - 800)
            snippet_end = min(len(section_html), course_match.end() + 800)
            snippet = section_html[snippet_start:snippet_end]
            image_match = re.search(r"<img[^>]+src=[\"\']([^\"\']+)[\"\']", snippet, re.IGNORECASE)

            courses.append(
                {
                    "name": name,
                    "slug": slug,
                    "stream": stream_name,
                    "logo_url": urljoin(LIVE_COURSES_URL, image_match.group(1)) if image_match else "/static/logo.png",
                    "source_url": urljoin(LIVE_COURSES_URL, href),
                }
            )

            if len(courses) >= 150:
                break

        if len(courses) >= 150:
            break

        pos = stream_match.end()

    return courses


def get_live_courses():
    now = time.time()
    if now - COURSE_CACHE["fetched_at"] < COURSE_CACHE_SECONDS:
        return COURSE_CACHE

    try:
        request = Request(LIVE_COURSES_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(request, timeout=20) as response:
            page_html = response.read().decode("utf-8", errors="ignore")

        courses = _extract_courses_from_html(page_html)
        if courses:
            stream_options = sorted({course["stream"] for course in courses if course["stream"]})

            COURSE_CACHE.update(
                {
                    "fetched_at": now,
                    "courses": courses,
                    "streams": stream_options,
                }
            )
    except Exception:
        pass

    return COURSE_CACHE


def _extract_history_text(page_html, text_fallback):
    history_block = re.search(
        r"<h[1-6][^>]*>\s*history\s*</h[1-6]>(?P<body>[\s\S]{0,5000})",
        page_html,
        re.IGNORECASE,
    )
    if history_block:
        paragraphs = re.findall(r"<p[^>]*>([\s\S]*?)</p>", history_block.group("body"), re.IGNORECASE)
        cleaned = [
            _clean_html_text(paragraph)
            for paragraph in paragraphs
            if _clean_html_text(paragraph)
        ]
        if cleaned:
            return "\n\n".join(cleaned[:3])

    text_history = re.search(
        r"History\s*[:\-]?\s*(.+?)(?:Contact|Courses|Placement|Fees|Infrastructure|$)",
        text_fallback,
        re.IGNORECASE,
    )
    if text_history:
        return re.sub(r"\s+", " ", text_history.group(1)).strip()[:1200]

    return "History information is currently unavailable from the live source."


def _pick_official_website(page_html, source_url):
    blocked_domains = {
        "vidyarthimitra.org",
        "facebook.com",
        "twitter.com",
        "x.com",
        "instagram.com",
        "youtube.com",
        "linkedin.com",
        "whatsapp.com",
        "api.whatsapp.com",
        "google.com",
        "goo.gl",
    }

    href_urls = re.findall(r"href=[\"\'](https?://[^\"\']+)[\"\']", page_html, re.IGNORECASE)
    raw_urls = re.findall(r"(?:https?://|www\.)[^\s<\"'\)]+", page_html, re.IGNORECASE)

    candidates = []
    for value in href_urls + raw_urls:
        cleaned = value.strip().strip(".,;)")
        if cleaned.startswith("www."):
            cleaned = f"https://{cleaned}"
        parsed = urlparse(cleaned)
        host = parsed.netloc.lower().replace("www.", "")
        if not host:
            continue
        if any(host == blocked or host.endswith(f".{blocked}") for blocked in blocked_domains):
            continue

        score = 0
        if any(token in host for token in [".edu", "ac.in", "edu.in"]):
            score += 6
        if host.endswith(".org"):
            score += 3
        if host.endswith(".in"):
            score += 2
        if host.endswith(".edu"):
            score += 2
        if "admission" in host or "apply" in host:
            score -= 1

        candidates.append((score, cleaned))

    if not candidates:
        return source_url

    candidates.sort(key=lambda item: item[0], reverse=True)
    return candidates[0][1]


def get_university_detail(slug):
    cached = UNIVERSITY_DETAIL_CACHE.get(slug)
    now = time.time()
    if cached and now - cached["fetched_at"] < UNIVERSITY_DETAIL_CACHE_SECONDS:
        return cached["detail"]

    source_url = f"{LIVE_UNIVERSITIES_URL}/{slug}"

    fallback_name = re.sub(r"\s+", " ", html.unescape(slug).replace("-", " ")).strip(" ,")
    detail = {
        "name": fallback_name,
        "location": "India",
        "type": "University",
        "nirf": "-",
        "phone": "Not available",
        "website": source_url,
        "address": "Not available",
        "history": "History information is currently unavailable from the live source.",
        "logo_url": "/static/logo.png",
        "source_url": source_url,
    }

    try:
        request = Request(source_url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(request, timeout=15) as response:
            page_html = response.read().decode("utf-8", errors="ignore")

        full_text = _clean_html_text(page_html)

        title_match = re.search(r"<h1[^>]*>(.*?)</h1>", page_html, re.IGNORECASE | re.DOTALL)
        if title_match:
            title_text = _clean_html_text(title_match.group(1))
            if title_text and not title_text.lower().startswith("top university"):
                detail["name"] = title_text

        contact_name_match = re.search(
            r"CONTACT\s+INFORMATION\s+([A-Za-z\s,\-.]{8,120})",
            full_text,
            re.IGNORECASE,
        )
        if contact_name_match:
            candidate = contact_name_match.group(1).strip(" -:,.")
            if candidate and "phone" not in candidate.lower() and "http" not in candidate.lower():
                detail["name"] = candidate.title()

        location_match = re.search(r"LOCATION\s+([A-Za-z\s\-]{2,60})\s+TYPE", full_text, re.IGNORECASE)
        if location_match:
            detail["location"] = location_match.group(1).strip().title()

        type_match = re.search(
            r"TYPE\s+([A-Za-z\s\-&/,]{3,100})\s+NIRF",
            full_text,
            re.IGNORECASE,
        )
        if type_match:
            detail["type"] = type_match.group(1).strip().title()

        nirf_match = re.search(r"NIRF(?:\s*\d{4})?\s*[:\-]?\s*(\d{1,3})", full_text, re.IGNORECASE)
        if nirf_match:
            detail["nirf"] = nirf_match.group(1)

        phone_match = re.search(r"(?:Phone|Tel|Telephone)\s*[:\-]?\s*(\+?\d[\d\s\-]{7,20})", full_text, re.IGNORECASE)
        if phone_match:
            detail["phone"] = re.sub(r"\s+", " ", phone_match.group(1)).strip()

        detail["website"] = _pick_official_website(page_html, source_url)

        address_match = re.search(r"Address\s*[:\-]?\s*([^\n\r]{10,220})", full_text, re.IGNORECASE)
        if address_match:
            detail["address"] = address_match.group(1).strip(" -:")
        else:
            detail["address"] = f"{detail['name']}, {detail['location']}"

        image_match = re.search(r"<img[^>]+src=[\"\']([^\"\']+)[\"\']", page_html, re.IGNORECASE)
        if image_match:
            detail["logo_url"] = urljoin(source_url, image_match.group(1))

        detail["history"] = _extract_history_text(page_html, full_text)
    except Exception:
        pass

    UNIVERSITY_DETAIL_CACHE[slug] = {
        "fetched_at": now,
        "detail": detail,
    }
    return detail


SECTION_CONTENT = {
    "universities": {
        "title": "Top Universities",
        "subtitle": "UGC recognized Government, Private and Deemed universities with admission-focused information.",
        "items": [
            "Search university profiles by state and stream.",
            "Check available programs and eligibility.",
            "Review key deadlines and admission notices.",
            "Compare options based on your career goal.",
        ],
    },
    "colleges": {
        "title": "Colleges Directory",
        "subtitle": "Explore institutes, branches, cut-off trends, and campus-level opportunities.",
        "items": [
            "Browse top colleges with key details.",
            "Compare branch options and seat insights.",
            "Track CAP and counselling driven selections.",
            "Shortlist colleges based on your rank.",
        ],
    },
    "courses": {
        "title": "Courses & Streams",
        "subtitle": "Find courses across Engineering, Medical, Law, Commerce, Arts, Management and more.",
        "items": [
            "Understand course structure and scope.",
            "Check entrance pathways per stream.",
            "Explore trending and career-oriented options.",
            "Map courses to your long-term goals.",
        ],
    },
    "exams": {
        "title": "Entrance Exams",
        "subtitle": "Latest updates for MHT-CET, JEE, NEET, CLAT, NDA and other major exams.",
        "items": [
            "Important dates and notification alerts.",
            "Syllabus, pattern and exam timelines.",
            "Application and counselling checkpoints.",
            "Result and merit list tracking support.",
        ],
    },
    "mock_exams": {
        "title": "Mock Exams",
        "subtitle": "Practice tests to evaluate preparation with guided improvement.",
        "items": [
            "Attempt exam-style practice papers.",
            "Understand strengths and weak areas.",
            "Track progress with regular testing.",
            "Prepare strategically before final exams.",
        ],
    },
    "epaper": {
        "title": "Epaper",
        "subtitle": "Education, admission and career updates in digital news format.",
        "items": [
            "Daily education sector highlights.",
            "Admission bulletins and policy updates.",
            "Exam and career guidance stories.",
            "Curated content for students and parents.",
        ],
    },
    "guide": {
        "title": "Guide Me",
        "subtitle": "Structured guidance for better decisions from exam stage to final admission.",
        "items": [
            "Step-by-step admission guidance.",
            "Decision support for branch selection.",
            "Career path suggestions by profile.",
            "Actionable checklists for each stage.",
        ],
    },
    "blog": {
        "title": "Blog",
        "subtitle": "Insights, explainers and expert articles on education and career planning.",
        "items": [
            "Student-friendly admission explainers.",
            "Career planning guides and strategies.",
            "Exam prep and productivity tips.",
            "Real-world guidance from experts.",
        ],
    },
    "news": {
        "title": "News",
        "subtitle": "Latest official and practical updates from education boards and institutions.",
        "items": [
            "Admission and counselling notices.",
            "Exam announcements and deadlines.",
            "Scholarship and policy updates.",
            "Trending student opportunities.",
        ],
    },
    "feedback": {
        "title": "Feedback",
        "subtitle": "Share your experience and help improve the platform for students.",
        "items": [
            "Submit platform suggestions.",
            "Report missing or incorrect information.",
            "Share counselling experience.",
            "Help us improve student support.",
        ],
    },
    "admissions": {
        "title": "Admissions",
        "subtitle": "Admission-focused section for application windows, eligibility and CAP process updates.",
        "items": [
            "Current admission openings.",
            "Eligibility criteria snapshots.",
            "Document and timeline readiness.",
            "Round-wise admission updates.",
        ],
    },
    "counselling": {
        "title": "Career Counselling",
        "subtitle": "Get guided counselling support for Mumbai, Pune and Virtual sessions.",
        "items": [
            "One-to-one profile discussion.",
            "Branch and college finalization help.",
            "Admission strategy by rank profile.",
            "Guidance for parents and students.",
        ],
    },
    "scholarship": {
        "title": "Scholarships",
        "subtitle": "Scholarship discovery and update section to support higher education journeys.",
        "items": [
            "Merit and category based options.",
            "Application timing and deadlines.",
            "Eligibility checkpoints and documents.",
            "Updates from verified sources.",
        ],
    },
    "dte": {
        "title": "DTE Updates",
        "subtitle": "Important DTE and State CET Cell notices simplified for students.",
        "items": [
            "CAP round and process updates.",
            "Option form and choice filling guidance.",
            "Deadline reminders and document alerts.",
            "Admission decisions with clarity.",
        ],
    },
}


def render_section(section_key):
    section = SECTION_CONTENT[section_key]
    return render_template("inner_page.html", section=section, section_key=section_key)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/universities")
def universities():
    live_universities = get_live_universities()
    city_options = sorted(
        {
            university["location"]
            for university in live_universities
            if university.get("location") and university["location"] != "India"
        }
    )
    type_options = sorted(
        {
            university["type"]
            for university in live_universities
            if university.get("type") and university["type"] != "Updated Live"
        }
    )
    return render_template(
        "universities.html",
        states=UNIVERSITY_STATES,
        cities=city_options,
        types=type_options,
        streams=DEFAULT_UNIVERSITY_STREAMS,
        universities=live_universities,
    )


@app.route("/universities/<path:slug>")
def university_detail(slug):
    detail = get_university_detail(slug)
    return render_template("university_detail.html", detail=detail)


@app.route("/colleges")
def colleges():
    data = get_live_colleges()
    return render_template(
        "colleges.html",
        states=data["states"],
        cities=data["cities"],
        types=data["types"],
        streams=data["streams"],
        colleges=data["colleges"],
    )


@app.route("/courses")
def courses():
    data = get_live_courses()
    return render_template(
        "courses.html",
        streams=data["streams"],
        courses=data["courses"],
    )


@app.route("/exams")
def exams():
    return render_section("exams")


@app.route("/entrance-exams")
def entrance_exams():
    return render_section("exams")


@app.route("/mock-exams")
def mock_exams():
    return render_section("mock_exams")


@app.route("/epaper")
def epaper():
    return render_template("epaper.html")


@app.route("/guide")
def guide():
    return render_section("guide")


@app.route("/blog")
def blog():
    return render_section("blog")


@app.route("/news")
def news():
    return render_template("news.html")


@app.route("/feedback")
def feedback():
    return render_section("feedback")


@app.route("/admissions")
def admissions():
    return render_template("admission.html")


@app.route("/counselling")
def counselling():
    return render_section("counselling")


@app.route("/scholarship")
def scholarship():
    return render_section("scholarship")


@app.route("/dte")
def dte():
    return render_section("dte")


# ============ AUTHENTICATION ROUTES ============

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@app.route("/login", methods=['GET', 'POST'])
def login():
    """Login page with Firebase authentication"""
    if request.method == 'GET':
        return render_template('login.html')
    
    # Handle login via API (JavaScript will call this)
    return jsonify({'status': 'success'})


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    """Signup page with Firebase authentication"""
    if request.method == 'GET':
        return render_template('signup.html')
    
    # Handle signup via API (JavaScript will call this)
    return jsonify({'status': 'success'})



# Terms and Conditions route
@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/logout", methods=['GET'])
def logout():
    """Logout user"""
    session.clear()
    return redirect(url_for('index'))


@app.route("/auth/set-user", methods=['POST'])
def set_user():
    """Set user session after Firebase authentication"""
    try:
        data = request.get_json()
        user = data.get('user')
        
        if user and user.get('uid'):
            session['user'] = {
                'uid': user.get('uid'),
                'email': user.get('email'),
                'name': user.get('displayName', ''),
                'photo': user.get('photoURL', '/static/default-avatar.png'),
            }
            return jsonify({'status': 'success', 'message': 'User logged in'}), 200
        
        return jsonify({'status': 'error', 'message': 'Invalid user data'}), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route("/auth/get-user", methods=['GET'])
def get_user():
    """Get current user from session"""
    if 'user' in session:
        return jsonify({'user': session['user']}), 200
    return jsonify({'user': None}), 200


@app.route("/auth/check-auth", methods=['GET'])
def check_auth():
    """Check if user is authenticated"""
    return jsonify({'authenticated': 'user' in session}), 200


@app.errorhandler(404)
def not_found(error):
    return render_template("not_found.html"), 404


if __name__ == "__main__":
    app.run(debug=True)

