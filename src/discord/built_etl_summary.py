from datetime import datetime, timedelta
from src.ai.jd_summarizer import summarize_jd
import pandas as pd
import os
import json
from src.utils.logger import get_logger
from src.utils.contants import NOTIFIED_JOBS_FILE

logger = get_logger(__name__)

def build_job_key(row):
    return f"{row['job_title']}|{row['company']}|{row['address']}|{row['salary']}".lower()

os.makedirs("data/state", exist_ok=True)

def load_notified_jobs():
    if not os.path.exists(NOTIFIED_JOBS_FILE):
        return set()
    with open(NOTIFIED_JOBS_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f))

def save_notified_jobs(job_keys):
    with open(NOTIFIED_JOBS_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(job_keys)), f, ensure_ascii=False, indent=2)

def built_etl_summary(df_final):
    df_final = df_final.copy()

    df_final['posted_date'] = pd.to_datetime(
        df_final['posted_date'],
        errors='coerce'
    )

    one_week_ago = datetime.now() - timedelta(days=7)

    df_filtered = df_final[
        (df_final['title_group'] == "Data Engineer") &
        (df_final['posted_date'] >= one_week_ago)
    ].copy()

    logger.info("Filtered Data jobs (last 7 days): %d rows", len(df_filtered))

    notified_keys = load_notified_jobs()

    df_filtered["job_key"] = df_filtered.apply(build_job_key, axis=1)

    df_new = df_filtered[~df_filtered["job_key"].isin(notified_keys)].copy()

    logger.info("New jobs to notify: %d", len(df_new))

    if df_new.empty:
        return df_new

    # summarize JD (CORRECT)
    df_new["jd_summary"] = df_new["jd"].apply(summarize_jd)

    # save notified
    save_notified_jobs(set(notified_keys) | set(df_new["job_key"]))

    return df_new[['job_title', 'company', 'address', 'salary', 'jd_summary', 'url']]

