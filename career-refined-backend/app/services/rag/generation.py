import json
import logging
from typing import Dict, Any, Optional

# Third-party imports
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser # To get string output from LLM first
from pydantic import ValidationError

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
- Based *only* on the `Retrieved Context` and the `Job Description`:
    - **Select:** Choose the *most relevant* experiences and projects from the context that best match the Job Description (e.g., 2-4 experiences, 2-3 projects).
    - **Tailor:** Rewrite the descriptions ('responsibilities' in experience, 'description' in projects) for the *selected items only*, aligning them with the Job Description using action verbs and details from the context. Use newline '\\n' for bullets.
    - **Skills:** Identify skills from the context relevant to the job. Categorize them into: {"languages", "frameworks", "developerTools", "cloudTechnologies", "dbsApplications", "otherSkillsAndTools"}. Only include relevant skills found in context.
    - **Extract:** Extract company name and role for selected experiences, project name and technologies (comma-separated string) for selected projects *if found in the context*. Output null if not found.
- Structure this tailored content under the `tailored_resume` key in the final JSON output, adhering *strictly* to the sub-structure defined below.

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
def generate_combined_rag_output(user_id: int, job_description: str) -> Optional[Dict[str, Any]]:
    """
    Generates combined RAG output: tailored resume, keywords, suggestions.
    Returns a dictionary conforming to CombinedRagOutputSchema if successful.
    """
    logger.info(f"Starting COMBINED RAG generation task for user_id: {user_id}")

    # 1. Get Retriever (remains the same)
    retriever = get_profile_retriever(user_id=user_id, k=15) # Keep k reasonably high for context
    if not retriever:
        logger.error(f"Combined generation failed: Could not get retriever for user_id {user_id}.")
        return None

    # 2. Retrieve Context (remains the same)
    try:
        logger.debug(f"Invoking retriever for combined task for user_id {user_id}...")
        query = job_description
        relevant_docs = retriever.invoke(query)
        context_string = "\n\n---\n\n".join([f"Source: {doc.metadata.get('source', 'unknown')} (ID: {doc.metadata.get('doc_id', 'N/A')})\nContent: {doc.page_content}" for doc in relevant_docs])
        logger.info(f"Retrieved {len(relevant_docs)} documents for combined context for user_id {user_id}.")
        if not relevant_docs:
             logger.warning(f"Retriever returned no documents for user {user_id}. Proceeding without specific context.")
             context_string = "No specific context documents retrieved from the user's profile for this job description."
    except Exception as e:
        logger.exception(f"Combined generation failed: Error retrieving context for user_id {user_id}: {e}", exc_info=True)
        return None

    # 3. Construct Chain and Invoke LLM (Using NEW Prompt)
    try:
        # Use the NEW combined prompt
        rag_chain = COMBINED_RAG_PROMPT | llm | StrOutputParser()

        logger.info(f"Invoking LLM chain for combined task for user_id: {user_id}...")
        llm_response_str = rag_chain.invoke({
            "job_description": job_description,
            "context": context_string
        })
        logger.debug(f"LLM Raw Response String received (length: {len(llm_response_str)}) for user_id: {user_id}")

        if not llm_response_str:
             logger.error(f"Combined generation failed: LLM returned an empty response for user_id {user_id}.")
             return None

        # Cleanup (remains the same)
        cleaned_response_str = llm_response_str.strip()
        if cleaned_response_str.startswith("```json"): cleaned_response_str = cleaned_response_str[7:]
        if cleaned_response_str.startswith("```"): cleaned_response_str = cleaned_response_str[3:]
        if cleaned_response_str.endswith("```"): cleaned_response_str = cleaned_response_str[:-3]
        cleaned_response_str = cleaned_response_str.strip()


        # 4. Parse and Validate JSON Output (Using NEW Schema)
        logger.debug(f"Attempting to parse LLM response as JSON for combined output (user_id: {user_id})...")
        try:
            parsed_json = json.loads(cleaned_response_str)
            logger.debug(f"Combined JSON parsing successful for user_id: {user_id}.")
        except json.JSONDecodeError as e:
            logger.error(f"Combined generation failed: Failed to parse LLM response as JSON for user_id {user_id}. Error: {e}")
            logger.error(f"LLM Response (cleaned) that failed parsing:\n{cleaned_response_str}")
            return None

        logger.debug(f"Attempting to validate JSON against CombinedRagOutputSchema for user_id: {user_id}...")
        try:
            # ---> MODIFICATION: Validate using the NEW combined schema <---
            validated_data = CombinedRagOutputSchema.model_validate(parsed_json)
            validated_dict = validated_data.model_dump(mode='json')
            logger.info(f"Combined JSON validation successful for user_id: {user_id}.")
            return validated_dict # Success!

        except ValidationError as e:
            logger.error(f"Combined generation failed: LLM JSON output failed Pydantic validation for user_id {user_id}. Errors:\n{e}")
            logger.error(f"Parsed JSON that failed validation:\n{json.dumps(parsed_json, indent=2)}")
            return None

    except Exception as e:
        logger.exception(f"Combined generation failed: Unexpected error during LLM chain invocation or processing for user_id {user_id}: {e}", exc_info=True)
        return None