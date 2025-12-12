from src.pipeline.etl import run_etl
from src.db.db_client import get_engine_pg
from dotenv import load_dotenv
import os

if __name__ == "__main__":
    load_dotenv()
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')
    host = os.getenv('POSTGRES_HOST')
    port = os.getenv('POSTGRES_PORT')
    dbname = os.getenv('POSTGRES_DB')

    #write to Postgres, configure and pass engine:
    engine = get_engine_pg(user, password, host, port, dbname)
    run_etl(db_engine=engine)
