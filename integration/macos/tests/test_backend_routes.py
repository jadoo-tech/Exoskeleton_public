from __future__ import annotations


def test_basic_routes(backend_client):
    for route in (
        "/",
        "/motionControls",
        "/dataDisplay",
        "/fetchData",
        "/exoDashboard",
        "/exoDashboard/client/test-client",
    ):
        response = backend_client.get(route)
        assert response.status_code == 200


def test_fetch_data_returns_json_list(backend_client):
    response = backend_client.get("/fetchData")
    assert response.status_code == 200
    payload = response.get_json()
    assert isinstance(payload, list)
    assert payload
