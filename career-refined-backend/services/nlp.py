import os
import re
import nltk
from nltk.corpus import stopwords
from nltk.data import find
from openai import OpenAI
from dotenv import load_dotenv
from config.logging_config import get_logger
import json

load_dotenv()
logger = get_logger(__name__)

nltk.download("stopwords")
nltk.download("punkt_tab")
stop_words = set(stopwords.words("english"))

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
            model="gpt-3.5-turbo",
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

def compare_and_generate_suggestions(extracted_keywords: dict, resume_data: dict):
    logger.info("Starting analysis of job description.")
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are an expert assistant that compares resume bullet points with important keywords and provide some inference."},
                {"role": "user", "content": f"""You are provided with two sets of data:

A flat JSON list of technical keywords extracted from a computer science-oriented job description.
A user's profile containing a skills section and bullet points from their resume (including work experience and project details).
Your task is to:

Identify Matched Keywords:
1 - Compare the technical keywords from the job description to the user's profile (both skills section and bullet points).
2 - Perform a case-insensitive match and dynamically infer semantic equivalences. If a phrase in the user's profile is semantically equivalent to a job description keyword—even if not an exact text match—it should be considered a match.

Identify Missing Keywords:
1 - Determine which technical keywords from the job description are not present in the user's profile, either directly or through semantic equivalence.
                 
Provide Suggestions for Incorporation:
1 - For each missing keyword, analyze the user's bullet points to identify any that are contextually related via semantic inference.
2 - For related bullet points, extract a 4-5 word snippet from the original bullet point (sufficient for the user to identify it) and provide a revised suggestion that incorporates the missing keyword.
3 - Ensure the new bullet point suggestion matches the flow and style of the existing bullet points and is highly technical.
4 - If no semantically related bullet point is found, offer a general suggestion for adding a new bullet point that seamlessly fits into the existing flow while incorporating the missing keyword.

Output Format:  
Return the results as a JSON object with the following structure:
  "matched_keywords": ["keyword1", "keyword2", ...],
  "missing_keywords": ["keyword3", "keyword4", ...],
  "suggestions":
    "keyword3": "Old snippet: [4-5 word snippet] -> Proposed revision: [new bullet point suggestion incorporating keyword3, matching the flow and highly technical]",
    "keyword4": "Old snippet: [4-5 word snippet] -> Proposed revision: [new bullet point suggestion incorporating keyword4, matching the flow and highly technical]"

Input:
keywords - {extracted_keywords.get("technical_keywords")}
resume_data - {json.dumps(resume_data, indent=4)}
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