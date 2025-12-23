import requests
from twilio.rest import Client
from datetime import datetime
import os

# ======================
# SAFE LOGGING (CLOUD)
# ======================
def log(msg):
    print(f"[{datetime.now()}] {msg}")

log("===== SCRIPT STARTED =====")

# ======================
# READ SECRETS (CLOUD)
# ======================
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

FROM_WHATSAPP = "whatsapp:+14155238886"
TO_WHATSAPP = "whatsapp:+919606429957"

# ======================
# VALIDATION
# ======================
if not all([ADZUNA_APP_ID, ADZUNA_APP_KEY, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN]):
    raise RuntimeError("❌ Missing environment variables (Secrets not loaded)")

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

def is_entry_level(text):
    text = text.lower()
    return any(i in text for i in INCLUDE_KEYWORDS) and not any(e in text for e in EXCLUDE_KEYWORDS)

# ======================
# FETCH JOBS
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
    raw_jobs = response.json().get("results", [])
    log(f"Fetched {len(raw_jobs)} jobs")

except Exception as e:
    log(f"ERROR fetching jobs: {e}")
    raw_jobs = []

# ======================
# FILTER ENTRY LEVEL
# ======================
filtered_jobs = []
for job in raw_jobs:
    combined = f"{job.get('title','')} {job.get('description','')}"
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
    log("✅ WhatsApp message sent")

except Exception as e:
    log(f"❌ WhatsApp send error: {e}")

log("===== SCRIPT FINISHED =====")
