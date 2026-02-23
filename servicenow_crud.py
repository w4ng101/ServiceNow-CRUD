"""
ServiceNow CRUD client for the ServiceNow Table REST API.

Provides Create, Read, Update, and Delete operations against any
ServiceNow table using basic authentication or OAuth bearer tokens.
"""

import requests
from requests.auth import HTTPBasicAuth


class ServiceNowClient:
    """Client for performing CRUD operations on ServiceNow tables."""

    def __init__(self, instance, username=None, password=None, token=None):
        """
        Initialise the ServiceNow client.

        Args:
            instance (str): ServiceNow instance name (e.g. 'mycompany') or
                            full base URL (e.g. 'https://mycompany.service-now.com').
            username (str, optional): Username for basic authentication.
            password (str, optional): Password for basic authentication.
            token (str, optional): OAuth bearer token for token-based auth.

        Raises:
            ValueError: If neither (username + password) nor token is provided.
        """
        if not token and not (username and password):
            raise ValueError(
                "Either (username and password) or token must be provided."
            )

        if instance.startswith("http://") or instance.startswith("https://"):
            self.base_url = instance.rstrip("/")
        else:
            self.base_url = f"https://{instance}.service-now.com"

        self.session = requests.Session()
        self.session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )

        if token:
            self.session.headers.update({"Authorization": f"Bearer {token}"})
        else:
            self.session.auth = HTTPBasicAuth(username, password)

    def _table_url(self, table, sys_id=None):
        url = f"{self.base_url}/api/now/table/{table}"
        if sys_id:
            url = f"{url}/{sys_id}"
        return url

    def create(self, table, data):
        """
        Create a new record in a ServiceNow table.

        Args:
            table (str): Table name (e.g. 'incident').
            data (dict): Field values for the new record.

        Returns:
            dict: The created record returned by ServiceNow.

        Raises:
            requests.HTTPError: If the request fails.
        """
        response = self.session.post(self._table_url(table), json=data)
        response.raise_for_status()
        return response.json().get("result", {})

    def read(self, table, sys_id=None, query=None, fields=None, limit=None, offset=None):
        """
        Read one or more records from a ServiceNow table.

        Args:
            table (str): Table name (e.g. 'incident').
            sys_id (str, optional): sys_id of a specific record to fetch.
            query (str, optional): Encoded query string (sysparm_query).
            fields (list[str], optional): Fields to return (sysparm_fields).
            limit (int, optional): Maximum number of records (sysparm_limit).
            offset (int, optional): Pagination offset (sysparm_offset).

        Returns:
            dict | list[dict]: A single record dict when sys_id is provided,
                               or a list of record dicts otherwise.

        Raises:
            requests.HTTPError: If the request fails.
        """
        params = {}
        if query:
            params["sysparm_query"] = query
        if fields:
            params["sysparm_fields"] = ",".join(fields)
        if limit is not None:
            params["sysparm_limit"] = limit
        if offset is not None:
            params["sysparm_offset"] = offset

        response = self.session.get(self._table_url(table, sys_id), params=params)
        response.raise_for_status()
        return response.json().get("result", {} if sys_id else [])

    def update(self, table, sys_id, data):
        """
        Update an existing record in a ServiceNow table.

        Args:
            table (str): Table name (e.g. 'incident').
            sys_id (str): sys_id of the record to update.
            data (dict): Field values to update.

        Returns:
            dict: The updated record returned by ServiceNow.

        Raises:
            requests.HTTPError: If the request fails.
        """
        response = self.session.patch(self._table_url(table, sys_id), json=data)
        response.raise_for_status()
        return response.json().get("result", {})

    def delete(self, table, sys_id):
        """
        Delete a record from a ServiceNow table.

        Args:
            table (str): Table name (e.g. 'incident').
            sys_id (str): sys_id of the record to delete.

        Raises:
            requests.HTTPError: If the request fails.
        """
        response = self.session.delete(self._table_url(table, sys_id))
        response.raise_for_status()
