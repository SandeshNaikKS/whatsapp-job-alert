import requests
from twilio.rest import Client
from datetime import datetime
import os

def log(msg):
    print(f"[{datetime.now()}] {msg}")

log("===== SCRIPT STARTED =====")

# ===== Secrets =====
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

FROM_WHATSAPP = "whatsapp:+14155238886"
TO_WHATSAPP = "whatsapp:+919606429957"

if not all([ADZUNA_APP_ID, ADZUNA_APP_KEY, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN]):
    raise RuntimeError("Missing secrets")

# ===== JOB TITLES (YOUR LIST) =====
JOB_TITLES = [
    "software engineer i","associate software engineer","junior software engineer",
    "graduate software engineer","entry level software engineer","trainee software engineer",
    "software developer fresher","software engineer new grad","software engineer campus hire",
    "software engineer 0-1 years","junior full stack developer","associate full stack engineer",
    "web developer fresher","frontend developer junior","backend developer junior",
    "react developer fresher","java developer fresher","python developer fresher",
    "software developer intern","full stack intern","backend intern","frontend intern",
    "python intern","java intern","engineering trainee","graduate trainee engineer","gte",
    "associate cloud engineer","junior devops engineer","cloud support engineer fresher",
    "site reliability engineer trainee","platform engineer junior",
    "junior data analyst","data analyst fresher","associate data engineer",
    "junior machine learning engineer","ai engineer trainee","python data intern",
    "qa engineer fresher","junior test engineer","software tester entry level",
    "automation test engineer trainee","quality analyst junior"
]

def is_target_job(text):
    text = text.lower()
    return any(t in text for t in JOB_TITLES)

# ===== LOAD SEEN JOBS =====
SEEN_FILE = "seen_jobs.txt"
seen_jobs = set()

if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r") as f:
        seen_jobs = set(f.read().splitlines())

# ===== FETCH JOBS =====
url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
params = {
    "app_id": ADZUNA_APP_ID,
    "app_key": ADZUNA_APP_KEY,
    "results_per_page": 20,
    "what": "software",
    "where": "Bangalore OR Bengaluru OR Chennai OR Hyderabad"
}

jobs = requests.get(url, params=params, timeout=15).json().get("results", [])
new_jobs = []

for job in jobs:
    job_id = job.get("id")
    combined = f"{job.get('title','')} {job.get('description','')}"

    if job_id and job_id not in seen_jobs and is_target_job(combined):
        new_jobs.append(job)
        seen_jobs.add(job_id)

# ===== SEND WHATSAPP =====
client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

for job in new_jobs:
    msg = (
        "🚨 NEW JOB JUST POSTED\n\n"
        f"Role: {job.get('title','N/A')}\n"
        f"Company: {job.get('company',{}).get('display_name','N/A')}\n"
        f"Location: {job.get('location',{}).get('display_name','India')}\n\n"
        f"Apply now:\n{job.get('redirect_url','')}"
    )
    client.messages.create(from_=FROM_WHATSAPP,to=TO_WHATSAPP,body=msg)

with open(SEEN_FILE,"w") as f:
    f.write("\n".join(seen_jobs))

log("===== SCRIPT FINISHED =====")
