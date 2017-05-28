import json
import requests
import requests.exceptions


class APIError(Exception):
    pass


class APIClient(object):
    """
    Allows to use Reborn HTTP API to upload new content.
    """

    DEFAULT_API_ENDPOINT = "http://localhost:8000/api/v1"

    def __init__(self, token, api_endpoint=None):
        self.token = token
        self.api_endpoint = api_endpoint or self.DEFAULT_API_ENDPOINT
        self._source_entries = []

    def _get_auth_headers(self):
        return {'Authorization': 'Token {0}'.format(self.token)}

    def _get_resource_url(self, resource):
        return self.api_endpoint.rstrip("/") + "/" + resource + "/"

    def get_sources(self):
        response = requests.get(
            self._get_resource_url("sources"),
            headers=self._get_auth_headers()
        )
        if response.status_code != 200:
            raise APIError(response.text)
        return response.json()

    def _post_data(self):
        headers = self._get_auth_headers()
        headers.update({'Content-type': 'application/json'})
        try:
            response = requests.post(
                self._get_resource_url("upload"),
                data=json.dumps({
                    "sources": self._source_entries
                }),
                headers=headers
            )
        except requests.exceptions.RequestException as err:
            raise APIError(str(err))

        return response.json()

    def add_source_entries(self, source, entries):
        self._source_entries.append({
            "source": source,
            "entries": entries
        })

    def _reset_data(self):
        self._source_entries = []

    def upload(self):
        self._post_data()
        self._reset_data()
