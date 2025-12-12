from src.cleaning.title_job_standardizer import standardize_title_job

def test_standardize_title_job():
    assert standardize_title_job("Backend Developer (Golang)") == "Software Engineer"
    assert standardize_title_job("QC Engineer") == "Quality Assurance"
    assert standardize_title_job("Tester Automation") == "Quality Assurance"
    assert standardize_title_job("Business Analyst (Middle/Senior)") == "Business Analyst"
    assert standardize_title_job("Project Manager (Base Tech - Upto 55M)") == "Project Manager"
    assert standardize_title_job("Chuyên Viên Data Engineer Từ 3 Yoe ( Tiếng Anh Giao Tiếp Tốt ) Offer Upto $2000") == "Data Engineer"