import re
import spacy
import pdfplumber
import docx  # pip install python-docx
from spacy.matcher import PhraseMatcher

nlp = spacy.load("en_core_web_sm")

SKILL_ALIASES = {
    "ml":   "machine learning",
    "dl":   "deep learning",
    "ai":   "artificial intelligence",
    "js":   "javascript",
    "py":   "python",
    "tf":   "tensorflow",
    "nlp":  "natural language processing",
    "cv":   "computer vision",
    "oop":  "object oriented programming",
    "dsa":  "data structures",
    "cicd": "ci/cd",
    "k8s":  "kubernetes",
}

KNOWN_SKILLS = [
    "python", "java", "sql", "javascript", "html", "css", "c++", "r",
    "machine learning", "deep learning", "artificial intelligence",
    "natural language processing", "computer vision", "statistics",
    "tensorflow", "pytorch", "scikit-learn", "keras",
    "pandas", "numpy", "data visualization", "excel", "tableau", "power bi",
    "react", "flask", "django", "api", "rest api", "node.js",
    "docker", "kubernetes", "aws", "azure", "gcp", "linux", "git",
    "ci/cd", "networking", "cloud", "database", "mongodb", "postgresql", "mysql",
    "network security", "cryptography", "ethical hacking",
    "object oriented programming", "data structures", "ui design",
]

_matcher = PhraseMatcher(nlp.vocab, attr="LOWER")
_matcher.add("SKILLS", [nlp.make_doc(s) for s in KNOWN_SKILLS])


def extract_text_from_pdf(filepath: str) -> str:
    text = ""
    with pdfplumber.open(filepath) as pdf:
        for page in pdf.pages:
            text += page.extract_text() or ""
    return text


def extract_text_from_docx(filepath: str) -> str:
    doc = docx.Document(filepath)
    return " ".join(para.text for para in doc.paragraphs)


def extract_text_from_txt(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return f.read()


def extract_text(filepath: str) -> str:
    """Auto-detect file type and extract text."""
    ext = filepath.rsplit(".", 1)[-1].lower()
    if ext == "pdf":
        return extract_text_from_pdf(filepath)
    elif ext == "docx":
        return extract_text_from_docx(filepath)
    elif ext == "txt":
        return extract_text_from_txt(filepath)
    else:
        return ""  # unsupported type


def _normalize(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[^\w\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    for short, full in SKILL_ALIASES.items():
        text = re.sub(r"\b" + re.escape(short) + r"\b", full, text)
    return text


def extract_skills(text: str) -> list[str]:
    doc = nlp(_normalize(text))
    matches = _matcher(doc)
    found = {doc[s:e].text.lower() for _, s, e in matches}
    return sorted(found)


def extract_skills_from_text_input(raw_input: str) -> list[str]:
    cleaned = raw_input.replace(",", " ")
    return extract_skills(cleaned)