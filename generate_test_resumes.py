"""Скрипт для автоматичної генерації тестових .docx резюме у папці resumes/."""

import os
from docx import Document

RESUMES_DIR = "resumes"

candidates = [
    {
        "filename": "01_strong_senior_dev.docx",
        "content": """
        Ivan Petrenko
        Senior Python Developer
        Email: ivan.petrenko.dev@gmail.com | Phone: +380501112233
        
        Summary:
        Highly skilled Senior Python Developer with 7+ years of experience building scalable web applications, REST APIs, and microservices. Expert in Python, Django, FastAPI, PostgreSQL, Docker, and AWS.
        
        Experience:
        - Lead Backend Developer at TechCorp (2021 - Present)
          - Designed and implemented high-load microservices using FastAPI and PostgreSQL.
          - Optimized database queries, reducing response time by 40%.
          - Mentored junior and middle developers, conducted code reviews.
        - Python Developer at SoftSolutions (2018 - 2021)
          - Developed RESTful APIs using Django and Django REST Framework.
          - Integrated CI/CD pipelines with GitHub Actions and Docker.
          
        Skills:
        Python, FastAPI, Django, PostgreSQL, Docker, AWS, Git, Celery, Redis, CI/CD, Kubernetes.
        
        Education:
        Master's degree in Computer Science, National University of Kyiv (2018).
        """
    },
    {
        "filename": "02_strong_architect.docx",
        "content": """
        Maria Kovalenko
        Principal Software Engineer / Tech Lead
        Email: m.kovalenko@example.com | Phone: +380672223344
        
        Summary:
        Architect and senior developer with 9 years of commercial experience. Strong background in Python ecosystem, cloud infrastructure (AWS/GCP), system design, and team leadership.
        
        Experience:
        - Tech Lead at Enterprise Solutions (2020 - Present)
          - Led a team of 8 engineers delivering fintech products.
          - Architected event-driven systems using Python, Kafka, and PostgreSQL.
        - Senior Backend Engineer at DataSystems (2016 - 2020)
          - Built robust backend services with Django and Flask.
          - Managed database scaling and performance tuning.
          
        Skills:
        Python, Django, FastAPI, PostgreSQL, AWS, Kafka, Docker, Kubernetes, System Design, Leadership.
        
        Education:
        Bachelor's in Software Engineering, KPI (2016).
        """
    },
    {
        "filename": "03_strong_backend.docx",
        "content": """
        Oleksandr Bondar
        Senior Backend Developer
        Email: o.bondar.Dev@gmail.com | Phone: +380933334455
        
        Summary:
        Senior Backend Engineer specialized in Python, distributed systems, and cloud-native development with 6 years of hands-on experience.
        
        Experience:
        - Senior Python Dev at CloudScale (2019 - Present)
          - Built scalable REST APIs and background workers using Celery and Redis.
          - Implemented robust testing suites with Pytest.
        - Software Developer at WebDev Studio (2018 - 2019)
          - Developed web apps using Python and Flask.
          
        Skills:
        Python, FastAPI, Flask, PostgreSQL, Redis, Docker, Pytest, Git, AWS.
        
        Education:
        Bachelor's in Applied Mathematics, Lviv Polytechnic (2018).
        """
    },
    {
        "filename": "04_middle_python.docx",
        "content": """
        Dmytro Melnyk
        Middle Python Developer
        Email: d.melnyk@ukr.net | Phone: +380504445566
        
        Summary:
        Middle Python developer with 3 years of experience in web development, API integration, and database management.
        
        Experience:
        - Python Developer at StartupHub (2022 - Present)
          - Developed backend endpoints using Django REST Framework.
          - Worked with PostgreSQL and wrote unit tests.
        - Junior Developer at WebSoft (2021 - 2022)
          - Assisted in maintaining legacy Python scripts and databases.
          
        Skills:
        Python, Django, PostgreSQL, Git, Docker, REST API.
        
        Education:
        Bachelor's in Computer Science, Kharkiv National University (2021).
        """
    },
    {
        "filename": "05_middle_fullstack.docx",
        "content": """
        Yuliia Shevchenko
        Fullstack Developer (Python / JavaScript)
        Email: yuliia.sh@gmail.com | Phone: +380675556677
        
        Summary:
        Fullstack developer with 3.5 years of professional experience focusing on Python backend and React frontend.
        
        Experience:
        - Fullstack Dev at DigitalAgency (2022 - Present)
          - Built web applications using Python (Flask/FastAPI) and React.
          - Integrated third-party payment gateways and REST APIs.
          
        Skills:
        Python, FastAPI, Flask, JavaScript, React, PostgreSQL, Git.
        
        Education:
        Master's in Economics and IT, Kyiv Taras Shevchenko University (2022).
        """
    },
    {
        "filename": "06_middle_data_engineer.docx",
        "content": """
        Andrii Boyko
        Data Engineer / Python Developer
        Email: andrii.boyko.data@gmail.com | Phone: +380936667788
        
        Summary:
        Data engineer with 4 years of experience building ETL pipelines, working with big data tools, and writing robust Python code.
        
        Experience:
        - Data Engineer at DataCorp (2022 - Present)
          - Developed ETL pipelines using Python, Pandas, and PostgreSQL.
          - Automated data ingestion from various APIs.
          
        Skills:
        Python, Pandas, SQL, PostgreSQL, Airflow, Docker, Git.
        
        Education:
        Bachelor's in Cybernetics, KPI (2020).
        """
    },
    {
        "filename": "07_middle_support.docx",
        "content": """
        Serhii Tkachenko
        Python Support Engineer
        Email: s.tkachenko@gmail.com | Phone: +380507778899
        
        Summary:
        Python support and maintenance specialist with 3 years of experience troubleshooting backend issues and writing small automation scripts.
        
        Experience:
        - Support Engineer at IT Service Group (2023 - Present)
          - Resolved client issues related to web application performance.
          - Maintained Python automation scripts.
          
        Skills:
        Python, Linux, Bash, SQL, Git.
        
        Education:
        Bachelor's in IT, Vinnytsia National Technical University (2023).
        """
    },
    {
        "filename": "08_junior_dev.docx",
        "content": """
        Victoria Moroz
        Junior Python Developer
        Email: v.moroz.junior@gmail.com | Phone: +380678889900
        
        Summary:
        Junior Python developer who recently completed intensive bootcamp and pet projects. Eager to grow in a professional backend team.
        
        Experience:
        - Trainee / Junior at Freelance (2025 - Present)
          - Built simple Telegram bots and web scrapers using Python and BeautifulSoup.
          
        Skills:
        Python, Git, SQLite, Basic SQL, HTML/CSS.
        
        Education:
        Student at Computer Science faculty, Kyiv Polytechnic (Expected 2027).
        """
    },
    {
        "filename": "09_frontend_only.docx",
        "content": """
        Denys Lysenko
        Frontend Developer (React / Vue)
        Email: denys.frontend@gmail.com | Phone: +380939990011
        
        Summary:
        Frontend developer with 4 years of experience specializing in single-page applications using React, TypeScript, and modern CSS frameworks. No backend Python experience.
        
        Experience:
        - Frontend Developer at WebArt (2022 - Present)
          - Developed UI components with React and Redux.
          
        Skills:
        JavaScript, TypeScript, React, Redux, HTML, CSS, Tailwind.
        
        Education:
        Bachelor's in Design, Kharkiv Academy of Design (2022).
        """
    },
    {
        "filename": "10_irrelevant_candidate.docx",
        "content": """
        Tetiana Koval
        Account Manager / Sales Specialist
        Email: tetiana.sales@gmail.com | Phone: +380500001122
        
        Summary:
        Experienced sales and account management professional with 5 years of experience in B2B client communications, contract negotiation, and customer support.
        
        Experience:
        - Account Manager at TradeGlobal (2021 - Present)
          - Managed key client accounts, increased sales retention by 20%.
          
        Skills:
        Client Communication, B2B Sales, CRM, Negotiation, Excel, English (C1).
        
        Education:
        Bachelor's in International Relations, Kyiv Linguistic University (2021).
        """
    }
]

def create_resumes():
    os.makedirs(RESUMES_DIR, exist_ok=True)
    for candidate in candidates:
        filepath = os.path.join(RESUMES_DIR, candidate["filename"])
        doc = Document()
        for line in candidate["content"].strip().split("\n"):
            doc.add_paragraph(line.strip())
        doc.save(filepath)
        print(f"Створено: {filepath}")

if __name__ == "__main__":
    create_resumes()
    print("Усі 10 тестових резюме успішно згенеровано!")