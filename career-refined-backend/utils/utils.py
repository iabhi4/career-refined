from typing import Dict, List, Any
from config.logging_config import get_logger

logger = get_logger(__name__)

def extract_relevant_items(suggestions: Dict, experiences: List[str], projects: List[str]) -> Dict[str, List[str]]:
    """
    Extract experience and project names from suggestions
    Returns dict with 'experiences' and 'projects' lists
    """
    relevant_items = {
        "experiences": [],
        "projects": []
    }
    
    for suggestion_type, suggestions_list in suggestions.items():
        # Skip if not a list of suggestions
        if not isinstance(suggestions_list, list):
            continue
            
        for suggestion in suggestions_list:
            # Extract the name from the suggestion
            if "Old text:" in suggestion:
                # Get text between "Old text:" and "New text:"
                old_text = suggestion.split("Old text:")[1].split("New text:")[0].strip()
                
                # Add to appropriate list based on suggestion type
                if suggestion_type.lower() == "experience suggestions":
                    relevant_items["experiences"].append(old_text)
                elif suggestion_type.lower() == "project suggestions":
                    relevant_items["projects"].append(old_text)

    return relevant_items

def categorize_skills(skills: List[str]) -> Dict[str, List[str]]:
    if isinstance(skills, str):
        skills = [s.strip() for s in skills.split(",") if s.strip()]
    logger.info("Starting skill categorization for skills: %s", skills)
    
    # Default lists used for classification only
    default_categories: Dict[str, List[str]] = {
        "languages": [
            "java", "python", "c", "c++", "c/c++", "javascript", "typescript",
            "html", "css", "sql", "r", "scala", "swift", "objective-c", "kotlin",
            "perl", "ruby", "go", "rust", "dart", "matlab", "julia", "groovy",
            "vb.net", "f#", "php", "c#", "powershell", "bash", "shell", "clojure",
            "elixir", "haskell", "erlang", "fortran", "lua", "assembly", "prolog",
            "ada", "delphi"
        ],
        "frameworks": [
            "springboot", "spring mvc", "django", "flask", "express", "laravel",
            "ruby on rails", "react", "angular", "vue", "svelte", "ember", "backbone",
            "node.js", "jquery", "next.js", "nuxt.js", "gatsby", "fastapi", "asp.net",
            ".net", "meteor", "redux", "mobx", "polymer", "bootstrap", "tailwind",
            "material-ui", "ant design", "electron", "capacitor", "react native",
            "ionic", "xamarin", "tensorflow", "keras", "pytorch", "scikit-learn",
            "mxnet", "caffe", "theano", "pandas", "numpy", "scipy", "wagtail",
            "struts", "zend", "symfony"
        ],
        "developerTools": [
            "git", "github", "gitlab", "bitbucket", "vs code", "intellij", "pycharm",
            "eclipse", "sublime text", "webstorm", "visual studio", "xcode", "atom",
            "notepad++", "vim", "emacs", "npm", "yarn", "webpack", "rollup", "babel",
            "maven", "gradle", "ant", "docker", "docker desktop", "jenkins", "travis ci",
            "circleci", "gitlab ci", "sentry", "newrelic", "postman", "fiddler",
            "chrome devtools", "slack", "jira", "confluence", "trello", "notion",
            "sourcetree", "azure devops", "deno", "gulp", "grunt", "vagrant", "bazel"
        ],
        "cloudTechnologies": [
            "aws ec2", "aws rds", "aws s3", "aws lambda", "aws ses", "aws cloudfront",
            "aws elastic beanstalk", "aws dynamodb", "aws cognito", "aws cli", "azure",
            "azure devops", "google cloud platform", "gcp", "heroku", "digitalocean",
            "openstack", "vmware", "cloudflare", "kubernetes", "docker", "terraform",
            "ansible", "chef", "puppet", "docker swarm", "nomad", "serverless"
        ],
        "dbsApplications": [
            "jdbc", "postgresql", "mysql", "mariadb", "oracle", "sql server",
            "mongodb", "redis", "cassandra", "couchdb", "firebase", "neo4j",
            "dynamodb", "influxdb", "clickhouse", "hive", "presto", "snowflake",
            "elasticsearch", "solr", "ms access", "informix", "db2"
        ],
        "otherSkillsAndTools": [
            "object-oriented programming", "design patterns", "data structures", "algorithms",
            "system design", "microservices", "rest api", "graphql", "soap",
            "agile methodologies", "scrum", "kanban", "tdd", "bdd", "unit testing",
            "integration testing", "performance testing", "load testing", "automation testing",
            "ci/cd", "docker-compose", "monitoring", "logging", "prometheus", "grafana",
            "elk stack", "security best practices", "penetration testing", "debugging",
            "code review", "pair programming", "version control", "devops", "sdlc",
            "communication", "leadership", "project management", "cloud computing",
            "virtualization", "machine learning", "deep learning", "natural language processing",
            "computer vision", "data analysis", "statistics", "data visualization", "big data",
            "spark", "hadoop", "airflow", "mlops", "research", "innovation", "problem solving",
            "continuous improvement", "restful services", "soap web services", "ui/ux design",
            "responsive design", "cross-browser compatibility", "performance optimization",
            "selenium", "cucumber", "appium", "k6", "jmeter"
        ]
    }
    
    # Prepare a dictionary to collect the user-provided skills by category.
    user_categorized: Dict[str, List[str]] = {
        "languages": [],
        "frameworks": [],
        "developerTools": [],
        "cloudTechnologies": [],
        "dbsApplications": [],
        "otherSkillsAndTools": []
    }
    
    logger.debug(f"Default categories loaded: {list(default_categories.keys())}")
    
    # Normalize the incoming skills (lowercase and strip spaces)
    normalized_skills = [skill.lower().strip() for skill in skills]
    logger.debug(f"Normalized skills: {normalized_skills}")
    
    # For each normalized skill, check if it exactly matches a default value.
    for skill in normalized_skills:
        matched = False
        for category, default_list in default_categories.items():
            if skill in default_list:
                user_categorized[category].append(skill)
                logger.debug(f"Skill '{skill}' categorized under '{category}'.")
                matched = True
                break
        if not matched:
            # If not found in any category, put it in otherSkillsAndTools
            user_categorized["otherSkillsAndTools"].append(skill)
            logger.debug(f"Skill '{skill}' categorized under 'otherSkillsAndTools'.")
    
    logger.info("Skill categorization completed. Categorized skills: %s", user_categorized)
    return user_categorized


