import json
from pathlib import Path

import pytest

CASES = Path(__file__).resolve().parent / "goldens" / "cases.json"


def load_cases():
    data = json.loads(CASES.read_text(encoding="utf-8"))
    return [c for c in data["cases"] if c.get("api") == "getvoleq_r"]


@pytest.fixture(scope="session")
def golden_cases():
    return json.loads(CASES.read_text(encoding="utf-8"))["cases"]


@pytest.mark.parametrize("case", load_cases(), ids=lambda c: c["name"])
def test_getvoleq_golden(nvel, case):
    inp = case["inputs"]
    exp = case["expected"]
    volume_equation = nvel.get_voleq(
        region=inp["region"],
        forest=inp["forest"],
        district=inp["district"],
        species=inp["species"],
    )
    assert volume_equation == exp["voleq"]
