import requests
from twilio.rest import Client
from datetime import datetime
import os

def log(msg):
    print(f"[{datetime.now()}] {msg}")

log("===== SCRIPT STARTED =====")

# ===== READ SECRETS =====
ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")

FROM_WHATSAPP = "whatsapp:+14155238886"
TO_WHATSAPP = "whatsapp:+919606429957"

if not all([ADZUNA_APP_ID, ADZUNA_APP_KEY, TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN]):
    raise RuntimeError("Missing secrets")

# ===== JOB TITLE FILTERS =====
INCLUDE = [
    "software engineer","software developer","sde","sde i","sde-1",
    "junior software engineer","associate software engineer",
    "entry level software engineer","graduate software engineer",
    "software engineer fresher","software engineer graduate",
    "software engineer trainee","software trainee","engineering trainee",
    "graduate trainee engineer","gte","campus hire","new grad","graduate hire",
    "backend developer","backend engineer","frontend developer","frontend engineer",
    "full stack developer","fullstack developer","junior backend developer",
    "junior frontend developer","junior full stack developer",
    "python developer","python engineer","java developer","java engineer",
    "javascript developer","node js developer","react developer","angular developer",
    "software intern","developer intern","engineering intern","backend intern",
    "frontend intern","full stack intern","python intern","java intern",
    "associate cloud engineer","cloud engineer fresher","junior devops engineer",
    "devops trainee","cloud support engineer","site reliability engineer trainee",
    "junior data analyst","data analyst fresher","associate data engineer",
    "data engineer fresher","junior machine learning engineer","ml engineer trainee",
    "ai engineer trainee","python data intern",
    "qa engineer","qa tester","quality analyst","junior test engineer",
    "software tester","automation test engineer trainee"
]

EXCLUDE = [
    "senior","lead","manager","architect","principal","staff",
    "sr","ii","iii","5+","6+","7+","head","director","vp"
]

def is_target_job(text):
    text = text.lower()
    return any(k in text for k in INCLUDE) and not any(x in text for x in EXCLUDE)

# ===== LOAD SEEN JOBS =====
SEEN_FILE = "seen_jobs.txt"
seen_jobs = set()
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE,"r") as f:
        seen_jobs = set(f.read().splitlines())

# ===== FETCH JOBS =====
url = "https://api.adzuna.com/v1/api/jobs/in/search/1"
params = {
    "app_id": ADZUNA_APP_ID,
    "app_key": ADZUNA_APP_KEY,
    "results_per_page": 20,
    "what": "software",
    "where": "Bangalore OR Chennai OR Hyderabad"
}

jobs = requests.get(url, params=params, timeout=15).json().get("results", [])
new_jobs = []

for job in jobs:
    job_id = job.get("id")
    combined = f"{job.get('title','')} {job.get('description','')}".lower()
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
