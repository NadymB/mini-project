## 📌 Overview
This project is a **mini ETL (Extract - Transform - Load) pipeline**. The goal is to crawl data from TopDev (one of the leading IT recruitment platform in Vietnam), then process, normalize, clean and store it in **PostgreSQL** for analysis. The project also integrates **AI to summarize job descriptions** for Data Engineer position and **sends notifications to Discord** so that new jobs can be easily tracked. The entire workflow is automated and maintained using **GitHub Actions (CI/CD)**.\
\
The diagram above illustrates the full data: \
\
![ETL Pipeline Diagram](assets/images/job_data_etl_pipeline_diagram.png)

## 🏗️ Architecture & Data Flow
### 1. Data Source - TopDev:
  - Data is crawled from TopDev using Playwright.
  - Raw job data includes:
      - Created date
      - Job title
      - Company
      - Address
      - Salary
      - Period time
      - Job URL
      - Job descriptions
### 2. Extract data:
  - Crawled data is stored first in PostgreSQL as raw data to:
      - Preserve original data.
      - Avoid re-crawling duplicated jobs.
      - Support reprocessing if transform logic changes.
### 3. Transform data:
  - **Pandas** is used for data transformation:
      - Remove duplicate.
      - Normalize salary data by cleaning and separating it into minimun salary, maximum salary and salary unit columns.
      - Normalize address data by parsing and separating it into city and district columns.
      - Normalize job title data by grouping similar roles to ensure data consistency.
      - Write unit tests to check the above functions.
### 4. Load data:
  - Standardized and cleaned data is **loaded back into PostgreSQL**.

### 5. AI job description summarization - Notify to Discord:
  - Create notified jobs table to store Data Engineer job records filtered from the cleaned dataset, purpose:
      - Track which jobs have already been processed.
      - Prevent duplicate notifications.
  - Using **Groq LLM API** to summary job descriptions.
  - New jobs are sent to Discord via webhook.
### 6. Analytics:
  - **Jupyter Notebook** is used for:
      - Salary trend.
      - Job by address.
      - Technology keyword insights.
### 7. CI/CD - GitHub Actions:
  - The entire pipeline is automated with **Github Actions**:
      - Scheduled runs (cron).
      - Secure secrets management (DATABSE URL, API Keys, Discord Webhook).
## 🛠️ Tech Stack
| Category | Technology |
|-----:|-----------|
|     Language| Python|
|     Crawling| Playwright|
|     Data Processing| Pandas    |
|     Database| PostgreSQL       |
|     AI Summarization| Groq API       |
|     Analytics| Jupyter Notebook       |
|     Notifications| Discord Webhook       |
|     CI/CD| GitHub Actions       |
## 🔐 Environment Variables
```
DATABASE_URL=postgresql://user:password@host:port/db
GROQ_API_KEY=your_api_key
DISCORD_WEBHOOK_URL=your_webhook_url
```
## 🚀 Key Features
  - End-to-end ETL pipeline.
  - AI powered JD summarization.
  - Automated Discord notifications.
  - CI/CD ready for production workflow.
## 📈 Future Improvements
  - Add Airflow for orchestration.
  - Introduction data warehouse (BigQuery/RedShift).
  - Dashboard visualization.
## 👨‍💻 Author
This project is built as a **learning-oriented Data Engineering mini project**, focusing ETL design, automation and integrate with AI services. 

<br/>
___
<br/>
⭐ If you find this project useful, feel free to star the repository and give feedback!
