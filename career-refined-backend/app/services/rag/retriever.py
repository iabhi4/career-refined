# app/services/rag/retriever.py

import os
import logging
import shutil # For potentially clearing old index directories if needed
from typing import List, Optional, Dict # Ensure Dict is imported

# Third-party imports
import chromadb # ChromaDB client library
from sqlalchemy.orm import Session
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.vectorstores import VectorStoreRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Application-specific imports
from app.core.config import settings # Your settings management (e.g., Pydantic BaseSettings)
#from app.models import User, WorkExperience, Project, Education, Skill # Adjust imports based on your models location
# Import the function that generates the editorData JSON
try:
    from app.crud.application import get_editor_data_for_first_time # Or adjust path
except ImportError:
    logger_init = logging.getLogger(__name__) # Use temp logger for setup
    logger_init.error("Could not import get_editor_data_for_first_time. Ensure it is defined and accessible.")
    # Define a dummy if import fails, for structure (won't work at runtime)
    def get_editor_data_for_first_time(*args, **kwargs): return None


# --- Setup Logger ---
logger = logging.getLogger(__name__)

# --- Constants ---
COLLECTION_NAME_PREFIX = "user_profile_"
CHROMA_PERSIST_PATH = settings.CHROMA_PERSIST_DIRECTORY

# --- Initialize Shared Components ---
# (Keep the existing initialization block for embeddings_model, text_splitter, chroma_client)
try:
    embeddings_model = OpenAIEmbeddings(
        api_key=settings.OPENAI_API_KEY,
        model=settings.EMBEDDING_MODEL_NAME
    )
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.RAG_CHUNK_SIZE,
        chunk_overlap=settings.RAG_CHUNK_OVERLAP
    )
    chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_PATH)
    logger.info(f"ChromaDB client initialized. Persistence path: {CHROMA_PERSIST_PATH}")
except Exception as e:
    logger.exception(f"Failed to initialize RAG components: {e}", exc_info=True)
    raise RuntimeError("Failed to initialize essential RAG components.") from e

# --- Helper Functions ---
def _format_date_string(month: Optional[str], year: Optional[int]) -> Optional[str]:
    """Safely formats month and year into 'Month Year' string."""
    # Using Optional from typing for Python < 3.10 compatibility
    if month and isinstance(year, (int, float)) and not isinstance(year, bool):
        try:
            return f"{month} {int(year)}"
        except (ValueError, TypeError):
            return None
    return None

