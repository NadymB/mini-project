from src.pipeline.etl import run_etl
from src.db.db_client import get_engine_pg

if __name__ == "__main__":
    #write to Postgres, configure and pass engine:
    engine = get_engine_pg()
    run_etl(db_engine=engine)
