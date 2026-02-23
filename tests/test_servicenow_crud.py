"""
Unit tests for the ServiceNow CRUD client.

All HTTP calls are mocked so no real ServiceNow instance is required.
"""

import json
import pytest
import responses

from servicenow_crud import ServiceNowClient


INSTANCE = "test"
BASE_URL = "https://test.service-now.com"
TABLE = "incident"
SYS_ID = "abc123"


@pytest.fixture
def client():
    return ServiceNowClient(instance=INSTANCE, username="admin", password="secret")


@pytest.fixture
def token_client():
    return ServiceNowClient(instance=INSTANCE, token="mytoken")


# ---------------------------------------------------------------------------
# Initialisation
# ---------------------------------------------------------------------------

class TestInit:
    def test_basic_auth_credentials_stored(self):
        c = ServiceNowClient(instance=INSTANCE, username="u", password="p")
        assert c.session.auth is not None

    def test_token_auth_header_set(self, token_client):
        assert token_client.session.headers.get("Authorization") == "Bearer mytoken"

    def test_full_url_instance(self):
        c = ServiceNowClient(
            instance="https://custom.service-now.com", username="u", password="p"
        )
        assert c.base_url == "https://custom.service-now.com"

    def test_instance_name_builds_url(self, client):
        assert client.base_url == BASE_URL

    def test_no_credentials_raises(self):
        with pytest.raises(ValueError):
            ServiceNowClient(instance=INSTANCE)

    def test_username_only_raises(self):
        with pytest.raises(ValueError):
            ServiceNowClient(instance=INSTANCE, username="u")

    def test_password_only_raises(self):
        with pytest.raises(ValueError):
            ServiceNowClient(instance=INSTANCE, password="p")

    def test_content_type_header(self, client):
        assert client.session.headers["Content-Type"] == "application/json"


# ---------------------------------------------------------------------------
# Create
# ---------------------------------------------------------------------------

class TestCreate:
    @responses.activate
    def test_create_posts_to_table(self, client):
        record = {"sys_id": SYS_ID, "short_description": "Test incident"}
        responses.add(
            responses.POST,
            f"{BASE_URL}/api/now/table/{TABLE}",
            json={"result": record},
            status=201,
        )

        result = client.create(TABLE, {"short_description": "Test incident"})

        assert result == record
        assert responses.calls[0].request.method == "POST"

    @responses.activate
    def test_create_raises_on_http_error(self, client):
        responses.add(
            responses.POST,
            f"{BASE_URL}/api/now/table/{TABLE}",
            json={"error": {"message": "Forbidden"}},
            status=403,
        )

        with pytest.raises(Exception):
            client.create(TABLE, {})


# ---------------------------------------------------------------------------
# Read
# ---------------------------------------------------------------------------

class TestRead:
    @responses.activate
    def test_read_single_record(self, client):
        record = {"sys_id": SYS_ID, "short_description": "Hello"}
        responses.add(
            responses.GET,
            f"{BASE_URL}/api/now/table/{TABLE}/{SYS_ID}",
            json={"result": record},
            status=200,
        )

        result = client.read(TABLE, sys_id=SYS_ID)

        assert result == record

    @responses.activate
    def test_read_list_of_records(self, client):
        records = [{"sys_id": "1"}, {"sys_id": "2"}]
        responses.add(
            responses.GET,
            f"{BASE_URL}/api/now/table/{TABLE}",
            json={"result": records},
            status=200,
        )

        result = client.read(TABLE)

        assert result == records

    @responses.activate
    def test_read_with_query_and_fields(self, client):
        responses.add(
            responses.GET,
            f"{BASE_URL}/api/now/table/{TABLE}",
            json={"result": []},
            status=200,
        )

        client.read(
            TABLE,
            query="active=true",
            fields=["sys_id", "short_description"],
            limit=10,
            offset=0,
        )

        req = responses.calls[0].request
        assert "sysparm_query=active%3Dtrue" in req.url
        assert "sysparm_fields=sys_id%2Cshort_description" in req.url
        assert "sysparm_limit=10" in req.url
        assert "sysparm_offset=0" in req.url

    @responses.activate
    def test_read_raises_on_http_error(self, client):
        responses.add(
            responses.GET,
            f"{BASE_URL}/api/now/table/{TABLE}",
            json={"error": {"message": "Not found"}},
            status=404,
        )

        with pytest.raises(Exception):
            client.read(TABLE)


# ---------------------------------------------------------------------------
# Update
# ---------------------------------------------------------------------------

class TestUpdate:
    @responses.activate
    def test_update_patches_record(self, client):
        updated = {"sys_id": SYS_ID, "short_description": "Updated"}
        responses.add(
            responses.PATCH,
            f"{BASE_URL}/api/now/table/{TABLE}/{SYS_ID}",
            json={"result": updated},
            status=200,
        )

        result = client.update(TABLE, SYS_ID, {"short_description": "Updated"})

        assert result == updated
        assert responses.calls[0].request.method == "PATCH"

    @responses.activate
    def test_update_raises_on_http_error(self, client):
        responses.add(
            responses.PATCH,
            f"{BASE_URL}/api/now/table/{TABLE}/{SYS_ID}",
            status=500,
        )

        with pytest.raises(Exception):
            client.update(TABLE, SYS_ID, {})


# ---------------------------------------------------------------------------
# Delete
# ---------------------------------------------------------------------------

class TestDelete:
    @responses.activate
    def test_delete_sends_delete_request(self, client):
        responses.add(
            responses.DELETE,
            f"{BASE_URL}/api/now/table/{TABLE}/{SYS_ID}",
            status=204,
        )

        client.delete(TABLE, SYS_ID)

        assert responses.calls[0].request.method == "DELETE"

    @responses.activate
    def test_delete_raises_on_http_error(self, client):
        responses.add(
            responses.DELETE,
            f"{BASE_URL}/api/now/table/{TABLE}/{SYS_ID}",
            status=403,
        )

        with pytest.raises(Exception):
            client.delete(TABLE, SYS_ID)


# ---------------------------------------------------------------------------
# Token auth integration
# ---------------------------------------------------------------------------

class TestTokenAuth:
    @responses.activate
    def test_bearer_token_sent_in_header(self, token_client):
        responses.add(
            responses.GET,
            f"{BASE_URL}/api/now/table/{TABLE}",
            json={"result": []},
            status=200,
        )

        token_client.read(TABLE)

        assert responses.calls[0].request.headers["Authorization"] == "Bearer mytoken"
