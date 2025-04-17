from app.core.logging_config import get_logger
from app.celery_app import celery_app
from app.services.latex.compiler import compile_latex_file
from app.services.latex.s3_uploader import upload_pdf_to_s3

logger = get_logger(__name__)

@celery_app.task
def compile_latex(latex_filepath: str) -> str:
    """
    Celery task to compile LaTeX to PDF and upload to S3.
    """
    logger.info(f"Compiling and uploading LaTeX for: {latex_filepath}")
    
    # Compile PDF
    pdf_filepath = compile_latex_file(latex_filepath)

    # Upload to S3
    s3_bucket = "career-refined"
    s3_key = "pdfs/resume.pdf"
    pdf_url = upload_pdf_to_s3(pdf_filepath, s3_bucket, s3_key)

    logger.info(f"PDF available at: {pdf_url}")
    return pdf_url
