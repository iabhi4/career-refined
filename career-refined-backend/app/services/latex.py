import os, subprocess
from jinja2 import Environment
import boto3
from botocore.exceptions import NoCredentialsError, ClientError
from app.core.logging_config import get_logger
from app.utils.helpers import transform_data_for_latex
from app.celery_app import celery_app

logger = get_logger(__name__)

def escape_latex_characters(text):
    special_chars = {
        '\\': r'\\textbackslash{}',
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}'
    }
    for char, escape in special_chars.items():
        text = text.replace(char, escape)
    return text

def normalize_windows_path(win_path: str) -> str:
    # Convert backslashes to forward slashes and remove colon.
    drive, path = os.path.splitdrive(win_path)
    drive = drive.lower().replace(":", "")
    normalized = f"/{drive}{path.replace(os.sep, '/')}"
    return normalized

def generate_resume_latex(resume_data):
    resume_data = resume_data.dict()
    logger.info("Generating LaTeX template for resume.")
    env = Environment()
    env.globals['escape_latex_characters'] = escape_latex_characters
    latex_template = r"""%-------------------------
% Resume in Latex
% Author : Jake Gutierrez
% Based off of: https://github.com/sb2nov/resume
% License : MIT
%------------------------

\documentclass[letterpaper,11pt]{article}

\usepackage{latexsym}
\usepackage[empty]{fullpage}
\usepackage{titlesec}
\usepackage{marvosym}
\usepackage[usenames,dvipsnames]{color}
\usepackage{verbatim}
\usepackage{enumitem}
\usepackage[hidelinks]{hyperref}
\usepackage{fancyhdr}
\usepackage[english]{babel}
\usepackage{tabularx}
\input{glyphtounicode}


%----------FONT OPTIONS----------
% sans-serif
% \usepackage[sfdefault]{FiraSans}
% \usepackage[sfdefault]{roboto}
% \usepackage[sfdefault]{noto-sans}
% \usepackage[default]{sourcesanspro}

% serif
% \usepackage{CormorantGaramond}
% \usepackage{charter}


\pagestyle{fancy}
\fancyhf{} % clear all header and footer fields
\fancyfoot{}
\renewcommand{\headrulewidth}{0pt}
\renewcommand{\footrulewidth}{0pt}

% Adjust margins
\addtolength{\oddsidemargin}{-0.5in}
\addtolength{\evensidemargin}{-0.5in}
\addtolength{\textwidth}{1in}
\addtolength{\topmargin}{-.5in}
\addtolength{\textheight}{1.0in}

\urlstyle{same}

\raggedbottom
\raggedright
\setlength{\tabcolsep}{0in}

% Sections formatting
\titleformat{\section}{
  \vspace{-4pt}\scshape\raggedright\large
}{}{0em}{}[\color{black}\titlerule \vspace{-5pt}]

% Ensure that generate pdf is machine readable/ATS parsable
\pdfgentounicode=1

%-------------------------
% Custom commands
\newcommand{\resumeItem}[1]{
  \item\small{
    {\#1 \vspace{-2pt}}
  }
}

\newcommand{\resumeSubheading}[4]{
  \vspace{-2pt}\item
    \begin{tabular*}{0.97\textwidth}[t]{l@{\extracolsep{\fill}}r}
      \textbf{\#1} & \#2 \\
      \textit{\small\#3} & \textit{\small \#4} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubSubheading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \textit{\small\#1} & \textit{\small \#2} \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeProjectHeading}[2]{
    \item
    \begin{tabular*}{0.97\textwidth}{l@{\extracolsep{\fill}}r}
      \small\#1 & \#2 \\
    \end{tabular*}\vspace{-7pt}
}

\newcommand{\resumeSubItem}[1]{\resumeItem{\#1}\vspace{-4pt}}

\renewcommand\labelitemii{$\vcenter{\hbox{\tiny$\bullet$}}$}

\newcommand{\resumeSubHeadingListStart}{\begin{itemize}[leftmargin=0.15in, label={}]}
\newcommand{\resumeSubHeadingListEnd}{\end{itemize}}
\newcommand{\resumeItemListStart}{\begin{itemize}}
\newcommand{\resumeItemListEnd}{\end{itemize}\vspace{-5pt}}

%-------------------------------------------
%%%%%%  RESUME STARTS HERE  %%%%%%%%%%%%%%%%%%%%%%%%%%%%
\begin{document}
\begin{center}
    \textbf{\Huge \scshape {{personal.name}}} \\ \vspace{1pt}
    \small {{ personal.phone }} $|$ \href{ mailto:x@x.com }{\underline{ {{ personal.email }} }} $|$ 
    \href{ {{ personal.linkedin }} }{\underline{ {{ personal.linkedin }} }} $|$
    \href{ {{ personal.github }} }{\underline{ {{ personal.github }} }}
\end{center}

%-----------EXPERIENCE-----------
\section{Experience}
  \resumeSubHeadingListStart
    {% for exp in experience %}
    \resumeSubheading
      { {{ escape_latex_characters(exp.company) }} }{ {{ exp.startDate }} -- {{ exp.endDate }} }
      { {{ escape_latex_characters(exp.role) }} }{ {{ escape_latex_characters(exp.location) }} }
      \resumeItemListStart
        {% for responsibility in exp.responsibilities.split('\n') %}
        \resumeItem{ {{ escape_latex_characters(responsibility) }} }
        {% endfor %}
      \resumeItemListEnd
    {% endfor %}
  \resumeSubHeadingListEnd

%-----------PROJECTS-----------
\section{Projects}
  \resumeSubHeadingListStart
    {% for proj in projects %}
    \resumeProjectHeading
      { \textbf{ {{ escape_latex_characters(proj.name) }} } $|$ \emph{ {{ escape_latex_characters(proj.technologies) }} }}{ {{ proj.startDate }} -- {{ proj.endDate }} }
      \resumeItemListStart
        {% for detail in proj.description.split('\n') %}
        \resumeItem{ {{ escape_latex_characters(detail) }} }
        {% endfor %}
      \resumeItemListEnd
    {% endfor %}
  \resumeSubHeadingListEnd

%-----------PROGRAMMING SKILLS-----------
\section{Technical Skills}
  \begin{itemize}[leftmargin=0.15in, label={}]
      \small{\item{
      \textbf{Languages}{: {{ skills.languages }} } \\
      \textbf{Frameworks}{: {{ skills.frameworks }} } \\
      \textbf{Developer Tools}{: {{ skills.developerTools }} } \\
      \textbf{Cloud Technologies}{: {{ skills.cloudTechnologies }} } \\
      \textbf{DBS Applications}{: {{ skills.dbsApplications }} } \\
      \textbf{Other Skills \& Tools}{: {{ skills.otherSkillsAndTools }} }
      }}
  \end{itemize}

%-----------EDUCATION-----------
\section{Education}
  \resumeSubHeadingListStart
    {% for edu in education %}
    \resumeSubheading
      { {{ edu.institution }} }{ {{ edu.startYear }} -- {{ edu.endYear }} }
      { {{ edu.degree }} }{ {{ edu.location }} }
    {% endfor %}
  \resumeSubHeadingListEnd
\end{document}"""


    
    template = env.from_string(latex_template)
    sanatized_resume_data = transform_data_for_latex(resume_data)
    logger.info("Rendering LaTeX template with resume data.")
    rendered_latex = template.render(
        personal=sanatized_resume_data["personalDetails"],
        experience=sanatized_resume_data["experience"],
        projects=sanatized_resume_data["projects"],
        skills=sanatized_resume_data["skills"],
        education=sanatized_resume_data["education"]
    )
    rendered_latex = rendered_latex.replace(r'\#', r'#')
    with open("resume.tex", "w") as file:
        logger.info("Writing rendered LaTeX to resume.tex.")
        file.write(rendered_latex)

    logger.info("Running pdflatex to generate PDF.")
    filePath = os.path.join(os.getcwd(), "resume.tex")
    return filePath

