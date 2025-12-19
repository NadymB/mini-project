from datetime import datetime, timedelta
from src.ai.jd_summarizer import summarize_jd
import pandas as pd
from src.db.db_client import upsert_df_to_db
from src.utils.logger import get_logger
from src.db.command_sql import CREATE_NOTIFIED_JOBS_TABLE_SQL
from sqlalchemy import inspect

logger = get_logger(__name__)

def build_job_key(row):
    return f"{row['job_title']}|{row['company']}|{row['address']}|{row['salary']}".lower()

def built_etl_summary(df_final, engine):
    df = df_final.copy()

    df['created_date'] = pd.to_datetime(df['created_date'], errors='coerce')

    df = df[
        (df['job_group'] == "Data Engineer") &
        (df['created_date'] >= datetime.now() - timedelta(days=7))
        ].copy()

    if df.empty:
        return df

    df["job_key"] = df.apply(build_job_key, axis=1)

    # 🔍 check notified_jobs exists
    inspector = inspect(engine)

    if inspector.has_table("notified_jobs"):
        existing_keys = pd.read_sql(
            "SELECT job_key FROM notified_jobs",
            engine
        )["job_key"].tolist()
    else:
        existing_keys = []

    # Only get new jobs
    new_df = df[~df["job_key"].isin(existing_keys)].copy()

    if new_df.empty:
        logger.info("No new jobs to notify")
        return new_df

    # New jobs exist -> apply summarize_jd def
    new_df["jd_summary"] = new_df["jd"].apply(summarize_jd)

    inserted = upsert_df_to_db(
        new_df[[
            "job_key",
            "job_group",
            "company",
            "address",
            "salary",
            "jd_summary",
            "url"
        ]],
        engine,
        table_name="notified_jobs",
        conflict_cols=["job_key"],
        create_table_sql=CREATE_NOTIFIED_JOBS_TABLE_SQL
    )

    logger.info("New Discord notifications: %d", inserted)

    return new_df

