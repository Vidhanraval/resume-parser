from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

# 1️⃣ CREATE APP FIRST (ABSOLUTELY FIRST)
app = FastAPI(title="Resume Screening API")

# 2️⃣ ADD CORS IMMEDIATELY (BEFORE ANY HEAVY IMPORTS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # safe for demo
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 3️⃣ NOW IMPORT HEAVY MODULES
from resume_parser import parse_resume
from job_parser import parse_job
from matcher import hiring_decision
from supabase_client import supabase
from nltk_setup import setup_nltk

# 4️⃣ SAFE NLTK SETUP (AFTER APP + CORS)
setup_nltk()


# -----------------------------
# RESUME PARSER ENDPOINT
# -----------------------------
@app.post("/parse")
async def parse_only(resume_file: UploadFile = File(...)):
    resume_bytes = await resume_file.read()
    resume_data = parse_resume(resume_bytes, resume_file.filename)
    return resume_data


# -----------------------------
# RESUME SCREENING ENDPOINT
# -----------------------------
@app.post("/screen")
async def screen_candidate(
    resume_file: UploadFile = File(...),
    job_requirement: str = Form(...),
    user_id: str = Form(...),
):
    # Read resume
    resume_bytes = await resume_file.read()
    resume_data = parse_resume(resume_bytes, resume_file.filename)

    resume_data.setdefault("skills", [])
    resume_data.setdefault("experience", 0)
    resume_data.setdefault("raw_text", "")

    # Parse job
    job_data = parse_job(job_requirement)
    job_data.setdefault("required_skills", [])
    job_data.setdefault("required_experience", 0)

    # Decision
    result = hiring_decision(
        resume_skills=resume_data["skills"],
        resume_experience=resume_data["experience"],
        resume_text=resume_data["raw_text"],
        job_skills=job_data["required_skills"],
        required_experience=job_data["required_experience"],
        job_text=job_requirement,
    )

    # Save to Supabase
    supabase.table("screening_results").insert({
        "user_id": user_id,
        "resume_filename": resume_file.filename,
        "job_requirement": job_requirement,
        "decision": result["decision"],
        "reason": result["reason"],
    }).execute()

    return {
        "decision": result["decision"],
        "reason": result["reason"],
    }
