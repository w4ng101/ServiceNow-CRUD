# ServiceNow-CRUD

A lightweight Python client for performing **Create, Read, Update, and Delete** (CRUD) operations against the [ServiceNow Table REST API](https://docs.servicenow.com/bundle/utah-api-reference/page/integrate/inbound-rest/concept/c_TableAPI.html).

## Requirements

- Python 3.8+
- `requests` (see `requirements.txt`)

```bash
pip install -r requirements.txt
```

## Usage

### Initialise the client

```python
from servicenow_crud import ServiceNowClient

# Basic auth
client = ServiceNowClient(
    instance="mycompany",      # → https://mycompany.service-now.com
    username="admin",
    password="secret",
)

# OAuth bearer token
client = ServiceNowClient(
    instance="mycompany",
    token="<oauth_bearer_token>",
)

# Full URL
client = ServiceNowClient(
    instance="https://mycompany.service-now.com",
    username="admin",
    password="secret",
)
```

### Create a record

```python
record = client.create("incident", {
    "short_description": "Network outage",
    "urgency": "1",
    "impact": "1",
})
print(record["sys_id"])
```

### Read records

```python
# Fetch a single record by sys_id
incident = client.read("incident", sys_id="abc123def456")

# List records with a query
incidents = client.read(
    "incident",
    query="active=true^urgency=1",
    fields=["sys_id", "short_description", "state"],
    limit=10,
    offset=0,
)
```

### Update a record

```python
updated = client.update("incident", sys_id="abc123def456", data={
    "state": "6",   # Resolved
    "close_notes": "Issue resolved by restarting the service.",
})
```

### Delete a record

```python
client.delete("incident", sys_id="abc123def456")
```

## Running tests

```bash
pip install pytest responses
pytest tests/ -v
```