def transform_data_for_latex(original_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transform raw resume data into the structure expected by the LaTeX template.
    This does NOT escape LaTeX characters; it just renames/combines fields.

    The returned dict will look like:
    {
      "personal": {
        "name": str,
        "phone": str,
        "email": str,
        "linkedin": str,
        "github": str
      },
      "experience": [
        {
          "company": str,
          "startDate": str,     # e.g. "Aug 2021"
          "endDate": str,       # e.g. "May 2023"
          "role": str,
          "location": str,
          "responsibilities": str (multiline)
        },
        ...
      ],
      "projects": [
        {
          "name": str,
          "technologies": str,
          "startDate": str,     # e.g. "Jan 2022"
          "endDate": str,       # e.g. "Dec 2022"
          "description": str (multiline)
        },
        ...
      ],
      "skills": {
        "languages": str,
        "frameworks": str,
        "developerTools": str,
        "cloudTechnologies": str,
        "dbsApplications": str,
        "otherSkillsAndTools": str
      },
      "education": [
        {
          "institution": str,
          "startYear": str,     # e.g. "Aug 2017"
          "endYear": str,       # e.g. "May 2021"
          "degree": str,
          "location": str
        },
        ...
      ]
    }
    """

    # Prepare the final dict that matches the LaTeX template
    transformed = {
        "personal": {},
        "experience": [],
        "projects": [],
        "skills": {
            "languages": "",
            "frameworks": "",
            "developerTools": "",
            "cloudTechnologies": "",
            "dbsApplications": "",
            "otherSkillsAndTools": "",
        },
        "education": []
    }

    # ---------------- 1) Personal  ----------------
    personal_raw = original_data.get("personalDetails", {})
    transformed["personalDetails"] = {
        "name": personal_raw.get("name", ""),
        "phone": personal_raw.get("phone", ""),       # or phone_number
        "email": personal_raw.get("email", ""),
        "linkedin": personal_raw.get("linkedin", ""), # or linkedin_link
        "github": personal_raw.get("github", ""),     # or github_link
    }

    # ---------------- 2) Experience  ----------------
    # Template expects: company, startDate, endDate, role, location, responsibilities (multiline)
    exp_raw = original_data.get("experience", [])
    for exp in exp_raw:
        start_date = exp.get("startDate", "").strip()
        end_date= exp.get("endDate", "").strip()

        # If responsibilities is an array, convert to multiline
        resp = exp.get("responsibilities", "")
        if isinstance(resp, list):
            resp_str = "\n".join(resp)
        else:
            resp_str = str(resp)

        transformed["experience"].append({
            "company": exp.get("company", ""),
            "startDate": start_date,
            "endDate": end_date,
            "role": exp.get("role", ""),  # fallback to position
            "location": exp.get("location", ""),
            "responsibilities": resp_str,
        })

    # ---------------- 3) Projects  ----------------
    # Template expects: name, technologies, startDate, endDate, description (multiline)
    proj_raw = original_data.get("projects", [])
    for proj in proj_raw:
        start_date = proj.get("startDate", "").strip()
        end_date= proj.get("endDate", "").strip()

        # If description is an array, convert to multiline
        desc = proj.get("description", [])
        if isinstance(desc, list):
            desc = "\n".join(desc)
        else:
            desc = str(desc)

        #logger.info("yo look here Project description: %s", desc)

        # If technologies is an array, convert to comma-separated
        tech = proj.get("technologies", "")
        if isinstance(tech, list):
            tech_str = ", ".join(tech)
        else:
            tech_str = str(tech)

        transformed["projects"].append({
            "name": proj.get("name", proj.get("project_name", "")),
            "technologies": tech_str,
            "startDate": start_date,
            "endDate": end_date,
            "description": desc,
        })

    # ---------------- 4) Skills  ----------------
    # The template expects single strings for each category
    # def to_comma_string(val):
    #     if isinstance(val, list):
    #         return ", ".join(val)
    #     return str(val or "")

    skills_raw = original_data.get("skills", {})
    transformed["skills"] = {
        "languages": skills_raw.get("languages", ""),
        "frameworks": skills_raw.get("frameworks", ""),
        "developerTools": skills_raw.get("developerTools", ""),
        "cloudTechnologies": skills_raw.get("cloudTechnologies", ""),
        "dbsApplications": skills_raw.get("dbsApplications", ""),
        "otherSkillsAndTools": skills_raw.get("otherSkillsAndTools", ""),
    }

    # ---------------- 5) Education  ----------------
    # Template expects: institution, startYear, endYear, degree, location
    edu_raw = original_data.get("education", [])
    for edu in edu_raw:
        # Merge start_month + start_year => startYear
        start_date = edu.get("startYear", "").strip()
        end_date= edu.get("endYear", "").strip()


        transformed["education"].append({
            "institution": edu.get("institution", edu.get("school_name", "")),
            "startYear": start_date,
            "endYear": end_date,
            "degree": edu.get("degree", edu.get("degree_type", "")),
            "location": edu.get("location", ""),
        })

    return transformed