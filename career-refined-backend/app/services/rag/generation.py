import json
import logging
from typing import Dict, Any, Optional

# Third-party imports
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser # To get string output from LLM first
from pydantic import ValidationError
from langchain_core.documents import Document
import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb import PersistentClient

# Application-specific imports
# Adjust import paths based on your project structure
from app.core.config import settings
from app.services.rag.retriever import get_profile_retriever # Function to get retriever from retriever.py
from app.models.editor import StrictEditorDataSchema, SkillsSchema, CombinedRagOutputSchema

# --- Setup Logger ---
logger = logging.getLogger(__name__)

# --- Initialize LLM ---
# Use a powerful model capable of following complex instructions and JSON formatting
# Recommended: gpt-4-turbo, gpt-4o, or equivalent Claude 3 models
try:
    llm = ChatOpenAI(
        # Ensure GENERATION_MODEL_NAME is set in your settings (e.g., "gpt-4-turbo")
        model=settings.GENERATION_MODEL_NAME,
        temperature=0.2, # Lower temperature for more deterministic JSON structure
        api_key=settings.OPENAI_API_KEY,
        # OPTIONAL: Enable JSON mode if using compatible model (e.g., gpt-4-turbo, gpt-4o)
        # This often improves reliability but requires the prompt to explicitly ask for JSON.
        # model_kwargs={"response_format": {"type": "json_object"}},
    )
    logger.info(f"Initialized ChatOpenAI generation model: {settings.GENERATION_MODEL_NAME}")
except Exception as e:
    logger.exception(f"Failed to initialize ChatOpenAI generation model: {e}", exc_info=True)
    # Fail fast if LLM can't be initialized
    raise RuntimeError("Failed to initialize essential Generation LLM.") from e


# --- Prepare Schema Details for Prompt ---
# Load the schema structure and skill categories to guide the LLM
# --- Prepare Schema Details for Prompt ---
try:
    schema_json_str = json.dumps(StrictEditorDataSchema.model_json_schema(), indent=2) # Keep this

    # ---> MODIFICATION: Get keys directly from SkillsSchema <---
    if hasattr(SkillsSchema, 'model_fields'): # Check if it's a Pydantic V2 model
         skill_categories_list = list(SkillsSchema.model_fields.keys())
    else:
         # Fallback or error if SkillsSchema isn't a V2 model somehow
         logger.error("SkillsSchema does not appear to be a Pydantic V2 model (no model_fields).")
         # Provide a default list or raise an error
         skill_categories_list = ["languages", "frameworks", "developerTools", "cloudTechnologies", "dbsApplications", "otherSkillsAndTools"] # Example default
         # raise TypeError("SkillsSchema is not a valid Pydantic V2 model.")

    logger.debug(f"Using skill categories for prompt: {skill_categories_list}")

except Exception as e:
    logger.exception("Failed to load schema details for the RAG prompt.", exc_info=True)
    raise RuntimeError("Failed to load schema details for RAG prompt.") from e

