from core.documents import __all__

EXPECTED_ALL = ["Document"]


def test_all_imports() -> None:
    assert set(__all__) == set(EXPECTED_ALL)