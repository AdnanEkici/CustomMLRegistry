from __future__ import annotations

import json


def load_test_cases(file_path: str, key: str):
    """Load test cases from a JSON file dynamically."""
    with open(file_path) as f:
        data = json.load(f)

    test_cases = []
    for case in data[key]:
        # Extract values dynamically
        case_tuple = tuple(case.get(k) for k in case.keys())
        test_cases.append(case_tuple)

    return test_cases
