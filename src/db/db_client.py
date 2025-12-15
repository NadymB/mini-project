from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

def get_engine_pg():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    return create_engine(db_url)

def write_df_to_db(df, engine, table_name="jobs"):
    with engine.begin() as conn:
        # Recreate table schema (replace) if exist -> drop table else -> create table
        df.head(0).to_sql(
            table_name,
            conn,
            if_exists="replace",
            index=False
        )

        # insert new data
        df.to_sql(
            table_name,
            conn,
            if_exists="append",
            index=False
        )


    