from typing import List

def time_to_minutes(time_str: str) -> int:
    h, m = map(int, time_str.split(':'))
    return h * 60 + m

def is_overlapping(hours_a: List[str], hours_b: List[str]) -> bool:
    for interval_a in hours_a:
        start_a_str, end_a_str = interval_a.split('-')
        start_a = time_to_minutes(start_a_str)
        end_a = time_to_minutes(end_a_str)

        for interval_b in hours_b:
            start_b_str, end_b_str = interval_b.split('-')
            start_b = time_to_minutes(start_b_str)
            end_b = time_to_minutes(end_b_str)

            if max(start_a, start_b) < min(end_a, end_b):
                return True
    return False

def get_max_weight(courier_type: str) -> float:
    limits = {
        "foot": 10.0,
        "bike": 20.0,
        "car": 40.0
    }
    return limits.get(courier_type, 0.0)