def _get_user_profile_documents(user_id: int, db: Session) -> List[Document]:
    """
    Fetches comprehensive profile data for a user using get_editor_data_for_first_time,
    parses the returned JSON, and converts relevant text fields into
    LangChain Document objects with metadata for indexing.
    (Includes previous modifications to use editor_data and exclude personal/education)
    """
    logger.debug(f"Fetching editor data via get_editor_data_for_first_time for user_id: {user_id}")
    documents = []
    try:
        editor_data = get_editor_data_for_first_time(db=db, user_id=user_id, exps=None, projects=None)
        if not editor_data:
            logger.warning(f"_get_user_profile_documents: get_editor_data_for_first_time returned no data for user_id: {user_id}")
            return []

        logger.debug(f"Processing editorData JSON for user_id: {user_id}")

        # --- Work Experience ---
        experience_list = editor_data.get("experience", [])
        logger.debug(f"Processing {len(experience_list)} experience entries.")
        for i, exp in enumerate(experience_list):
            exp_base_metadata = {"source": "experience", "index": i, "user_id": user_id}
            if exp.get("role"):
                doc_id = f"user_{user_id}_exp_{i}_role"
                documents.append(Document(page_content=exp["role"], metadata={**exp_base_metadata, "field": "role", "doc_id": doc_id}))
            if exp.get("company"):
                name = exp["company"]
                logger.debug(f"Company name embedding - {name}")
                doc_id = f"user_{user_id}_exp_{i}_company"
                documents.append(Document(page_content=exp["company"], metadata={**exp_base_metadata, "field": "company", "doc_id": doc_id}))
            if exp.get("responsibilities"):
                desc_chunks = text_splitter.split_text(exp["responsibilities"])
                for j, chunk in enumerate(desc_chunks):
                    doc_id = f"user_{user_id}_exp_{i}_resp_chunk_{j}"
                    documents.append(Document(page_content=chunk, metadata={**exp_base_metadata, "field": "responsibilities_chunk", "chunk_index": j, "doc_id": doc_id}))
            # Add other fields like location, dates if needed for context

        # --- Projects ---
        project_list = editor_data.get("projects", [])
        logger.debug(f"Processing {len(project_list)} project entries.")
        for i, proj in enumerate(project_list):
            proj_base_metadata = {"source": "project", "index": i, "user_id": user_id}
            if proj.get("name"):
                name = proj["name"]
                logger.debug(f"Project name embedding - {name}")
                doc_id = f"user_{user_id}_proj_{i}_name"
                documents.append(Document(page_content=proj["name"], metadata={**proj_base_metadata, "field": "name", "doc_id": doc_id}))
            if proj.get("description"):
                desc_chunks = text_splitter.split_text(proj["description"])
                for j, chunk in enumerate(desc_chunks):
                    doc_id = f"user_{user_id}_proj_{i}_desc_chunk_{j}"
                    documents.append(Document(page_content=chunk, metadata={**proj_base_metadata, "field": "description_chunk", "chunk_index": j, "doc_id": doc_id}))
            if proj.get("technologies"):
                doc_id = f"user_{user_id}_proj_{i}_tech"
                documents.append(Document(page_content=proj["technologies"], metadata={**proj_base_metadata, "field": "technologies", "doc_id": doc_id}))

        # --- Skills ---
        skills_dict = editor_data.get("skills", {})
        logger.debug(f"Processing skills dictionary with keys: {list(skills_dict.keys())}")
        for category, skill_list in skills_dict.items():
            if isinstance(skill_list, list):
                for k, skill in enumerate(skill_list):
                    if skill and isinstance(skill, str):
                        normalized_skill = skill.lower().replace(" ", "_")
                        doc_id = f"user_{user_id}_skill_{category}_{normalized_skill}_{k}"
                        documents.append(Document(
                            page_content=skill,
                            metadata={"source": "skills", "category": category, "user_id": user_id, "doc_id": doc_id}
                        ))

        # Education and Personal Details are intentionally omitted based on previous request

        logger.debug(f"Generated {len(documents)} documents from editorData for user_id: {user_id}")
        return documents

    except Exception as e:
        logger.exception(f"Error processing editor data for user_id {user_id}: {e}", exc_info=True)
        return []

# --- Core Service Functions ---

