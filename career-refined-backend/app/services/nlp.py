import os, re, json, nltk
from nltk.corpus import stopwords
from openai import OpenAI
from dotenv import load_dotenv
from app.core.logging_config import get_logger
from app.core.config import settings

load_dotenv()
logger = get_logger(__name__)

nltk.download("stopwords")
nltk.download("punkt_tab")
stop_words = set(stopwords.words("english"))
generation_model = settings.GENERATION_MODEL_NAME

# nltk_data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'nltk_data')
# nltk.data.path.append(nltk_data_dir)
# try:
#     find("corpora/stopwords.zip")
# except LookupError:
#     print("Stopwords not found. Please run the download script.")
# try:
#     find("tokenizers/punkt")
# except LookupError:
#     print("Punkt tokenizer not found. Please run the download script.")
# stop_words = set(stopwords.words("english"))

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

def clean_response(response: str):
    match = re.search(r"```json\s*(\{.*\})\s*```", response, re.DOTALL)
    if match:
        response = match.group(1)
    return response


def clean_job_description(job_description: str):
    """Removes non-relevant job description sections while keeping CS-relevant parts."""
    
    REMOVE_SECTIONS = [
    r"(?i)\b(about us|about [A-Z][a-z]+|company overview|our mission|company culture|summary|who we are|what we offer)\b.*?",
    r"(?i)\b(perks|benefits|compensation|salary|our team|why join us|what you get|why work here)\b.*?",
    r"(?i)\b(legal|terms|policies|disclaimer|employment conditions|diversity and inclusion|equal opportunity employer)\b.*?"
    ]
    
    for pattern in REMOVE_SECTIONS:
        job_description = re.sub(pattern, "", job_description, flags=re.DOTALL)

    # Remove excessive new lines
    job_description = re.sub(r"\n\s*\n+", "\n\n", job_description).strip()

    # Tokenize words & remove stop words
    words = nltk.word_tokenize(job_description)
    filtered_text = " ".join([word for word in words if word.lower() not in stop_words])

    return filtered_text



def analyze_job_description(description: str):
    logger.info("Starting analysis of job description.")
    try:
        response = client.chat.completions.create(
            model=generation_model,
            messages=[
                {"role": "system", "content": "You are an expert assistant that extracts keywords from job descriptions."},
                {"role": "user", "content": f"""You are given a job description for a computer science oriented job. 
                 Your task is to dynamically extract every term that might be considered technical, including technical acronyms, from the job description. 
                 The extraction should be case-insensitive and focus exclusively on technical keywords—ignore all non-technical content such as soft skills,
                 general responsibilities, and organizational details. Extract keywords from various technical domains including programming languages, 
                 frameworks, tools, development methodologies, and any other technical terms relevant in a CS context. Even if a term appears only once, 
                 it is significant. If no technical keywords are found, return an empty list.

Return the extracted technical keywords as a flat JSON list in the following format:
"technical_keywords": ["keyword1", "keyword2", ...]

{description}
"""}
            ]
        )
        logger.info("Received response from OpenAI.")
        content = response.choices[0].message.content
        content = clean_response(content)
        return content
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        raise

def compare_and_generate_suggestions(job_description: str, resume_data: dict):
    logger.info("Starting analysis of job description. ", resume_data)
    try:
        response = client.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {"role": "system", "content": "You are an expert resume-tailoring and analysis assistant."},
                {"role": "user", "content": f"""
You will receive two inputs:\n\
1. **User Profile** – a JSON object containing personalDetails, experience, projects, skills, and education.\n\
2. **Job Description** – plain-text.\n\n\
Your tasks:\n\n\
────────────────────────────────────────\n\
TASK 1 – Extract Technical Keywords\n\
• Scan the Job Description and extract every technical term: languages, frameworks, tools, cloud tech, DBs, dev-ops items, acronyms, etc.\n\
• Ignore soft skills and company-culture text.\n\
• Case-insensitive search; preserve original casing in the output list.\n\
• Return this list under extracted_keywords.\n\n\
TASK 2 – Generate Tailored Resume\n\
**Personal Details**\n\
  • Copy exactly as provided (name, phone, email, linkedin, github).\n\
**Education**\n\
  • Include up to 2 most relevant entries (e.g. CS degrees).\n\
**Experience & Projects Selection Rules**\n\
  • Prioritize experience over projects.\n\
  • Select at least 2 experiences if available *and* at least 2-3 projects when ≥3 projects are available.\n\
  • Experience + project entries ≤ 5 total.\n\
  • Sum of all bullet points (across every experience + project) ≤ 15.\n\
  • Select items that best balance technical relevance *and* measurable impact for this JD.\n\
**Tailoring Guidelines**\n\
  • Rewrite responsibilities (experience) and descriptions (projects) to align strongly with the Job Description.\n\
  • Use strong action verbs and quantify impact (%, X × speed-up, # users, etc.) when possible.\n\
  • Bullet points separated by a literal \\n (newline) character.\n\
  • Do **NOT** invent companies, roles, project names, or technologies not present in the User Profile.\n\
  • If a field is missing in the profile, output null (do not hallucinate).\n\
  • Teaching-related experience: keep bullets strictly about pedagogy or measurable student outcomes. ↳ DO NOT add software-design / tech-stack jargon here.
**Skills**\n\
  • Keep only skills that are relevant to the Job Description.\n\
  • Categorize into exactly these keys — languages, frameworks, developerTools, cloudTechnologies, dbsApplications, otherSkillsAndTools.\n\
  • Omit any category that would be empty.\n\n\
TASK 3 – Improvement Feedback\n\
  • Provide 2–3 concise, actionable suggestions to further strengthen the tailored resume for *this* JD (e.g., \"Quantify outcome in Project X\", \"Mention Docker usage explicitly\").\n\n\
────────────────────────────────────────\n\
**STRICT OUTPUT RULES**\n\
Return *one* valid JSON object **only**, with these top-level keys:\n\
  1. tailored_resume\n\
  2. extracted_keywords\n\
  3. improvement_feedback\n\
No additional keys, text, or markdown.\n\n\
**tailored_resume** must exactly follow the schema of the input USER_PROFILE_JSON with all the tailored content:\n\       
**Inputs (replace placeholders before sending):**\n\
<USER_PROFILE_JSON>\n\
{json.dumps(resume_data)}\n\
<JOB_DESCRIPTION>\n\
{job_description}\n\
"""}
            ]
        )
        logger.info("Received response from OpenAI.")
        content = response.choices[0].message.content
        content = clean_response(content)
        return content
    except Exception as e:
        logger.error(f"Error during analysis: {e}")
        raise