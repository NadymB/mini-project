import pandas as pd
import os
import json
from src.cleaning.salary_cleaner import clean_salary
from src.cleaning.address_parser import parse_locations
from src.cleaning.title_job_standardizer import standardize_title_job
from src.utils.logger import get_logger
from dotenv import load_dotenv
from src.discord.notify_jobs import notify_discord
from src.discord.built_etl_summary import built_etl_summary
from src.db.command_sql import CREATE_CLEANED_JOBS_TABLE_SQL, READ_RAWS_JOBS_TABLE_QUERY_SQL
from src.db.db_client import load_data_from_db

with open("data/raw/vietnam-provinces.json", "r", encoding="utf-8") as f:
    PROVINCES = json.load(f)

logger = get_logger(__name__)
os.makedirs("data/interim", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

load_dotenv()
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

def transform(df):
    # normalize col names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')

    before = len(df)
    # 🔥 remove duplicate jobs
    df = df.drop_duplicates(
        subset=['job_title', 'company', 'salary'],
        keep='first'
    )

    logger.info(f"Removed duplicates: {before - len(df)}")
    logger.info(f"Rows after dedup: {len(df)}")

    # salary
    df[['min_salary','max_salary','salary_unit']] = df['salary'].apply(
        lambda x: pd.Series(clean_salary(x))
    )
    # remove salary data invalid
    mask_invalid = (
            (df['salary_unit'] == 'USD') &
            ((df['min_salary'] > 100000) | (df['max_salary'] > 100000))
    )

    # Move mask_invalid to removed_invalid_salary.csv
    removed_rows = df[mask_invalid]
    os.makedirs("data/invalid", exist_ok=True)
    removed_rows.to_csv("data/invalid/invalid_salary.csv", index=False)
    # Move from df
    df = df[~mask_invalid]

    # address -> city,district
    df['address'] = df['address'].fillna('') #replace all NaN/None/missing to ''
    df[['city','district']] = df['address'].apply(lambda x: pd.Series(parse_locations(x, PROVINCES)))
    # title group
    df['job_group'] = df['job_title'].apply(standardize_title_job)

    return df

def run_etl(output_csv="data/processed/data_cleaned.csv", db_engine=None):
    try:
        df = load_data_from_db(READ_RAWS_JOBS_TABLE_QUERY_SQL ,db_engine)
        logger.info("Raw rows: %d", len(df))

        if df.empty:
            logger.info("No data in raw_jobs")
            return df
        df_trans = transform(df)
        df_trans.to_csv(output_csv, index=False)
        logger.info("Saved processed to %s", output_csv)
        # optional DB load
        if db_engine is not None:
            from src.db.db_client import upsert_df_to_db
            upsert_df_to_db(
                df_trans,
                db_engine,
                table_name="cleaned_jobs",
                conflict_cols=["url"],
                create_table_sql=CREATE_CLEANED_JOBS_TABLE_SQL
            )
            logger.info("Loaded into DB")

        if DISCORD_WEBHOOK_URL:
            df_notify = built_etl_summary(df_trans, engine=db_engine)
            notify_discord(df_notify, DISCORD_WEBHOOK_URL)
        return df_trans
    except FileNotFoundError as e:
        logger.exception("Input file not found: %s", e)
        raise
    except Exception as e:
        logger.exception("ETL failed: %s", e)
        # store bad snapshot
        df.to_csv("data/interim/bad_snapshot.csv", index=False)
        raise
