from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import Table, MetaData
import pandas as pd

def get_engine_pg():
    load_dotenv()
    db_url = os.getenv("DATABASE_URL")
    return create_engine(db_url)

def upsert_df_to_db(df, engine, table_name, conflict_cols=None, create_table_sql=None):
    metadata = MetaData()

    with engine.begin() as conn:
        if create_table_sql is not None:
            conn.execute(create_table_sql)
        # 🔥 Reflect schema
        table = Table(
            table_name,
            metadata,
            autoload_with=conn
        )
        records = df.to_dict(orient="records")
        stmt = insert(table).values(records)
        if conflict_cols:
            stmt = stmt.on_conflict_do_nothing(index_elements=conflict_cols)
        conn.execute(stmt)

def load_data_from_db(query, engine):
    return pd.read_sql(query, engine)