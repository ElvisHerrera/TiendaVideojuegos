import datetime

import db


def test_normalize_date_with_date():
    d = datetime.date(2020, 1, 2)
    assert db._normalize_date(d) == "2020-01-02"


def test_normalize_date_with_none():
    assert db._normalize_date(None) == ""


def test_row_to_dict_memoryview_and_date():
    # Simulate a RealDictCursor row with a memoryview for BYTEA and a date
    row = {
        "id": 5,
        "title": "Prueba",
        "company": "ACME",
        "release_date": datetime.date(2019, 12, 31),
        "image_data": memoryview(b"ABC"),
    }

    d = db._row_to_dict(row)

    assert isinstance(d, dict)
    assert d["id"] == 5
    assert d["title"] == "Prueba"
    # release_date should be normalized to string
    assert d["release_date"] == "2019-12-31"
    # image_data should be converted to bytes
    assert isinstance(d["image_data"], bytes)
    assert d["image_data"] == b"ABC"


def test_row_to_dict_none_returns_none():
    assert db._row_to_dict(None) is None
