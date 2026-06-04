from flask import Flask, render_template, request, redirect, session, jsonify
import os
from groq import Groq

from skill_analyzer import analyze_skill_gap, get_required_skills
from resume_parser import extract_text, extract_skills, extract_skills_from_text_input
from database import (init_db, save_history, get_history, clear_history,
                      delete_history_item, get_total_analyses, change_password,
                      get_learned_skills, save_learned_skills)
from config import UPLOAD_FOLDER
from auth import save_user, validate_user, verify_current_password

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "skillgap_secret_123")

init_db()

app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {"pdf", "docx", "txt"}
groq_client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

COURSE_LINKS = {
    "python":                                               "https://youtu.be/rfscVS0vtbw",
    "r":                                                    "https://youtu.be/_V8eKsto3Ug",
    "java":                                                 "https://youtu.be/eIrMbAQSU34",
    "node.js":                                              "https://youtu.be/fBNz5xF-Kx4",
    "express":                                              "https://youtu.be/L72fhGm1tfE",
    "django":                                               "https://youtu.be/rHux0gMZ3Eg",
    "flask":                                                "https://youtu.be/Z1RJmh_OqeA",
    "html":                                                 "https://youtu.be/UB1O30fR-EE",
    "css":                                                  "https://youtu.be/1PnVor36_40",
    "html/css":                                             "https://youtu.be/G3e-cpL7ofc",
    "javascript":                                           "https://youtu.be/8ext9G7xspg",
    "react":                                                "https://youtu.be/bMknfKXIFA8",
    "angular":                                              "https://youtu.be/3qBXWUpoPHo",
    "vue.js":                                               "https://youtu.be/FXpIoQ_rT_c",
    "bootstrap":                                            "https://youtu.be/-qfEOE4vtxE",
    "responsive web design":                                "https://youtu.be/srvUrASNj0s",
    "css preprocessors like sass or less":                  "https://youtu.be/Zz6eOVaaelI",
    "sql":                                                  "https://youtu.be/ua-CiDNNj30",
    "mysql":                                                "https://youtu.be/oeYBdghaIjc",
    "mongodb":                                              "https://youtu.be/c2M-rlkkT5o",
    "database management systems like mysql or mongodb":    "https://youtu.be/oeYBdghaIjc",
    "excel":                                                "https://youtu.be/Vl0H-qTclOg",
    "tableau":                                              "https://youtu.be/aHaOIvR00So",
    "machine learning":                                     "https://youtu.be/aircAruvnKk",
    "deep learning":                                        "https://youtu.be/7eh4d6sabA0",
    "natural language processing":                          "https://youtu.be/8rXD5-xhemo",
    "computer vision":                                      "https://youtu.be/01sAkU_NvOY",
    "tensorflow":                                           "https://youtu.be/tPYj3fFJGjk",
    "pytorch":                                              "https://youtu.be/IC0_FRiX-sw",
    "keras":                                                "https://youtu.be/qFJeN9V1ZsI",
    "scikit-learn":                                         "https://youtu.be/0B5eIE_1vpU",
    "statistics":                                           "https://youtu.be/xxpc-HPKN28",
    "data visualization":                                   "https://youtu.be/GPVsHOlRBBI",
    "data mining":                                          "https://youtu.be/gMPeRJIXo5A",
    "data preprocessing":                                   "https://youtu.be/7moa-xy-1Co",
    "aws":                                                  "https://youtu.be/k1RI5locZE4",
    "aws or azure or google cloud":                         "https://youtu.be/k1RI5locZE4",
    "docker":                                               "https://youtu.be/3c-iBn73dDE",
    "containerization using docker":                        "https://youtu.be/3c-iBn73dDE",
    "kubernetes":                                           "https://youtu.be/X48VuDVv0do",
    "git":                                                  "https://youtu.be/RGOj5yH7evk",
    "linux":                                                "https://youtu.be/ROjZy1WbCIA",
    "infrastructure as code using terraform or cloudformation": "https://youtu.be/SLB_c_ayRMo",
    "networking fundamentals":                              "https://youtu.be/qiQR5rTSshw",
    "security and compliance":                              "https://youtu.be/3QhU9jd03a0",
    "monitoring and logging tools like prometheus or splunk": "https://youtu.be/h4Sl21AKiDg",
    "scripting languages like python or powershell":        "https://youtu.be/rfscVS0vtbw",
    "network security":                                     "https://youtu.be/3QhU9jd03a0",
    "api":                                                  "https://youtu.be/GZvSYJDk-us",
    "api design and development using rest or graphql":     "https://youtu.be/GZvSYJDk-us",
    "server-side frameworks like express or django":        "https://youtu.be/L72fhGm1tfE",
    "version control systems like git":                     "https://youtu.be/RGOj5yH7evk",
    "cloud platforms such as aws or azure":                 "https://youtu.be/k1RI5locZE4",
    "testing frameworks like junit or pyunit":              "https://youtu.be/byHcYRpMgI4",
    "programming languages such as java or python":         "https://youtu.be/eIrMbAQSU34",
    "solidity":                                             "https://youtu.be/ipwxYa-F1uY",
    "smart contract development":                           "https://youtu.be/M576WGiDBdQ",
    "ethereum":                                             "https://youtu.be/jYEqoIeAoBg",
    "hyperledger":                                          "https://youtu.be/7EpLxOfeBEM",
    "cryptographic algorithms":                             "https://youtu.be/AQDCe585Lnc",
    "blockchain architecture":                              "https://youtu.be/SSo_EIwHSd4",
    "web3.js":                                              "https://youtu.be/t3wM5903ty0",
}