# --- Define Prompt Template ---
# Guides the LLM to select, tailor, and structure the output as JSON.
COMBINED_RAG_PROMPT_TEMPLATE = f"""
You are an expert resume analysis and tailoring assistant. Your goal is to perform three tasks based on the user's background ('Retrieved Context') and a target 'Job Description', then output the results in a single, specific JSON format.

**TASK 1: Extract Technical Keywords**
- Analyze the 'Job Description'.
- Extract every term that might be considered technical (programming languages, frameworks, tools, methodologies, technical acronyms, etc.).
- Focus *exclusively* on technical keywords; ignore soft skills, general responsibilities, company details.
- Extraction should be case-insensitive but preserve original casing in the output list if appropriate.
- Return these keywords as a flat list within the specified JSON structure under `extracted_keywords.technical_keywords`.

**TASK 2: Generate Tailored Resume Content**
-Based strictly on the Retrieved Context and the Job Description:
	-*Select*: Choose the most relevant experiences and projects from the context that best match the Job Description.
		-Always prioritize experiences over projects when selecting.
		-Select at least 2 experiences if available.
		-Maximum total entries (experiences + projects) = 5:
			-If 2 or more experiences are selected, select 3 or fewer projects.
			-If only 1 experience is selected, select up to 4 projects.
			-Never exceed 5 total items combined.
	-*Tailor*: Rewrite the descriptions:
		-For experiences: tailor the responsibilities field.
		-For projects: tailor the description field.
		-Tailoring must align descriptions strongly with the Job Description.
		-Use powerful action verbs and measurable impacts when possible.
		-Use newline \n for bullet points (each bullet point must be clearly separated by \n).
	-Skills:
		-Select only the skills from the context relevant to the job.
		-Categorize them into: {"languages", "frameworks", "developerTools", "cloudTechnologies", "dbsApplications", "otherSkillsAndTools"}.
		-Do not invent or hallucinate skills outside the context.
	-Extract metadata:
		-For each selected experience: extract company and role.
		-For each selected project: extract name and technologies (comma-separated).
		-If any metadata is missing in context, return null for that field rather than inventing.
IMPORTANT Grounding Rules:
-You are strictly forbidden from inventing new companies, roles, or project names.
-You must only select from the "Experiences" and "Projects" listed in the context above.
-Company and role names in experience must match exactly (case-sensitive) from the context.
-Project names must match exactly from the context.
-If an experience or project is missing in the context, do not create a substitute — skip it.
Structure the tailored content under the tailored_resume key in the final JSON output, adhering strictly to the specified sub-structure.

**TASK 3: Provide Improvement Feedback on Tailored Resume**
- AFTER performing TASK 2 (generating the tailored resume content), critically review the `tailored_resume` output you generated.
- Compare this generated `tailored_resume` against the requirements and nuances of the 'Job Description'.
- Identify 2-3 key areas where the generated resume could be *further improved* to maximize its impact and alignment specifically for *this* job.
- Focus on actionable, constructive feedback beyond the basic tailoring already performed. Examples: "Consider quantifying achievements more specifically in Project X's description.", "The skills section is good, but explicitly mentioning [Specific Skill from JD] if applicable based on context could strengthen it.", "Adding a brief introductory summary tailored to this role above the experience might be beneficial.", "Ensure the action verbs used in the experience section are consistently strong."
- Provide this feedback as a list of concise strings under the `improvement_feedback` key in the final JSON output.

**FINAL OUTPUT STRUCTURE:**
Construct the *entire* output as a single, valid JSON object. It MUST contain ONLY the following top-level keys: "tailored_resume", "extracted_keywords", "suggestions".

1.  `tailored_resume`: Object containing:
    * `experience`: List of objects, each with ONLY keys "company" (string), "role" (string), "responsibilities" (string).
    * `projects`: List of objects, each with ONLY keys "name" (string), "technologies" (string), "description" (string).
    * `skills`: Object with keys for categories {"languages", "frameworks", "developerTools", "cloudTechnologies", "dbsApplications", "otherSkillsAndTools"}, each mapping to a list of skill strings. Do NOT include empty category lists.
2.  `extracted_keywords`: Object containing:
    * `technical_keywords`: List of strings.
3.  `improvement_feedback`: A list of strings, where each string is a concise, actionable feedback point based on comparing the generated `tailored_resume` to the job description.

**Crucial Formatting Rules:**
- Output ONLY the JSON object. No explanations, apologies, comments, or markdown ```json formatting.
- Adhere strictly to the specified keys and structures.
- Do NOT invent information (like company names, skills, or experiences) not found in the `Retrieved Context`. Output null or omit where appropriate according to the structure if information is missing in the context.

**Input:**

Job Description:
---
{{job_description}}
---

Retrieved Context (Relevant snippets from user's full profile):
---
{{context}}
---

**Output (JSON object only):**
"""

COMBINED_RAG_PROMPT = ChatPromptTemplate.from_template(COMBINED_RAG_PROMPT_TEMPLATE)

