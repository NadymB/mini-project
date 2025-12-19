import json

from src.cleaning.address_parser import parse_locations

with open("data/raw/vietnam-provinces.json", "r", encoding="utf-8") as f:
    PROVINCES = json.load(f)

def test_address():
    assert parse_locations("Thanh Xuân, Hà Nội", PROVINCES) == ("Thành phố Hà Nội", "Quận Thanh Xuân")
    assert parse_locations("Phú Nhuận, Hồ Chí Minh", PROVINCES) == ("Thành phố Hồ Chí Minh", "Quận Phú Nhuận")
    assert parse_locations("Hồ Chí Minh", PROVINCES) == ("Thành phố Hồ Chí Minh", None)
    assert parse_locations("Cái Răng, Cần Thơ", PROVINCES) == ("Thành phố Cần Thơ", "Quận Cái Răng")
    assert parse_locations("Quận 7, Hồ Chí Minh", PROVINCES) == ("Thành phố Hồ Chí Minh", "Quận 7")
    assert parse_locations("TP Huế, Thừa Thiên Huế", PROVINCES) == ("Tỉnh Thừa Thiên Huế", "Thành phố Huế")
    assert parse_locations("Thủ Đức, Hồ Chí Minh - Thanh Khê, Đà Nẵng - TP Huế, Thừa Thiên Huế", PROVINCES) == ('Thành phố Hồ Chí Minh', 'Quận Thủ Đức')
    assert parse_locations("Hà Nội - Hồ Chí Minh - Đà Nẵng", PROVINCES) == ("Thành phố Hà Nội", None)
    assert parse_locations("TP Nha Trang, Khánh Hoà", PROVINCES) == ("Tỉnh Khánh Hòa", "Thành phố Nha Trang")
    assert parse_locations("Ngũ Hành Sơn, Đà Nẵng", PROVINCES) == ("Thành phố Đà Nẵng", "Quận Ngũ Hành Sơn")
    assert parse_locations("Trảng Bom, Đồng Nai", PROVINCES) == ("Tỉnh Đồng Nai", "Huyện Trảng Bom")