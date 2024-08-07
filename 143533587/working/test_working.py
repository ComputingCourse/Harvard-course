from working import convert
import pytest

def test_large():
    with pytest.raises(ValueError):
        convert("25 PM to 5 AM")
    with pytest.raises(ValueError):
        convert("9 AM to 13 PM")
    assert convert("12 AM to 12 PM") == "00:00 to 12:00"
    with pytest.raises(ValueError):
        convert("12:60 AM to 5:20 PM")

def test_format():
    with pytest.raises(ValueError):
        convert("9AMto13PM")

def test_work():
    assert convert("9 AM to 5 PM") == "09:00 to 17:00"
    assert convert("9:00 AM to 5:00 PM") == "09:00 to 17:00"