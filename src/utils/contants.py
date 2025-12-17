from urllib.parse import quote

# Rate USD -> VND
USD_TO_VND = 26000

# Sub words in address
SUB_WORDS_ADDRESS = [
    r"tp", r"tp\.", r"thanh pho",
    r"tinh",
    r"huyen",
    r"quan",
    r"phuong",
    r"xa",
    r"thi xa",
    r"thi tran"
]

# Job title map
JOB_TITLE_MAP = {
    "Software Engineer": ["software engineer", "developer", "programmer", "lap trinh", "dev", "frontend", "ky su", "devops"],
    "Product Manager / Business Analyst": ["business analyst", "business analysis", "product manager", "business", "phan tich kinh doanh"],
    "Data Engineer": ["data engineer", "etl", "data pipeline", "big data", "ky su du lieu"],
    "Data Scientist / Analyst": ["scientist", "khoa hoc du lieu", "khoa hoc", "data analyst", "data analysis", "phan tich du lieu"],
    "Project Manager": ["pm", "project manager", "product owner", "po", "quan ly du an"],
    "Quality Assurance / Tester": ["qc", "tester", "qa", "kiem thu", "kiem soat", "quality assurance", "quality control"],
    "Network Engineer / Cyber Security Expert": ["cybersecurity", "cyber", "security", "an toan", "systems", "system", "he thong", "IT", "cong nghe thong tin", "network", "administration", "quan tri", "ket noi"],
    "Machine Learning / AI Engineer": ["ai", "artificial intelligence", "tri tue nhan tao", "machine learning", "ml", "hoc may", "may hoc"],
    "UI/UX Designer": ["designer", "ui", "ux", "ui/ux"]
}

# URL to crawl
BASE_URL = "https://topdev.vn/jobs/search"
# Query param by job categories
job_categories = [2,3,4,5,6,7,8,9,10,11,12,13,67]
query = f"?job_categories_ids={quote(','.join(map(str, job_categories)))}"
CRAWL_URL = BASE_URL + query
MAX_PAGE = 10
RAW_DATA_FILE = "data/raw/data.csv"

# Cookie storage
COOKIES_TOPDEV_FILE = "data/raw/topdev_google.json"

#Notified jobs
NOTIFIED_JOBS_FILE = "data/state/notified_jobs.json"

#Summary system prompt on groq
SUMMARY_SYSTEM_PROMPT = """
You are a senior tech recruiter.
Summarize the following Job Description into 4–5 concise bullet points.
Focus on:
- Responsibilities
- Tech stack
- Experience requirements
- Important notes

Keep it short, clear, and recruiter-friendly.
"""

