"""Small helper: Streamlit calls the Node.js API in server.js."""
import os
import requests

API_URL = os.getenv("API_URL", "http://127.0.0.1:5000").rstrip("/")


class APIError(Exception):
    """Readable API error to display inside Streamlit."""


def api(method, path, token=None, data=None):
    """Make an HTTP request. Examples: api('GET', '/api/assignments', token)."""
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        response = requests.request(
            method, API_URL + path, json=data, headers=headers, timeout=10
        )
    except requests.RequestException as error:
        raise APIError("Backend is not running. Start 'node server.js' first.") from error

    try:
        result = response.json()
    except ValueError:
        result = {}

    if not response.ok:
        message = result.get("error") or result.get("message") or f"HTTP {response.status_code}"
        raise APIError(message)
    return result
