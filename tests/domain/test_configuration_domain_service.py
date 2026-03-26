from config_service.domain.services.configuration_domain_service import validate_payload


def test_valid_payload_returns_no_errors() -> None:
    payload = {
        "version": 1,
        "database": {"host": "db.local", "port": 5432},
        "features": {"enable_auth": True},
    }
    assert validate_payload(payload) == []


def test_missing_database_host_is_reported() -> None:
    payload = {"version": 1, "database": {"port": 5432}}
    errors = validate_payload(payload)
    assert any("database.host" in e for e in errors)


def test_missing_database_port_is_reported() -> None:
    payload = {"version": 1, "database": {"host": "db.local"}}
    errors = validate_payload(payload)
    assert any("database.port" in e for e in errors)


def test_missing_entire_database_key_reports_both_fields() -> None:
    payload = {"version": 1}
    errors = validate_payload(payload)
    assert len(errors) == 2


def test_empty_payload_reports_all_required_fields() -> None:
    errors = validate_payload({})
    assert len(errors) == 2
