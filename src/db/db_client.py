from sqlalchemy import create_engine
import urllib.parse

def get_engine_pg(user, password, host, port, dbname):
    return create_engine(f"postgresql://{user}:{urllib.parse.quote_plus(password)}@{host}:{port}/{dbname}")

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


    