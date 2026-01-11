from skills_db import SKILLS_DB
from nlp_utils import preprocess_text
from spell_corrector import correct_spelling

# Preprocess skill database ONCE
PROCESSED_SKILLS = {}

for skill in SKILLS_DB:
    tokens = preprocess_text(skill)
    for token in tokens:
        PROCESSED_SKILLS[token] = skill  # map stem → original skill


def extract_skills(text):
    skills_found = []

    tokens = clean_text(text)
    joined_text = " ".join(tokens)

    for skill in SKILLS_DB:
        skill_tokens = skill.split()
        if len(skill_tokens) == 1:
            if skill in tokens:
                skills_found.append(skill)
        else:
            if skill in joined_text:
                skills_found.append(skill)

    return list(set(skills_found))
