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
# LOAD SEEN JOBS (DUPLICATE PREVENTION)
# ======================
SEEN_FILE = "seen_jobs.txt"
seen_jobs = set()

if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r") as f:
        seen_jobs = set(f.read().splitlines())

log(f"Loaded {len(seen_jobs)} seen jobs")

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
# FILTER NEW ENTRY-LEVEL JOBS ONLY
# ======================
new_jobs = []

for job in raw_jobs:
    job_id = job.get("id")
    combined = f"{job.get('title','')} {job.get('description','')}"

    if job_id and job_id not in seen_jobs and is_entry_level(combined):
        new_jobs.append(job)
        seen_jobs.add(job_id)

log(f"New jobs found: {len(new_jobs)}")

# ======================
# SEND WHATSAPP FOR NEW JOBS
# ======================
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

for job in new_jobs:
    message_body = (
        "🚨 NEW JOB JUST POSTED\n\n"
        f"Role: {job.get('title','N/A')}\n"
        f"Company: {job.get('company',{}).get('display_name','N/A')}\n"
        f"Location: {job.get('location',{}).get('display_name','India')}\n\n"
        f"Apply now:\n{job.get('redirect_url','')}"
    )

    try:
        client.messages.create(
            from_=FROM_WHATSAPP,
            to=TO_WHATSAPP,
            body=message_body
        )
        log("✅ WhatsApp sent for new job")

    except Exception as e:
        log(f"❌ WhatsApp send error: {e}")

# ======================
# SAVE SEEN JOBS
# ======================
with open(SEEN_FILE, "w") as f:
    f.write("\n".join(seen_jobs))

log("===== SCRIPT FINISHED =====")
