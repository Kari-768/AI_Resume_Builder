import os
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from docx import Document
import pdfplumber

app = Flask(__name__, template_folder="templates")

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ======================================================
# 1. READ ANY RESUME (PDF / DOCX / TXT)
# ======================================================
def extract_text(filepath):
    text = ""
    if filepath.lower().endswith(".pdf"):
        with pdfplumber.open(filepath) as pdf:
            for page in pdf.pages:
                if page.extract_text():
                    text += page.extract_text() + "\n"
    elif filepath.lower().endswith(".docx"):
        doc = Document(filepath)
        for p in doc.paragraphs:
            if p.text.strip():
                text += p.text + "\n"
    else:
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
    return text.strip()

# ======================================================
# 2. UNIVERSAL SECTION DETECTION (TEMPLATE-INDEPENDENT)
# ======================================================
KNOWN_HEADINGS = [
    "professional summary", "summary", "education",
    "technical skills", "skills", "projects",
    "certifications", "internships", "internship",
    "experience", "soft skills", "languages", "hobbies"
]

def extract_section(text, headings):
    lines = text.splitlines()
    capture = False
    content = []

    for line in lines:
        clean = line.strip().lower()

        if clean in headings:
            capture = True
            continue

        if capture and clean in KNOWN_HEADINGS:
            break

        if capture and line.strip():
            content.append(line.strip())

    return "\n".join(content).strip()

# ======================================================
# 3. FALLBACK KEYWORD EXTRACTION (WHEN HEADINGS MISSING)
# ======================================================
def keyword_extract(text, keywords, max_lines=3):
    results = []
    for line in text.splitlines():
        if any(k in line.lower() for k in keywords):
            if len(line.split()) > 3:
                results.append(line.strip())
        if len(results) >= max_lines:
            break
    return "\n".join(results)

# ======================================================
# 4. INTERNSHIP EXTRACTION (SPECIAL CASE)
# ======================================================
def extract_internships(text):
    lines = [l.strip() for l in text.splitlines() if l.strip()]
    results = []

    for i, line in enumerate(lines):
        if "intern" in line.lower():
            block = line
            if i + 1 < len(lines) and "(" in lines[i + 1]:
                block += " " + lines[i + 1]
            results.append(block)

    return "\n".join(results)

# ======================================================
# 5. NORMALIZE CERTIFICATIONS
# ======================================================
def normalize_certifications(text):
    if not text:
        return ""
    if "|" in text:
        return "\n".join(f"- {x.strip()}" for x in text.split("|") if x.strip())
    return text

# ======================================================
# 6. EXTRACT ALL SECTIONS (UNIVERSAL LOGIC)
# ======================================================
def extract_sections(text):
    return {
        "summary": extract_section(text, ["professional summary", "summary"])
                   or keyword_extract(text, ["graduate", "developer"]),

        "education": extract_section(text, ["education"])
                   or keyword_extract(text, ["degree", "college", "university"]),

        "skills": extract_section(text, ["technical skills", "skills"])
                   or keyword_extract(text, ["python", "java", "sql", "html"]),

        "projects": extract_section(text, ["projects"])
                   or keyword_extract(text, ["project", "application"]),

        "certifications": extract_section(text, ["certifications"])
                   or keyword_extract(text, ["certification", "course"]),

        "internships": extract_section(text, ["internships", "internship", "experience"])
                   or extract_internships(text),

        "soft_skills": extract_section(text, ["soft skills"])
                   or keyword_extract(text, ["communication", "teamwork"]),

        "languages": extract_section(text, ["languages"])
                   or keyword_extract(text, ["english", "telugu", "hindi", "urdu"]),
    }

# ======================================================
# 7. BUILD UNIVERSAL RESUME (FIXED OUTPUT FORMAT)
# ======================================================
def build_resume(text):
    s = extract_sections(text)

    resume = f"""
KARISHMA NOORBHASHA
Email: karishma7659904757@gmail.com | Phone: +91 9666189925 | Guntur
LinkedIn: linkedin.com/in/nb-karishma-b06b1a2a1 | GitHub: github.com/kari7865
Portfolio: kari7865.github.io/KARISHMARESUME
"""

    ORDER = [
        ("Professional Summary", "summary"),
        ("Education", "education"),
        ("Technical Skills", "skills"),
        ("Projects", "projects"),
        ("Certifications", "certifications"),
        ("Internships", "internships"),
        ("Soft Skills", "soft_skills"),
        ("Languages", "languages"),
    ]

    for title, key in ORDER:
        if s[key]:
            content = normalize_certifications(s[key]) if title == "Certifications" else s[key]
            resume += f"\n{title}\n{content}\n"

    return resume.strip()

# ======================================================
# 8. HTML RENDERING (FIXED UNIVERSAL DESIGN)
# ======================================================
def format_html(text):
    headers = {
        "Professional Summary", "Education", "Technical Skills",
        "Projects", "Certifications", "Internships",
        "Soft Skills", "Languages"
    }

    html = ""
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    html += f"<h2 style='text-align:center'>{lines[0]}</h2>"

    i = 1
    while i < len(lines):
        if lines[i] in headers:
            html += f"<h3>{lines[i]}</h3>"
            i += 1
            while i < len(lines) and lines[i] not in headers:
                if lines[i].startswith("- "):
                    html += f"<li>{lines[i][2:]}</li>"
                else:
                    html += f"<p>{lines[i]}</p>"
                i += 1
        else:
            i += 1

    return html

# ======================================================
# 9. ROUTES
# ======================================================
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["resume"]
    path = os.path.join(UPLOAD_FOLDER, secure_filename(file.filename))
    file.save(path)

    resume_text = extract_text(path)
    final_resume = build_resume(resume_text)

    return render_template(
        "result.html",
        resume=format_html(final_resume),
        raw_text=final_resume
    )

@app.route("/download", methods=["POST"])
def download():
    path = os.path.join(OUTPUT_FOLDER, "Universal_Resume.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write(request.form["resume_text"])
    return send_file(path, as_attachment=True)

if __name__ == "__main__":
    app.run(debug=False)