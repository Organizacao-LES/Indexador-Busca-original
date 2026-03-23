from backend.app.main import root


def test_root_returns_service_status() -> None:
    assert root() == {"message": "IFESDOC API running"}
