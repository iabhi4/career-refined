import os
import sys
import time
from sqlalchemy.orm import Session

# --- Setup Python Path ---
# Add the project root to the Python path to allow importing 'app' modules
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '.'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- Imports from your app ---
# Ensure these imports match your project structure
from app.core.logging_config import get_logger  # Your logging configuration
from app.core.database import SessionLocal
from app.services.rag.retriever import update_user_vector_index, get_profile_retriever
from app.core.config import settings  # Your settings management

# --- Configure Logging ---
# Basic logging setup for the test script
logger = get_logger(__name__)

# --- Test Configuration ---
# !!! IMPORTANT: Change this to a user ID that exists in your database
# !!! and has associated profile data (experiences, projects, skills, etc.)
TEST_USER_ID = 10

def run_retrieval_test():
    """Runs the indexing and retrieval test."""
    logger.info(f"--- Starting RAG Retrieval Test for User ID: {TEST_USER_ID} ---")

    # --- Pre-checks ---
    if not settings.OPENAI_API_KEY or settings.OPENAI_API_KEY == "your_openai_api_key":
        logger.error("FATAL: OPENAI_API_KEY is not set in environment variables or .env file.")
        return

    logger.info(f"Using ChromaDB persistent path: {settings.CHROMA_PERSIST_DIRECTORY}")
    # Optional: Clean up previous test runs if desired
    # import shutil
    # if os.path.exists(settings.CHROMA_PERSIST_DIRECTORY):
    #     logger.warning(f"Removing existing Chroma directory: {settings.CHROMA_PERSIST_DIRECTORY}")
    #     shutil.rmtree(settings.CHROMA_PERSIST_DIRECTORY)

    db: Session | None = None
    try:
        # --- Step 1: Connect to Database ---
        logger.info("Creating database session...")
        db = SessionLocal()
        if not db:
            logger.error("Failed to create a database session.")
            return
        logger.info("Database session created.")
        # Add a basic check if user exists (optional)
        # from app.models import User
        # user = db.query(User).filter(User.id == TEST_USER_ID).first()
        # if not user:
        #     logger.error(f"Test user with ID {TEST_USER_ID} not found in the database.")
        #     return

        # --- Step 2: Run Indexing ---
        logger.info(f"Calling update_user_vector_index for user_id={TEST_USER_ID}...")
        start_time = time.time()
        update_user_vector_index(user_id=TEST_USER_ID, db=db, print_added_docs=True)
        end_time = time.time()
        logger.info(f"update_user_vector_index completed in {end_time - start_time:.2f} seconds.")
        logger.info(f"Check the directory '{settings.CHROMA_PERSIST_DIRECTORY}' for ChromaDB files.")

        # --- Step 3: Get Retriever ---
        logger.info(f"Calling get_profile_retriever for user_id={TEST_USER_ID}...")
        retriever = get_profile_retriever(user_id=TEST_USER_ID, k=15) # Request top 5 docs for testing

        # --- Step 4: Test with a Query ---
        if retriever:
            logger.info("Retriever object successfully obtained!")
            # !!! IMPORTANT: Change this query to something relevant to your TEST_USER_ID's data
            test_query = "experience with web frameworks and databases"
            logger.info(f"Invoking retriever with test query: '{test_query}'")

            start_time = time.time()
            # Use invoke() which is the standard LangChain interface
            relevant_docs = retriever.invoke(test_query)
            end_time = time.time()
            logger.info(f"Retriever query completed in {end_time - start_time:.4f} seconds.")

            logger.info(f"\n--- Found {len(relevant_docs)} relevant documents ---")
            if relevant_docs:
                for i, doc in enumerate(relevant_docs):
                    print(f"\n[Document {i+1}]")
                    print(f"  Content: {doc.page_content}")
                    print(f"  Metadata: {doc.metadata}")
            else:
                logger.warning("Retriever did not return any documents for this query.")
            logger.info("--- End of relevant documents ---")
        else:
            logger.error("Failed to get retriever. The index might not exist or an error occurred.")

    except Exception as e:
        logger.exception(f"An unexpected error occurred during the test: {e}", exc_info=True)
    finally:
        # --- Step 5: Close Database Session ---
        if db:
            db.close()
            logger.info("Database session closed.")

    logger.info("--- RAG Retrieval Test Finished ---")

if __name__ == "__main__":
    run_retrieval_test()