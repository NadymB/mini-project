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
    "Data Engineer / Scientist/ Analyst": ["data engineer", "etl", "data pipeline", "data", "big data", "scientist", "data analyst", "data analysis", "phan tich du lieu", "ky su du lieu", "du lieu", "khoa hoc du lieu", "khoa hoc" ],
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
MAX_PAGE = 10
OUTPUT_FILE = "data/raw/data.csv"
# Cookie storage
OUTPUT_STATE = "data/raw/topdev_google.json"