COMMON_ROLES = [
    "data scientist", "frontend developer", "backend developer",
    "full stack developer", "machine learning engineer", "ai engineer",
    "cloud engineer", "data analyst", "blockchain developer", "devops engineer"
]

# ── LOGIN ──────────────────────────────────────────

@app.route("/", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = request.form.get("remember")
        if validate_user(username, password):
            session["username"] = username
            if remember:
                session.permanent = True
            return redirect("/home")
        else:
            error = "Invalid username or password"
    return render_template("login.html", error=error)

# ── SIGNUP WITH OTP ────────────────────────────────

@app.route("/register", methods=["GET", "POST"])
def signup():
    error = None

    if request.method == "POST":
        username         = request.form.get("username", "").strip()
        password         = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username or not password:
            error = "Username and password are required."
            return render_template("signup.html", error=error)

        if len(password) < 4:
            error = "Password must be at least 4 characters."
            return render_template("signup.html", error=error)

        if password != confirm_password:
            error = "Passwords do not match."
            return render_template("signup.html", error=error)

        result = save_user(username, password, email=None, phone=None)

        if result is True:
            return redirect("/login")
        elif result == 'dup':
            error = "Username already taken. Please choose a different one."
            return render_template("signup.html", error=error)
        else:
            error = "Registration failed. Please try again."
            return render_template("signup.html", error=error)

    return render_template("signup.html")

# ── LOGOUT ─────────────────────────────────────────

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")

# ── HOME ───────────────────────────────────────────

@app.route("/home")
def home():
    if "username" not in session:
        return redirect("/login")
    return render_template("home.html", username=session["username"])

# ── PROFILE ────────────────────────────────────────

@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect("/login")
    username = session["username"]
    total    = get_total_analyses(username)
    history  = get_history(username)
    best     = max(history, key=lambda x: x["score"]) if history else None
    return render_template("profile.html",
        username=username,
        total=total,
        best=best
    )

# ── CHANGE PASSWORD ────────────────────────────────

@app.route("/change-password", methods=["POST"])
def change_pw():
    if "username" not in session:
        return redirect("/login")
    username   = session["username"]
    current_pw = request.form.get("current_password")
    new_pw     = request.form.get("new_password")
    confirm_pw = request.form.get("confirm_password")

    if not verify_current_password(username, current_pw):
        return render_template("profile.html",
            username=username, total=get_total_analyses(username),
            best=None, pw_error="Current password is incorrect.")
    if new_pw != confirm_pw:
        return render_template("profile.html",
            username=username, total=get_total_analyses(username),
            best=None, pw_error="New passwords do not match.")
    if len(new_pw) < 4:
        return render_template("profile.html",
            username=username, total=get_total_analyses(username),
            best=None, pw_error="Password must be at least 4 characters.")

    change_password(username, new_pw)
    return render_template("profile.html",
        username=username, total=get_total_analyses(username),
        best=None, pw_success="Password changed successfully!")

# ── ANALYZE ────────────────────────────────────────

@app.route("/analyze", methods=["GET", "POST"])
def analyze():
    if "username" not in session:
        return redirect("/login")

    if request.method == "POST":
        role         = request.form.get("role", "").strip()
        skills_input = request.form.get("skills")
        user_skills  = []

        if skills_input:
            user_skills = extract_skills_from_text_input(skills_input)

        file = request.files.get("resume")
        resume_text = ""
        if file and file.filename != "":
            ext = file.filename.rsplit(".", 1)[-1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                return render_template("analyze.html", error="Unsupported file. Upload PDF, DOCX, or TXT.")
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)
            resume_text   = extract_text(filepath)
            resume_skills = extract_skills(resume_text)
            user_skills   = sorted(set(user_skills) | set(resume_skills))

        result = analyze_skill_gap(role, user_skills)
        save_history(session["username"], role, result["score"], result["missing"])

        all_role_scores = {}
        for r in COMMON_ROLES:
            r_result = analyze_skill_gap(r, user_skills)
            all_role_scores[r.title()] = r_result["score"]
        top3 = sorted(all_role_scores.items(), key=lambda x: x[1], reverse=True)[:3]

        resume_feedback = None
        if resume_text:
            try:
                fb = groq_client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are an expert resume reviewer. Give 4-5 short, specific bullet-point improvements for the resume. Be direct and practical. Format as bullet points starting with •"},
                        {"role": "user", "content": f"Review this resume and suggest improvements:\n\n{resume_text[:3000]}"}
                    ],
                    max_tokens=400,
                    temperature=0.7
                )
                resume_feedback = fb.choices[0].message.content
            except Exception as e:
                resume_feedback = "• Could not generate feedback. Please check your Groq API key."

        learned      = get_learned_skills(session["username"])
        course_links = {skill: COURSE_LINKS[skill] for skill in result["missing"] if skill in COURSE_LINKS}

        return render_template(
            "dashboard.html",
            role            = role,
            score           = result["score"],
            have            = result["have"],
            missing         = result["missing"],
            courses         = course_links,
            top3            = top3,
            resume_feedback = resume_feedback,
            learned         = learned,
            suggestion      = "",
            description     = f"Here is your personalised learning roadmap for {role}."
        )

    return render_template("analyze.html")

