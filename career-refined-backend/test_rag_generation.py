# test_generation.py

import os
import sys
import logging
import time
import json # Needed for pretty printing the output
from pathlib import Path # Use pathlib for better path handling
from typing import Optional, Dict, Any

# --- Setup Python Path ---
# Add the project root to the Python path to allow importing 'app' modules
try:
    project_root = Path(__file__).resolve().parent # Assumes script is in project root
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    logger_setup = logging.getLogger(__name__) # Use temp logger for path info
    logger_setup.info(f"Added project root to sys.path: {project_root}")

    # --- Imports from your app ---
    # Ensure these imports match your project structure
    from app.core.config import settings # Your settings management
    from app.core.database import SessionLocal # Your SQLAlchemy session factory (Optional for this test, see below)
    from app.services.rag.generation import generate_combined_rag_output # The function we want to test

except ImportError as e:
    print(f"Error importing application modules: {e}")
    print("Please ensure:")
    print("1. This script is run from the project root directory ('career-refined-backend').")
    print("2. The necessary __init__.py files exist in your directories.")
    print("3. All dependencies are installed in the virtual environment.")
    sys.exit(1) # Exit if basic imports fail


# --- Configure Logging ---
# Basic logging setup for the test script
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()] # Log to console
)
logger = logging.getLogger("test_rag_generation")

# --- Test Configuration ---
# !!! IMPORTANT: Change this to a user ID that exists in your database
# !!! AND for whom the vector index has already been created using test_rag_retrieval.py
TEST_USER_ID = 10

# !!! IMPORTANT: Use a realistic job description for accurate testing
TEST_JOB_DESCRIPTION = """
We are hiring a Senior Software Engineer (Backend) proficient in Python.
The ideal candidate will have extensive experience designing, building, and maintaining scalable RESTful APIs
and microservices using frameworks like FastAPI or Django. Strong proficiency with SQL databases,
particularly PostgreSQL, is required. Experience with cloud platforms like AWS (Lambda, S3, RDS, API Gateway)
and containerization technologies (Docker, Kubernetes) is essential. Familiarity with message queues
(RabbitMQ/Kafka) and caching systems (Redis) is a plus. Must demonstrate ability to write clean,
testable code and work in an Agile environment.
"""

def run_generation_test():
    """Runs the RAG JSON generation test."""
    logger.info(f"--- Starting RAG Generation Test for User ID: {TEST_USER_ID} ---")

    # --- Pre-checks ---
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your_openai_api_key":
        logger.error("FATAL: OPENAI_API_KEY is not set in environment variables or .env file.")
        return
    if not settings.GENERATION_MODEL_NAME:
         logger.error("FATAL: GENERATION_MODEL_NAME is not set in settings.")
         return

    # Optional: Check if Chroma directory exists to infer if indexing likely ran
    if not os.path.exists(settings.CHROMA_PERSIST_DIRECTORY):
        logger.warning(f"Chroma persist directory '{settings.CHROMA_PERSIST_DIRECTORY}' not found.")
        logger.warning("Please ensure `test_rag_retrieval.py` or `update_user_vector_index` ran successfully first for this user.")
        # Decide if you want to exit or proceed (proceeding will likely fail in generate_ function)
        # return

    # Note: A direct DB session is usually NOT required by generate_tailored_editor_json itself,
    # as it primarily interacts with the retriever (which loads from disk) and the LLM.
    # Including it is only necessary if get_profile_retriever or other dependencies *unexpectedly* need it.
    # db: Optional[Session] = None
    # try:
        # logger.info("Creating database session (optional for this test)...")
        # db = SessionLocal()

    try:
        # --- Step 1: Call the Generation Function ---
        logger.info(f"Calling generate_tailored_editor_json for user_id={TEST_USER_ID}...")
        start_time = time.time()

        # Pass db=db only if the function signature requires it
        result_json: Optional[Dict[str, Any]] = generate_combined_rag_output(
            user_id=TEST_USER_ID,
            job_description=TEST_JOB_DESCRIPTION
        )

        end_time = time.time()
        logger.info(f"generate_tailored_editor_json completed in {end_time - start_time:.2f} seconds.")

        # --- Step 2: Evaluate Result ---
        if result_json:
            logger.info("\n--- Successfully Generated and Validated JSON Output ---")
            # Pretty print the resulting JSON
            print(json.dumps(result_json, indent=2))
            logger.info("--- End of Generated JSON ---")
            # You should manually review this JSON for content quality and relevance
        else:
            logger.error("\n--- JSON Generation Failed ---")
            logger.error("Check logs above for specific errors (retrieval, LLM call, parsing, validation).")

    except Exception as e:
        logger.exception(f"An unexpected error occurred during the test: {e}", exc_info=True)
    # finally:
        # --- Step 3: Close Database Session (if used) ---
        # if db:
        #     db.close()
        #     logger.info("Database session closed.")

    logger.info("--- RAG Generation Test Finished ---")

if __name__ == "__main__":
    run_generation_test()