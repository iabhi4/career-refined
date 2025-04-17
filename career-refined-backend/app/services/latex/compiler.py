import os, subprocess
from app.core.logging_config import get_logger

logger = get_logger(__name__)

def normalize_windows_path(win_path: str) -> str:
    # Convert backslashes to forward slashes and remove colon.
    drive, path = os.path.splitdrive(win_path)
    drive = drive.lower().replace(":", "")
    normalized = f"/{drive}{path.replace(os.sep, '/')}"
    return normalized

def compile_latex_file(latex_filepath: str) -> str:
    """
    Compile a LaTeX file using Docker and return the path to the compiled PDF.
    """
    logger.info(f"Starting LaTeX compilation for file: {latex_filepath}")

    if not os.path.exists(latex_filepath):
        logger.error(f"File not found: {latex_filepath}")
        raise FileNotFoundError(f"File not found: {latex_filepath}")

    directory = os.path.dirname(latex_filepath)
    normalized_directory = normalize_windows_path(directory)
    filename = os.path.basename(latex_filepath)

    pdfs_dir = os.path.join(directory, "pdfs")
    os.makedirs(pdfs_dir, exist_ok=True)

    command = [
        "docker", "run", "--rm",
        "-v", f"{normalized_directory}:/data",
        "my-latex",
        "pdflatex", "-interaction=nonstopmode",
        "-output-directory=/data/pdfs",
        filename
    ]

    logger.info(f"Running command: {' '.join(command)}")
    result = subprocess.run(command, cwd=directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = result.stdout.decode(), result.stderr.decode()
    logger.info("pdflatex stdout: %s", stdout)
    logger.info("pdflatex stderr: %s", stderr)

    pdf_filename = filename.replace(".tex", ".pdf")
    pdf_filepath = os.path.join(pdfs_dir, pdf_filename)

    if not os.path.exists(pdf_filepath):
        logger.error("PDF not generated.")
        raise RuntimeError(f"PDF not generated. pdflatex error: {stderr or 'Unknown error'}")

    logger.info(f"PDF successfully generated at: {pdf_filepath}")
    return pdf_filepath