@celery_app.task
def compile_latex(latex_filepath: str) -> str:
  """
  Compile a LaTeX file using pdflatex (via Docker) and return the PDF file path.
  """
  logger.info(f"Starting LaTeX compilation for file: {latex_filepath}")

  # Ensure the .tex file exists
  if not os.path.exists(latex_filepath):
    logger.error(f"File not found: {latex_filepath}")
    raise Exception(f"File not found: {latex_filepath}")

  directory = os.path.dirname(latex_filepath)
  normalized_directory = normalize_windows_path(directory)
  filename = os.path.basename(latex_filepath)
  logger.info(f"Using directory: {directory}, filename: {filename}")

  pdfs_dir = os.path.join(directory, "pdfs")
  if not os.path.exists(pdfs_dir):
    os.makedirs(pdfs_dir)

  # Use Docker to run pdflatex in a consistent environment.
  command = [
    "docker", "run", "--rm",
    "-v", f"{normalized_directory}:/data",
    "my-latex",  # Use the custom image
    "pdflatex", "-interaction=nonstopmode",
    "-output-directory=/data/pdfs",
    filename
  ]
  
  logger.info(f"Running command: {' '.join(command)}")
  result = subprocess.run(command, cwd=directory, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  stdout = result.stdout.decode()
  stderr = result.stderr.decode()
  logger.info("pdflatex stdout: %s", stdout)
  logger.info("pdflatex stderr: %s", stderr)
  
  # Check for errors:
  pdf_filename = filename.replace(".tex", ".pdf")
  pdf_filepath = os.path.join(directory, "pdfs", pdf_filename)
  if not os.path.exists(pdf_filepath):
    err = result.stderr.decode() if result.stderr else "Unknown error"
    logger.error(f"PDF not generated. pdflatex error: {err}")
    raise Exception(f"PDF not generated. pdflatex error: {err}")
  s3_bucket = "career-refined"
  #s3_key = f"pdfs/resume_{some_unique_id}.pdf"
  s3_key = f"pdfs/resume.pdf"
  url_or_presigned = upload_pdf_to_s3(pdf_filepath, s3_bucket, s3_key)

  # pdf_filename = filename.replace(".tex", ".pdf")
  #   # Assume pdf is generated in <directory>/pdfs/resume.pdf
  # source_pdf_path = os.path.join(directory, "pdfs", pdf_filename)
    
  #   # Destination in your Next.js project public folder (adjust the path as needed)
  # destination_pdf_path = os.path.join("..", "career-refined-frontend", "public", "pdfs", "resume.pdf")
    
  #   # Copy the generated PDF to the destination folder
  # shutil.copy(source_pdf_path, destination_pdf_path)

  logger.info(f"PDF successfully generated at: {url_or_presigned}")
  return url_or_presigned



def upload_pdf_to_s3(local_pdf_path: str, s3_bucket: str, s3_key: str) -> str:
    """
    Uploads a PDF file from the local path to the specified S3 bucket and key.
    Returns the S3 object URL or a presigned URL.
    """
    s3_client = boto3.client("s3")
    try:
        # e.g. local_pdf_path = "pdfs/resume.pdf"
        # s3_bucket = "my-app-pdfs"
        # s3_key = "pdfs/resume.pdf"

        s3_client.upload_file(
            Filename=local_pdf_path,
            Bucket=s3_bucket,
            Key=s3_key,
            ExtraArgs={
                "ContentType": "application/pdf"
            }
        )

        # Option A: Construct a public URL if the object is publicly accessible
        # https://my-app-pdfs.s3.amazonaws.com/pdfs/resume.pdf
        public_url = f"https://{s3_bucket}.s3.amazonaws.com/{s3_key}"
        return public_url

    except FileNotFoundError:
        raise Exception("The file to upload was not found.")
    except NoCredentialsError:
        raise Exception("AWS credentials were not found.")
    except ClientError as e:
        raise Exception(f"Failed to upload PDF to S3: {e}")