# --- Core Generation Function (generate_tailored_editor_json -> needs renaming?) ---
# Rename function to reflect combined output
def generate_combined_rag_output(
    user_id: int,
    job_description: str
) -> Optional[Dict[str, Any]]:
    """
    1) Retrieves ALL experience chunks, top‑3 project chunks, and ALL skill entries.
    2) Builds the combined context.
    3) Invokes the RAG chain and returns validated JSON.
    """
    logger.info(f"Starting COMBINED RAG for user_id={user_id}")

    # 1) fetch experiences
    exp_retriever = get_profile_retriever(
        user_id=user_id, k=9999, metadata_filter={"source": "experience"}
    )
    exp_docs = exp_retriever.get_relevant_documents(job_description) if exp_retriever else []

    # 2) fetch top 3 projects
    proj_retriever = get_profile_retriever(
        user_id=user_id, k=9999, metadata_filter={"source": "project"}
    )
    proj_docs = proj_retriever.get_relevant_documents(job_description) if proj_retriever else []

    # 3) fetch skills
    skill_retriever = get_profile_retriever(
        user_id=user_id, k=9999, metadata_filter={"source": "skills"}
    )
    skill_docs = skill_retriever.get_relevant_documents(job_description) if skill_retriever else []

    # merge
    context_docs = exp_docs + proj_docs + skill_docs
    logger.info(f"Context docs: {len(exp_docs)} exp, {len(proj_docs)} proj, {len(skill_docs)} skills")

    # 4) build context string - UPDATED STRUCTURE
    if context_docs:
        experiences = []
        projects = []
        skills = {"languages": [], "frameworks": [], "developerTools": [], "cloudTechnologies": [], "dbsApplications": [], "otherSkillsAndTools": []}

        for doc in context_docs:
            source = doc.metadata.get("source")
            field = doc.metadata.get("field")
            content = doc.page_content.strip()

            if source == "experience":
                exp_index = doc.metadata.get("index")
                if len(experiences) <= exp_index:
                    experiences.extend([{}] * (exp_index - len(experiences) + 1))
                exp = experiences[exp_index]
                if field == "company":
                    exp["company"] = content
                elif field == "role":
                    exp["role"] = content
                elif field == "responsibilities_chunk":
                    exp["responsibilities"] = exp.get("responsibilities", "") + f" {content}"
            elif source == "project":
                proj_index = doc.metadata.get("index")
                if len(projects) <= proj_index:
                    projects.extend([{}] * (proj_index - len(projects) + 1))
                proj = projects[proj_index]
                if field == "name":
                    proj["name"] = content
                elif field == "technologies":
                    proj["technologies"] = content
                elif field == "description_chunk":
                    proj["description"] = proj.get("description", "") + f" {content}"
            elif source == "skills":
                category = doc.metadata.get("category")
                if category in skills and isinstance(skills[category], list):
                    skills[category].append(content)

        context_parts = []

        if experiences:
            context_parts.append("## Experiences")
            for exp in experiences:
                if exp:
                    context_parts.append(f"- Company: {exp.get('company', 'Unknown')}")
                    context_parts.append(f"- Role: {exp.get('role', 'Unknown')}")
                    responsibilities = exp.get("responsibilities", "").strip()
                    if responsibilities:
                        bullets = responsibilities.split("\n")
                        bullet_list = "\n".join([f"    * {b.strip()}" for b in bullets if b.strip()])
                        context_parts.append(f"- Responsibilities:\n{bullet_list}")
                    context_parts.append("---")

        if projects:
            context_parts.append("## Projects")
            for proj in projects:
                if proj:
                    context_parts.append(f"- Name: {proj.get('name', 'Unknown')}")
                    context_parts.append(f"- Technologies: {proj.get('technologies', 'Unknown')}")
                    description = proj.get("description", "").strip()
                    if description:
                        bullets = description.split("\n")
                        bullet_list = "\n".join([f"    * {b.strip()}" for b in bullets if b.strip()])
                        context_parts.append(f"- Description:\n{bullet_list}")
                    context_parts.append("---")

        if skills:
            context_parts.append("## Skills")
            for category, skill_list in skills.items():
                if skill_list:
                    context_parts.append(f"- {category}: {', '.join(skill_list)}")
            context_parts.append("---")

        context_string = "\n".join(context_parts)

    else:
        logger.warning("No context docs found; using fallback text.")
        context_string = "No specific context documents retrieved from the user's profile."

    # 5) invoke LLM chain
    try:
        chain = COMBINED_RAG_PROMPT | llm | StrOutputParser()
        raw = chain.invoke({
            "job_description": job_description,
            "context": context_string
        })
    except Exception as e:
        logger.exception(f"LLM chain invocation failed: {e}")
        return None

    if not raw:
        logger.error("LLM returned empty response")
        return None

    # 6) strip fences & parse JSON
    cleaned = raw.strip()
    for fence in ("```json", "```"):
        if cleaned.startswith(fence):
            cleaned = cleaned[len(fence):].strip()
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3].strip()

    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to JSON‑parse LLM response: {e}\n{cleaned}")
        return None

    # 7) Pydantic validate
    try:
        validated = CombinedRagOutputSchema.model_validate(parsed)
        result = validated.model_dump(mode="json")
        logger.info("Combined RAG output validated successfully")
        return result
    except ValidationError as e:
        logger.error(f"Schema validation failed: {e}\n{json.dumps(parsed, indent=2)}")
        return None
