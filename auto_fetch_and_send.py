import requests
from twilio.rest import Client
from datetime import datetime
import os
import sys

# ======================
# LOGGING (CRITICAL FOR SCHEDULER)
# ======================
BASE_DIR = r"C:\Users\sande\OneDrive\Desktop\twilio_whatsapp"
LOG_FILE = os.path.join(BASE_DIR, "task_log.txt")

def log(msg):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {msg}\n")

log("===== SCRIPT STARTED =====")
log(f"Python: {sys.executable}")
log(f"Working Dir: {os.getcwd()}")

# ======================
# ADZUNA CONFIG
# ======================
ADZUNA_APP_ID = "bd632827"
ADZUNA_APP_KEY = "65f164fc7fceeea66049b21021c4dedc"

# ======================
# TWILIO CONFIG
# ======================
TWILIO_ACCOUNT_SID = "AC0fa5b42d5365035840a3c42e130e55ea"
TWILIO_AUTH_TOKEN = "7cc94c43881ce9a26293ddd147947ff2"

FROM_WHATSAPP = "whatsapp:+14155238886"
TO_WHATSAPP = "whatsapp:+919606429957"

# ======================
# STRICT ENTRY-LEVEL RULES
# ======================
INCLUDE_KEYWORDS = [
    "entry", "fresher", "graduate", "intern",
    "trainee", "associate", "sde-1", "sde i", "junior"
]

EXCLUDE_KEYWORDS = [
    "senior", "lead", "principal", "staff",
    "manager", "architect", "sr", "ii", "iii", "3+"
]

def is_entry_level(text: str) -> bool:
    text = text.lower()
    return any(i in text for i in INCLUDE_KEYWORDS) and not any(e in text for e in EXCLUDE_KEYWORDS)

# ======================
# FETCH JOBS (SAFE)
# ======================
url = "https://api.adzuna.com/v1/api/jobs/in/search/1"

params = {
    "app_id": ADZUNA_APP_ID,
    "app_key": ADZUNA_APP_KEY,
    "results_per_page": 15,
    "what": "software engineer OR software developer OR sde",
    "where": "Bangalore OR Bengaluru OR Chennai OR Hyderabad"
}

try:
    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()
    data = response.json()
    raw_jobs = data.get("results", [])
    log(f"Fetched {len(raw_jobs)} jobs from Adzuna")

except Exception as e:
    log(f"ERROR fetching jobs: {e}")
    raw_jobs = []

# ======================
# FILTER ENTRY-LEVEL ONLY
# ======================
filtered_jobs = []

for job in raw_jobs:
    title = job.get("title", "")
    description = job.get("description", "")
    combined = f"{title} {description}"

    if is_entry_level(combined):
        filtered_jobs.append(job)

log(f"Filtered to {len(filtered_jobs)} entry-level jobs")

# ======================
# BUILD MESSAGE
# ======================
if filtered_jobs:
    message_body = "🔥 Fresher / Entry-Level Software Jobs (India)\n\n"
    message_body += f"Found {len(filtered_jobs)} job(s):\n\n"

    for i, job in enumerate(filtered_jobs, 1):
        message_body += (
            f"{i}. {job.get('title','N/A')}\n"
            f"Company: {job.get('company',{}).get('display_name','N/A')}\n"
            f"Location: {job.get('location',{}).get('display_name','India')}\n"
            f"Apply: {job.get('redirect_url','')}\n\n"
        )
else:
    message_body = (
        "🔥 Fresher / Entry-Level Software Jobs (India)\n\n"
        "No new verified fresher or entry-level jobs today.\n\n"
        "Priority Cities:\n"
        "• Bangalore\n• Chennai\n• Hyderabad\n\n"
        "— Auto Job Alert"
    )

# ======================
# SEND WHATSAPP
# ======================
try:
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(
        from_=FROM_WHATSAPP,
        to=TO_WHATSAPP,
        body=message_body
    )
    log("WhatsApp message sent successfully")

except Exception as e:
    log(f"ERROR sending WhatsApp: {e}")

log("===== SCRIPT FINISHED =====\n")
