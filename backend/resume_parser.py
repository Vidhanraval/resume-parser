from io import BytesIO
import pdfplumber
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer

# Make sure NLTK resources are available
nltk.download("punkt")
nltk.download("stopwords")
nltk.download("wordnet")


def extract_text_from_pdf(file_bytes):
    text = ""
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.lower()


def extract_skills_from_section(text):
    """
    Extract skills ONLY from the skills section of the resume
    """
    # Try to capture content after "skill" or "skills"
    match = re.search(
        r"(skills|skill)(.*?)(education|experience|work|projects|$)",
        text,
        re.DOTALL
    )

    if not match:
        return []

    skills_text = match.group(2)

    # Tokenize
    tokens = word_tokenize(skills_text)

    stop_words = set(stopwords.words("english"))
    lemmatizer = WordNetLemmatizer()

    cleaned_tokens = [
        lemmatizer.lemmatize(token)
        for token in tokens
        if token.isalpha() and token not in stop_words
    ]

    # Reconstruct phrases (bigrams)
    skills = set()
    for i in range(len(cleaned_tokens) - 1):
        phrase = cleaned_tokens[i] + " " + cleaned_tokens[i + 1]
        skills.add(phrase)

    # Also keep single-word skills
    skills.update(cleaned_tokens)

    return sorted(skills)


def extract_experience(text):
    matches = re.findall(r"(\d+)\s*(years|year)", text)
    if matches:
        return max(int(m[0]) for m in matches)
    return 0


def extract_education(text):
    education_keywords = [
        "bachelor", "master", "masters", "mba", "phd",
        "university", "college"
    ]

    found = []
    for word in education_keywords:
        if word in text:
            found.append(word)

    return list(set(found))


def parse_resume(file_bytes, filename):
    if filename.endswith(".pdf"):
        text = extract_text_from_pdf(file_bytes)
    else:
        text = file_bytes.decode("utf-8").lower()

    skills = extract_skills_from_section(text)
    experience = extract_experience(text)
    education = extract_education(text)

    return {
        "skills": skills,
        "education": education,
        "experience": experience,
        "raw_text": text
    }
