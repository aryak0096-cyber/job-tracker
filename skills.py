"""Skill taxonomy used to extract skills from resumes and job descriptions.

Each category maps a canonical skill name to the aliases that should match it.
Matching is case-insensitive and respects word boundaries, so "java" does not
match "javascript" and "c++" / "c#" / ".net" are handled correctly.
"""

SKILL_CATEGORIES = {
    "Programming Languages": {
        "Python": ["python", "python3"],
        "Java": ["java"],
        "JavaScript": ["javascript", "js", "ecmascript", "es6"],
        "TypeScript": ["typescript"],
        "C++": ["c++"],
        "C#": ["c#", "csharp"],
        "Go": ["golang"],
        "Rust": ["rust"],
        "Kotlin": ["kotlin"],
        "Swift": ["swift"],
        "PHP": ["php"],
        "Ruby": ["ruby"],
        "Scala": ["scala"],
        "R": ["r programming", "rstudio"],
        "SQL": ["sql"],
        "Bash": ["bash", "shell scripting", "shell script"],
    },
    "Web & Frontend": {
        "HTML": ["html", "html5"],
        "CSS": ["css", "css3"],
        "React": ["react", "react.js", "reactjs"],
        "Angular": ["angular", "angularjs"],
        "Vue": ["vue", "vue.js", "vuejs"],
        "Next.js": ["next.js", "nextjs"],
        "Tailwind CSS": ["tailwind", "tailwindcss"],
        "Bootstrap": ["bootstrap"],
        "jQuery": ["jquery"],
    },
    "Backend & Frameworks": {
        "Flask": ["flask"],
        "Django": ["django"],
        "FastAPI": ["fastapi"],
        "Spring Boot": ["spring boot", "springboot"],
        "Spring": ["spring", "spring framework", "spring mvc"],
        "Hibernate": ["hibernate"],
        "Node.js": ["node.js", "nodejs", "node"],
        "Express": ["express", "express.js", "expressjs"],
        ".NET": [".net", "dotnet", "asp.net"],
        "REST API": ["rest", "restful", "rest api", "rest apis", "restful api"],
        "GraphQL": ["graphql"],
        "Microservices": ["microservices", "microservice"],
        "JWT": ["jwt", "json web token"],
        "OAuth": ["oauth", "oauth2"],
    },
    "Databases": {
        "MySQL": ["mysql"],
        "PostgreSQL": ["postgresql", "postgres"],
        "SQLite": ["sqlite"],
        "MongoDB": ["mongodb", "mongo"],
        "Redis": ["redis"],
        "Oracle": ["oracle db", "oracle database", "pl/sql"],
        "SQL Server": ["sql server", "mssql"],
        "Elasticsearch": ["elasticsearch", "elastic search"],
    },
    "Data & ML": {
        "Pandas": ["pandas"],
        "NumPy": ["numpy"],
        "scikit-learn": ["scikit-learn", "sklearn", "scikit learn"],
        "TensorFlow": ["tensorflow"],
        "PyTorch": ["pytorch"],
        "Machine Learning": ["machine learning", "ml"],
        "Deep Learning": ["deep learning"],
        "NLP": ["nlp", "natural language processing"],
        "Data Analysis": ["data analysis", "data analytics"],
        "Data Visualization": ["data visualization", "data visualisation", "matplotlib", "seaborn"],
        "Tableau": ["tableau"],
        "Power BI": ["power bi", "powerbi"],
        "Spark": ["spark", "pyspark", "apache spark"],
        "ETL": ["etl"],
    },
    "DevOps & Cloud": {
        "Git": ["git"],
        "GitHub": ["github"],
        "Docker": ["docker"],
        "Kubernetes": ["kubernetes", "k8s"],
        "AWS": ["aws", "amazon web services"],
        "Azure": ["azure"],
        "GCP": ["gcp", "google cloud"],
        "CI/CD": ["ci/cd", "cicd", "continuous integration", "continuous delivery"],
        "Jenkins": ["jenkins"],
        "GitHub Actions": ["github actions"],
        "Terraform": ["terraform"],
        "Linux": ["linux", "unix"],
        "Nginx": ["nginx"],
        "Maven": ["maven"],
        "Gradle": ["gradle"],
    },
    "Testing & Practices": {
        "Unit Testing": ["unit testing", "unit tests", "unit test"],
        "pytest": ["pytest"],
        "JUnit": ["junit"],
        "Selenium": ["selenium"],
        "Postman": ["postman"],
        "TDD": ["tdd", "test-driven development", "test driven development"],
        "Agile": ["agile", "scrum", "kanban"],
        "OOP": ["oop", "object-oriented", "object oriented"],
        "Data Structures": ["data structures"],
        "Algorithms": ["algorithms"],
        "System Design": ["system design"],
        "Design Patterns": ["design patterns"],
    },
    "Security": {
        "Cybersecurity": ["cybersecurity", "cyber security", "information security", "infosec"],
        "Penetration Testing": ["penetration testing", "pentesting", "pen testing"],
        "OWASP": ["owasp"],
        "SIEM": ["siem", "splunk"],
        "Spring Security": ["spring security"],
    },
}


def flat_skills():
    """Return {canonical_skill: (category, [aliases])}."""
    flat = {}
    for category, skills in SKILL_CATEGORIES.items():
        for name, aliases in skills.items():
            flat[name] = (category, aliases)
    return flat


def category_of(skill):
    return flat_skills().get(skill, ("Other", []))[0]
