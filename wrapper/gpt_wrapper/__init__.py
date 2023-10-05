import os
import time

import requests

TIMEOUT_STATUS_CODE = 504
BAD_GATEWAY_STATUS_CODE = 502
RATE_LIMIT_STATUS_CODE = 429
TIMEOUT_SLEEP_TIME = 10
TIMEOUT_MAX_ATTEMPTS = 5

api_key = os.environ.get("PARROT_API_KEY")
api_base = os.environ.get(
    "PARROT_API_BASE", "http://localhost:5000"
)


def get_json(response):
    try:
        return response.json()
    except Exception:
        return None

def get_error_message(response, default="Something went wrong. Please try again later or contact us."):
    response_json = get_json(response)
    if response_json and "error" in response_json:
        return response_json["error"]
    else:
        return default

class BearerAuth(requests.auth.AuthBase):
    def __init__(self, token: str):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = f"Bearer {self.token}"
        return r


class APIException(Exception):
    pass


class API:
    def __init__(self):
        self._session = requests.Session()
        self._session.auth = BearerAuth(api_key)

    def get(self, path: str, params: dict = None) -> requests.Response:
        return self._retry_on_timeout(
            self._session.get, url=f"{api_base}{path}", params=params
        )

    def post(self, path: str, json: dict = None) -> requests.Response:
        return self._retry_on_timeout(
            self._session.post, url=f"{api_base}{path}", json=json
        )

    def _retry_on_timeout(self, func, *args, **kwargs):
        attempts = 0

        while True:
            with self._session:
                response = func(*args, **kwargs)
            attempts += 1

            if response.status_code in [TIMEOUT_STATUS_CODE, BAD_GATEWAY_STATUS_CODE, RATE_LIMIT_STATUS_CODE]:
                print(get_error_message(response, default="Server timeout."))
                sleep_time = attempts * TIMEOUT_SLEEP_TIME
                print(
                    f"Retrying in {sleep_time} seconds..."
                )
                time.sleep(sleep_time)
            else:
                return response

            if attempts > TIMEOUT_MAX_ATTEMPTS:
                raise APIException("Too many timeouts, aborting. Retry later.")
