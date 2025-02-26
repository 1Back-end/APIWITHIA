import openai
from typing import List

# Assurez-vous que votre clé API OpenAI est configurée
openai.api_key = "your_openai_api_key"

def analyze_candidate_profile(cv_text: str, experience_text: str, cover_letter: str, job_description: str) -> str:
    """
    Analyse le profil du candidat (CV, expérience, lettre de motivation) par rapport à l'offre d'emploi.
    """
    prompt = f"""
    Job Description: {job_description}

    Candidate CV: {cv_text}

    Candidate Experience: {experience_text}

    Candidate Cover Letter: {cover_letter}

    Based on the job description, evaluate the candidate's suitability for the role. Consider their qualifications, experience, and the relevance of their cover letter.
    Provide a detailed analysis and suggestion whether this candidate should be shortlisted or rejected.
    """
    
    response = openai.Completion.create(
        model="gpt-4",
        prompt=prompt,
        max_tokens=300,
        temperature=0.7,
    )
    analysis = response.choices[0].text.strip()
    return analysis
