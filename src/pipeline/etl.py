import pandas as pd
from src.cleaning.salary_cleaner import clean_salary
from src.cleaning.address_parser import parse_locations
from src.cleaning.title_job_standardizer import standardize_title_job
from src.utils.logger import get_logger
import os
import json
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta

with open("data/raw/vietnam-provinces.json", "r", encoding="utf-8") as f:
    PROVINCES = json.load(f)

logger = get_logger(__name__)
os.makedirs("data/interim", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

load_dotenv()
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
logger.info("webhook_url", DISCORD_WEBHOOK_URL)

def notify_discord(df, webhook_url):
    """
    Send ALL jobs to Discord (auto split by Discord limit)
    """
    if df.empty:
        logger.info("No data to notify Discord")
        return

    header = "🔥 **New Data jobs (last 7 days)** 🔥\n\n"

    chunks = []
    current = header

    for _, row in df.iterrows():
        msg = (
            f"**{row['job_title']}**\n"
            f"🏢 {row['company']}\n"
            f"📍 {row['address']}\n"
            f"🔗 {row.get('url') or row.get('description_link')}\n\n"
        )

        # if over 2000 chars -> push chunk
        if len(current) + len(msg) > 1900:
            chunks.append(current)
            current = msg
        else:
            current += msg

    # push rest of
    if current.strip():
        chunks.append(current)

    logger.info("Sending %d Discord messages", len(chunks))

    for i, content in enumerate(chunks, 1):
        payload = {"content": content}
        resp = requests.post(webhook_url, json=payload, timeout=10)

        if resp.status_code != 204:
            logger.error(
                "Discord notify failed (part %d/%d): %s - %s",
                i, len(chunks), resp.status_code, resp.text
            )
        else:
            logger.info("Discord message %d/%d sent", i, len(chunks))

def built_etl_summary(df_raw, df_final):
    # convert date
    df_final['posted_date'] = pd.to_datetime(
        df_final['posted_date'],
        errors='coerce'
    )

    one_week_ago = datetime.now() - timedelta(days=7)

    df_filtered = df_final[
        (df_final['title_group'] == "Data Engineer") &
        (df_final['posted_date'] >= one_week_ago)
        ]
    logger.info("Filtered Data jobs (last 7 days): %d rows", len(df_filtered))
    logger.info("Sample:\n%s", df_filtered.head(5))

    df_result = df_filtered[
        ['job_title', 'company', 'address', 'url']
    ]

    return df_result


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
    df[['city','district']] = df['address'].apply(lambda x: pd.Series(parse_locations(x, PROVINCES)))
    # title group
    df['title_group'] = df['job_title'].apply(standardize_title_job)
    #tech stack
    # df['tech_stack'] = df['job_title'].apply(extract_tech)
    return df

def run_etl(input_csv="data/raw/data.csv", output_csv="data/processed/data_cleaned.csv", db_engine=None):
    try:
        logger.info("Loading %s", input_csv)
        df = pd.read_csv(input_csv, header=None, names=['posted_date','job_title','company','salary','address','remain','url'])
        logger.info("Raw rows: %d", len(df))
        df_trans = transform(df)
        df_trans.to_csv(output_csv, index=False)
        logger.info("Saved processed to %s", output_csv)
        # optional DB load
        if db_engine is not None:
            from src.db.db_client import write_df_to_db
            write_df_to_db(df_trans, db_engine)
            logger.info("Loaded into DB")
        if DISCORD_WEBHOOK_URL:
            df_notify = built_etl_summary(df, df_trans)
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
