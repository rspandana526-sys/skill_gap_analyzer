# 🎯 Skill Gap Analyzer

An AI-powered web app that analyzes your skills against job roles, identifies gaps, and gives personalized learning recommendations.

---

## Team Members

Ajmeera Mounika
Naramamidi Dhaarni Sri
Korlapati Maheswari
Malavath Vaishnavi 
Spandana Reddy

## Project Guide 

Ms S Lavanya Reddy

## ✨ Features

- 📄 Upload resume (PDF / DOCX / TXT) or type skills manually
- 🎯 Get a skill match score for any tech role
- 📚 Missing skills mapped to free YouTube courses
- 🤖 AI resume feedback via Groq (Llama 3.3)
- 💬 AI career chatbot
- 📝 Mock interview questions generator
- ✉️ Cover letter generator
- 📊 Analysis history & profile dashboard

---

## 🚀 Run Locally

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/skill-gap-analyzer.git
cd skill-gap-analyzer
```

### 2. Create a virtual environment
```bash
python -m venv venv
source venv/bin/activate      # Mac/Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Set up environment variables
```bash
cp .env.example .env
```
Edit `.env` and add your **Groq API key** (free at https://console.groq.com):
```
GROQ_API_KEY=your_key_here
SECRET_KEY=any_random_string
```

### 5. Run the app
```bash
python app.py
```
Visit http://localhost:5000 — the SQLite database is created automatically on first run.

---

## ☁️ Deploy to Render (Free)

1. Push this repo to GitHub
2. Go to https://render.com → **New Web Service**
3. Connect your GitHub repo
4. Set **Start Command**: `gunicorn app:app`
5. Add **Environment Variables** in the Render dashboard:
   - `GROQ_API_KEY` → your Groq key
   - `SECRET_KEY` → any random string (e.g. `abc123xyz`)
6. Click **Deploy** ✅

> The SQLite database file is created automatically. No MySQL or external DB needed.

---

## ☁️ Deploy to Railway

1. Push to GitHub
2. Go to https://railway.app → **New Project → Deploy from GitHub**
3. Add the same environment variables listed above
4. Railway auto-detects the `Procfile` and deploys ✅

---

## 🔑 Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | ✅ Yes | Get free at console.groq.com |
| `SECRET_KEY` | ✅ Yes | Any random string for Flask sessions |
| `FAST2SMS_API_KEY` | ❌ Optional | Only needed for OTP via SMS |

---

## 🛠 Tech Stack

- **Backend**: Python, Flask, SQLite
- **AI**: Groq API (Llama 3.3 70B)
- **Resume Parsing**: pdfplumber, python-docx, spaCy
- **Frontend**: HTML, CSS, Vanilla JS