# ── LEARNED SKILLS ─────────────────────────────────

@app.route("/learned", methods=["POST"])
def learned():
    if "username" not in session:
        return jsonify({"error": "not logged in"}), 401
    data   = request.get_json()
    skills = data.get("skills", [])
    save_learned_skills(session["username"], skills)
    return jsonify({"ok": True})

# ── ROLE MATCH ─────────────────────────────────────

@app.route("/role-match", methods=["POST"])
def role_match():
    if "username" not in session:
        return jsonify({"error": "not logged in"}), 401
    data        = request.get_json()
    user_skills = data.get("skills", [])
    all_scores  = {}
    for r in COMMON_ROLES:
        r_result = analyze_skill_gap(r, user_skills)
        all_scores[r.title()] = r_result["score"]
    top3 = sorted(all_scores.items(), key=lambda x: x[1], reverse=True)[:3]
    return jsonify({"top3": top3})

# ── HISTORY ────────────────────────────────────────

@app.route("/history")
def history():
    if "username" not in session:
        return redirect("/login")
    return render_template("history.html", history=get_history(session["username"]))

@app.route("/clear")
def clear():
    if "username" not in session:
        return redirect("/login")
    clear_history(session["username"])
    return redirect("/history")

@app.route("/delete/<int:index>")
def delete(index):
    if "username" not in session:
        return redirect("/login")
    delete_history_item(session["username"], index)
    return redirect("/history")

# ── CHAT ───────────────────────────────────────────

@app.route("/chat")
def chat():
    if "username" not in session:
        return redirect("/login")
    return render_template("chat.html")

@app.route("/chat/send", methods=["POST"])
def chat_send():
    data     = request.get_json()
    messages = data.get("messages", [])
    if not messages:
        return jsonify({"error": "No messages"}), 400
    try:
        response = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role":"system","content":"You are a helpful AI career advisor specialising in tech careers, skills, learning paths, and job preparation. Be concise, friendly and practical."}] + messages,
            max_tokens=500,
            temperature=0.7
        )
        return jsonify({"reply": response.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── MOCK INTERVIEW ─────────────────────────────────

@app.route("/mock-interview", methods=["POST"])
def mock_interview():
    if "username" not in session:
        return jsonify({"error": "not logged in"}), 401
    data = request.get_json()
    role = data.get("role", "Software Developer")
    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are an expert technical interviewer. Generate exactly 7 realistic interview questions for the given role. Mix behavioural, technical, and situational questions. Number them 1-7. Be concise and direct."},
                {"role": "user", "content": f"Generate 7 interview questions for a {role} position."}
            ],
            max_tokens=600,
            temperature=0.8
        )
        return jsonify({"questions": resp.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── COVER LETTER ────────────────────────────────────

@app.route("/cover-letter", methods=["POST"])
def cover_letter():
    if "username" not in session:
        return jsonify({"error": "not logged in"}), 401
    data       = request.get_json()
    role       = data.get("role", "Software Developer")
    skills     = data.get("skills", [])
    skills_str = ", ".join(skills) if skills else "various technical skills"
    try:
        resp = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a professional cover letter writer. Write a compelling, concise cover letter (3 short paragraphs). Keep it under 250 words. Make it sound human, confident, and specific to the role. Don't use placeholder brackets - make reasonable assumptions."},
                {"role": "user", "content": f"Write a cover letter for a {role} position. My skills include: {skills_str}."}
            ],
            max_tokens=500,
            temperature=0.75
        )
        return jsonify({"letter": resp.choices[0].message.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ── RUN ────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True)