def update_user_vector_index(user_id: int, db: Session, print_added_docs: bool = False): # Added flag
    """
    Fetches the latest profile data for a user, generates documents,
    and updates their vector index in ChromaDB.
    Optionally prints the content of added/updated documents.

    Args:
        user_id: The ID of the user.
        db: The SQLAlchemy database session.
        print_added_docs: If True, prints added documents to console.
    """
    collection_name = f"{COLLECTION_NAME_PREFIX}{user_id}"
    logger.info(f"Starting vector index update for user_id: {user_id}, collection: {collection_name}")

    try:
        # 1. Get latest documents from profile data
        documents = _get_user_profile_documents(user_id, db)

        # Use try-except-finally for collection handling to ensure it exists if needed later
        collection = None
        try:
            # Try deleting first to ensure a clean slate with this simple strategy
            # In production, you might use upsert or more granular deletes based on doc_ids
            chroma_client.delete_collection(name=collection_name)
            logger.info(f"Cleared existing collection '{collection_name}' before update.")
        except Exception:
            logger.debug(f"Collection '{collection_name}' did not exist or couldn't be deleted (which is fine).")

        if not documents:
            logger.warning(f"No documents generated for user_id {user_id}. Index will be empty.")
            # Ensure collection exists even if empty, or handle this case in get_retriever
            # For simplicity, we'll let get_retriever handle non-existent collections later.
            return # Nothing more to do if no documents

        # Now create the collection cleanly
        collection = chroma_client.create_collection(
            name=collection_name,
            # Metadata can be useful for describing the collection, e.g.
            # metadata={"hnsw:space": "cosine"}, # Example if customizing index, default is often fine
             embedding_function=chromadb.utils.embedding_functions.OpenAIEmbeddingFunction(
                 api_key=settings.OPENAI_API_KEY,
                 model_name=settings.EMBEDDING_MODEL_NAME
             ) # Pass embedding function details to Chroma client
        )

        # 3. Prepare data and Add documents to the collection
        contents = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        # Ensure IDs are strings as required by Chroma
        ids = [str(doc.metadata.get('doc_id', f"doc_{i}")) for i, doc in enumerate(documents)]

        if not contents:
             logger.warning(f"No content extracted to add to collection '{collection_name}'.")
             return

        collection.add(
            documents=contents,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"Successfully updated vector index for user_id: {user_id}. Added {len(ids)} documents to collection '{collection_name}'.")

        # --- MODIFIED: Print added documents for verification if requested ---
        if print_added_docs and collection:
            try:
                logger.info(f"Verifying documents added to collection '{collection_name}' by retrieving them...")
                # Retrieve the documents we just added using their IDs
                results = collection.get(ids=ids, include=['documents', 'metadatas'])

                if results and results.get('documents'):
                    print(f"\n--- Documents Added/Updated in ChromaDB for User {user_id} ---")
                    for i, doc_content in enumerate(results['documents']):
                        # Ensure indices don't go out of bounds if results are partial/malformed
                        doc_id = results.get('ids', [])[i] if i < len(results.get('ids', [])) else 'N/A'
                        doc_meta = results.get('metadatas', [])[i] if i < len(results.get('metadatas', [])) else {}

                        print(f"\n[ID: {doc_id}]")
                        print(f"  Metadata: {doc_meta}")
                        print(f"  Content: {doc_content}")
                    print(f"--- End of {len(results['documents'])} Verified Documents ---")
                    logger.info(f"Successfully retrieved and printed {len(results['documents'])} added/updated documents for verification.")
                else:
                    logger.warning(f"Could not retrieve documents from collection '{collection_name}' after adding, or result format unexpected.")
                    print("\n--- Verification Warning: Could not retrieve added documents from ChromaDB. ---")

            except Exception as verify_e:
                logger.error(f"Error during verification print of added documents for user {user_id}: {verify_e}", exc_info=True)
                print(f"\n--- Verification Error: Could not print added documents ({verify_e}) ---")
        # --- End MODIFIED ---

    except Exception as e:
        logger.exception(f"Error updating vector index for user_id {user_id}: {e}", exc_info=True)
        # raise # Optionally re-raise

def get_profile_retriever(user_id: int, k: int = 15) -> Optional[VectorStoreRetriever]:
    """
    Loads the persisted vector store for a user from ChromaDB
    and returns a LangChain Retriever object.

    Args:
        user_id: The ID of the user.
        k: The number of relevant documents to retrieve.

    Returns:
        A VectorStoreRetriever instance, or None if the index doesn't exist
        or an error occurs.
    """
    collection_name = f"{COLLECTION_NAME_PREFIX}{user_id}"
    logger.info(f"Attempting to load retriever for user_id: {user_id}, collection: {collection_name}")

    try:
        # Check if collection exists first to provide a clearer error/warning
        try:
            # This confirms the collection exists in the persistent storage
            chroma_client.get_collection(name=collection_name)
            logger.debug(f"Collection '{collection_name}' found.")
        except Exception as e:
             # Catching a general exception might be too broad, but Chroma's specific exception for non-existence isn't obvious
             # Let's assume any error here means we can't get the collection reliably
             logger.warning(f"Vector index collection '{collection_name}' not found or inaccessible for user_id {user_id}. Cannot create retriever. Run 'update_user_vector_index' first. Detail: {e}")
             return None

        # If collection exists, create the LangChain wrapper
        vector_store = Chroma(
            client=chroma_client,
            collection_name=collection_name,
            embedding_function=embeddings_model, # Use the initialized LangChain OpenAIEmbeddings
            persist_directory=CHROMA_PERSIST_PATH # Specifying path helps ensure connection
        )

        retriever = vector_store.as_retriever(search_kwargs={'k': k})
        logger.info(f"Successfully loaded retriever for user_id: {user_id} (k={k}).")
        return retriever

    except Exception as e:
        logger.exception(f"Error loading retriever for user_id {user_id}: {e}", exc_info=True)
        return None