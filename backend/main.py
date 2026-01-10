from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, UploadFile, File, Form
from resume_parser import parse_resume
from job_parser import parse_job
from matcher import hiring_decision
from supabase_client import supabase

from nltk_setup import setup_nltk
setup_nltk()


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/screen")
async def screen_candidate(
    resume_file: UploadFile = File(...),
    job_requirement: str = Form(...),
    user_id: str = Form(...)
):

    # 1. Read resume
    resume_bytes = await resume_file.read()
    resume_data = parse_resume(resume_bytes, resume_file.filename)

    # 2. Parse job
    job_data = parse_job(job_requirement)

    # 3. Make hiring decision
    result = hiring_decision(
        resume_skills=resume_data["skills"],
        resume_experience=resume_data["experience"],
        resume_text=resume_data["raw_text"],
        job_skills=job_data["required_skills"],
        required_experience=job_data["required_experience"],
        job_text=job_requirement
    )

    # 4. SAVE RESULT TO SUPABASE  ✅ (THIS IS THE PART YOU ASKED ABOUT)
    supabase.table("screening_results").insert({
    "user_id": user_id,
    "resume_filename": resume_file.filename,
    "job_requirement": job_requirement,
    "decision": result["decision"],
    "reason": result["reason"]
    }).execute()


    # 5. Return response
    return {
        "decision": result["decision"],
        "reason": result["reason"]
    }
