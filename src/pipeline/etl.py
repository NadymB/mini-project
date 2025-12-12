import pandas as pd
from src.cleaning.salary_cleaner import clean_salary
from src.cleaning.address_parser import parse_locations
from src.cleaning.title_job_standardizer import standardize_title_job
from src.utils.logger import get_logger
import os
import json

with open("data/raw/vietnam-provinces.json", "r", encoding="utf-8") as f:
    PROVINCES = json.load(f)

logger = get_logger(__name__)
os.makedirs("data/interim", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

def transform(df):
    # normalize col names
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
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
        return df_trans
    except FileNotFoundError as e:
        logger.exception("Input file not found: %s", e)
        raise
    except Exception as e:
        logger.exception("ETL failed: %s", e)
        # store bad snapshot
        df.to_csv("data/interim/bad_snapshot.csv", index=False)
        raise
