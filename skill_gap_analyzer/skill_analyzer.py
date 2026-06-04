import json
import os
from groq import Groq

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

CACHE_FILE = "role_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=4)

def get_required_skills(role):
    role = role.lower().strip()

    cache = load_cache()
    if role in cache:
        return cache[role]

    prompt = f"""You are a tech career advisor.
List the top 8 key technical skills required for the job role: "{role}".
Return ONLY this JSON, no explanation, no markdown backticks:
{{"required_skills": ["skill1", "skill2", "skill3"]}}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=200,
        temperature=0.3
    )

    text = response.choices[0].message.content.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    skills = [s.lower().strip() for s in json.loads(text)["required_skills"]]

    cache[role] = skills
    save_cache(cache)
    return skills

def analyze_skill_gap(role: str, user_skills: list) -> dict:
    role = role.lower().strip()
    required = get_required_skills(role)
    user_set = {s.lower().strip() for s in user_skills}

    have    = [s for s in required if s in user_set]
    missing = [s for s in required if s not in user_set]
    score   = int(len(have) / len(required) * 100) if required else 0

    return {"have": have, "missing": missing, "score": score}
