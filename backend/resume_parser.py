from io import BytesIO
import pdfplumber
import re
import nltk

from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# ---------------------------
# SKILLS DB (MATCH YOUR RESUME)
# ---------------------------
SKILLS_DB = [
    "graphic design",
    "visual imagination",
    "typography",
    "digital illustration",
    "design software",
    "communication",
    "ui ux design"
]

# ---------------------------
# FIX BROKEN PDF TEXT
# ---------------------------
def fix_spaced_text(text):
    return re.sub(
        r'(?:^|\n)(?:[a-z]\s)+[a-z](?:$|\n)',
        lambda m: m.group(0).replace(" ", ""),
        text
    )

# ---------------------------
# PDF TEXT EXTRACTION
# ---------------------------
def extract_text_from_pdf(file_bytes):
    text = ""
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"

    text = text.lower()
    text = fix_spaced_text(text)
    text = text.replace("ui/ux", "ui ux")

    return text

# ---------------------------
# PREPROCESS
# ---------------------------
def preprocess_text(text):
    tokens = word_tokenize(text)

    stop_words = set(stopwords.words("english"))
    lemmatizer = WordNetLemmatizer()

    return [
        lemmatizer.lemmatize(tok)
        for tok in tokens
        if tok.isalpha() and tok not in stop_words
    ]

# ---------------------------
# SKILL EXTRACTION (SECTION BASED)
# ---------------------------
def extract_skills(text):
    match = re.search(r"skill[s]?\n(.+?)\nwork experience", text, re.DOTALL)

    if not match:
        return []

    skills_text = match.group(1)
    tokens = preprocess_text(skills_text)
    joined = " ".join(tokens)

    return [s for s in SKILLS_DB if s in joined]

# ---------------------------
# EXPERIENCE
# ---------------------------
def extract_experience(text):
    years = re.findall(r"(\d+)\s*(?:year|years)", text)
    return max(map(int, years)) if years else 0

# ---------------------------
# EDUCATION
# ---------------------------
def extract_education(text):
    keywords = ["university", "bachelor", "master", "mba", "phd"]
    return [k for k in keywords if k in text]

# ---------------------------
# MAIN
# ---------------------------
def parse_resume(file_bytes, filename):
    if filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    else:
        text = file_bytes.decode("utf-8").lower()

    return {
        "skills": extract_skills(text),
        "education": extract_education(text),
        "experience": extract_experience(text),
        "raw_text": text
    }
