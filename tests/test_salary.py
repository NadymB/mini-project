from src.cleaning.salary_cleaner import clean_salary

def test_range():
    assert clean_salary("10 - 20 triệu") == (10000000.0, 20000000.0, 'VND')
    assert clean_salary("$1,000 - $1,200") == (1000.0, 1200.0, 'USD')
    assert clean_salary("$1.000 - $1.200") == (1000.0, 1200.0, 'USD')
    assert clean_salary("Từ 20 - 30 triệu") == (20000000.0, 30000000.0, 'VND')
    assert  clean_salary("10,000,000 - 14,000,000 USD") == (10000000.0, 14000000.0, 'USD')

def test_min():
    assert clean_salary("Trên 20 triệu") == (20000000.0, None, 'VND')
    assert clean_salary("From 2,000$") == (2000.0, None, 'USD')
    assert clean_salary("Từ 12 triệu") == (12000000.0, None, 'VND')

def test_max():
    assert clean_salary("Up to 2,000$") == (0.0, 2000.0, 'USD')
    assert clean_salary("Lên đến 30 triệu") == (0.0, 30000000.0, 'VND')
    assert clean_salary("Tới 40 triệu") == (0.0, 40000000.0, 'VND')
    # assert clean_salary("Tới 27.5 triệu") == (0.0, 27500000.0, 'VND')
    assert  clean_salary("Tới 30,000,000 USD") == (0.0, 30000000.0, 'USD')

def test_negotiation():
    assert clean_salary("Thoả thuận") == (None, None, None)
    assert clean_salary("Thỏa thuận") == (None, None, None)
    assert clean_salary("Thoa thuan") == (None, None, None)
    assert clean_salary("Thương lượng") == (None, None, None)
    assert clean_salary("Thương lượng") == (None, None, None)

def test_normal():
    assert clean_salary('Lương 18 triệu đồng') == (18000000.0, 18000000.0, 'VND')
    assert clean_salary('Salary: 1000$') == (1000.0, 1000.0, 'USD')
    assert clean_salary("20 triệu") == (20000000.0, 20000000.0, 'VND')