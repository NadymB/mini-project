import json

from src.cleaning.address_parser import parse_locations

with open("data/raw/vietnam-provinces.json", "r", encoding="utf-8") as f:
    PROVINCES = json.load(f)

def test_address():
    assert parse_locations("Hà Nội: Thanh Xuân", PROVINCES) == ("Thành phố Hà Nội", "Quận Thanh Xuân")
    assert parse_locations("Hồ Chí Minh: Phú Nhuận", PROVINCES) == ("Thành phố Hồ Chí Minh", "Quận Phú Nhuận")
    assert parse_locations("Hồ Chí Minh", PROVINCES) == ("Thành phố Hồ Chí Minh", None)
    assert parse_locations("Cần Thơ: Cái Răng", PROVINCES) == ("Thành phố Cần Thơ", "Quận Cái Răng")
    assert parse_locations("Hồ Chí Minh: Quận 7", PROVINCES) == ("Thành phố Hồ Chí Minh", "Quận 7")
    assert parse_locations("Thừa Thiên Huế: TP Huế", PROVINCES) == ("Tỉnh Thừa Thiên Huế", "Thành phố Huế")
    assert parse_locations("Hồ Chí Minh: Thủ Đức: Đà Nẵng: Thanh Khê: Thừa Thiên Huế: TP Huế", PROVINCES) == ('Thành phố Hồ Chí Minh', 'Quận Thủ Đức')
    assert parse_locations("Hà Nội: Hồ Chí Minh: Đà Nẵng", PROVINCES) == ("Thành phố Hà Nội", None)
    assert parse_locations("Khánh Hoà: TP Nha Trang", PROVINCES) == ("Tỉnh Khánh Hòa", "Thành phố Nha Trang")
    assert parse_locations("Đà Nẵng: Ngũ Hành Sơn", PROVINCES) == ("Thành phố Đà Nẵng", "Quận Ngũ Hành Sơn")
    assert parse_locations("Đồng Nai: Trảng Bom", PROVINCES) == ("Tỉnh Đồng Nai", "Huyện Trảng Bom")