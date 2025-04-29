import os
from jinja2 import Environment
from app.utils.helpers import transform_data_for_latex
from app.core.logging_config import get_logger

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

def convert_list_to_string(lst):
    if not isinstance(lst, list):
        return lst
    return ", ".join(item.strip() for item in lst if item.strip())


def generate_resume_latex(resume_data):
    if not isinstance(resume_data, dict):
      resume_data = resume_data.dict()
    logger.info("Generating LaTeX template for resume.")
    env = Environment()
    env.globals['escape_latex_characters'] = escape_latex_characters
    env.globals['convert_list_to_string'] = convert_list_to_string
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
      \textbf{Languages}{: {{ convert_list_to_string(skills.languages) }} } \\
      \textbf{Frameworks}{: {{ convert_list_to_string(skills.frameworks) }} } \\
      \textbf{Developer Tools}{: {{ convert_list_to_string(skills.developerTools) }} } \\
      \textbf{Cloud Technologies}{: {{ convert_list_to_string(skills.cloudTechnologies) }} } \\
      \textbf{DBS Applications}{: {{ convert_list_to_string(skills.dbsApplications) }} } \\
      \textbf{Other Skills \& Tools}{: {{ convert_list_to_string(skills.otherSkillsAndTools) }} }
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