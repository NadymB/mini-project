from sqlalchemy import text

CREATE_RAW_JOBS_TABLE_SQL = text("""
    CREATE TABLE IF NOT EXISTS raw_jobs (
        id SERIAL PRIMARY KEY,
        url TEXT UNIQUE,
        created_date DATE,
        job_title TEXT,
        company TEXT,
        salary TEXT,
        address TEXT,
        time DATE,
        jd TEXT
    );
""")

INSERT_RAW_JOBS_SQL = text("""
    INSERT INTO raw_jobs (
        created_date,
        job_title,
        company,
        salary,
        address,
        time,
        url,
        jd
    )
    VALUES (
        :created_date,
        :job_title,
        :company,
        :salary,
        :address,
        :time,
        :url,
        :jd
    )
    ON CONFLICT (url) DO NOTHING
""")

CREATE_CLEANED_JOBS_TABLE_SQL = text("""
    CREATE TABLE IF NOT EXISTS cleaned_jobs (
        id SERIAL PRIMARY KEY,
        url TEXT UNIQUE,
        created_date DATE,
        job_title TEXT,
        company TEXT,
        salary TEXT,
        address TEXT,
        time DATE,
        jd TEXT,
        min_salary FLOAT,
        max_salary FLOAT,
        salary_unit TEXT,
        city TEXT,
        district TEXT,
        job_group TEXT
    );
""")

CREATE_JOBS_TABLE_SQL = text("""
    CREATE TABLE IF NOT EXISTS jobs (
        id SERIAL PRIMARY KEY,
        url TEXT UNIQUE,
        created_date DATE,
        job_title TEXT,
        company TEXT,
        salary TEXT,
        address TEXT,
        time DATE,
        jd TEXT,
        min_salary FLOAT,
        max_salary FLOAT,
        salary_unit TEXT,
        city TEXT,
        district TEXT,
        job_group TEXT
    );
""")

CREATE_NOTIFIED_JOBS_TABLE_SQL = text("""
    CREATE TABLE IF NOT EXISTS notified_jobs (
        id SERIAL PRIMARY KEY,
        job_key TEXT UNIQUE,
        job_group TEXT,
        company TEXT,
        address TEXT,
        salary TEXT,
        jd_summary TEXT,
        url TEXT
    );
""")

# Read raw jobs table
READ_RAWS_JOBS_TABLE_QUERY_SQL = text("""
    SELECT
        created_date,
        job_title,
        company,
        salary,
        address,
        time,
        url,
        jd
    FROM raw_jobs
""")

# Calculate AVG min and max salary by title group
SALARY_QUERY_SQL = text("""
    SELECT
        job_group,
        AVG(
            CASE 
				WHEN NULLIF(min_salary, 'NaN'::float) > 0
				AND salary_unit = 'USD'
				THEN min_salary * 26000
				WHEN NULLIF(min_salary, 'NaN'::float) > 0
				THEN min_salary
				ELSE NULL
	           END
        ) AS avg_min_salary_vnd,
        AVG(
			CASE
            	WHEN NULLIF(max_salary, 'NaN'::float) > 0
             	AND salary_unit = 'USD'
		        THEN max_salary * 26000
		        WHEN NULLIF(max_salary, 'NaN'::float) > 0
		        THEN max_salary
		        ELSE NULL
            END
        ) AS avg_max_salary_vnd
    FROM cleaned_jobs
    GROUP BY job_group; 
""")

#Query job_title, job_group, city
JOBS_BY_CITY_QUERY_SQL = text("""
    SELECT job_title, job_group, city FROM cleaned_jobs;
""")

#Query tech count group by job_group
TECH_COUNT_QUERY_SQL = text("""
    SELECT
        job_group,
        COUNT(*) AS count
    FROM cleaned_jobs
    WHERE job_group IS NOT NULL
    GROUP BY job_group
    ORDER BY count DESC;
""")