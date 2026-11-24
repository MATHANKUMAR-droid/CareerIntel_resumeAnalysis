from app.services.experience_calc import union_months

def test_overlapping_ranges_not_double_counted():
 assert union_months([(2020*12,2022*12),(2021*12,2023*12)])==36
