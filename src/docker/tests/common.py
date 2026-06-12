import os
import time
from pathlib import Path

import requests


def get_api_address():
    return os.environ.get("API_ADDRESS", "api"), int(os.environ.get("API_PORT", "8000"))


def api_base_url():
    address, port = get_api_address()
    return f"http://{address}:{port}"


def wait_for_api(timeout: int = 30) -> bool:
    start = time.time()
    url = f"{api_base_url()}/status"
    while time.time() - start < timeout:
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(1)
    return False


def request(path: str, params: dict):
    url = f"{api_base_url()}{path}"
    return requests.get(url, params=params, timeout=8)


def parse_score(response):
    try:
        data = response.json()
    except ValueError:
        return None

    if isinstance(data, dict):
        for key in ["score", "sentiment", "prediction"]:
            if key in data:
                value = data[key]
                break
        else:
            if len(data) == 1:
                value = next(iter(data.values()))
            else:
                return None
    else:
        value = data

    if isinstance(value, (int, float)):
        return value
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def append_log(content: str) -> None:
    if os.environ.get("LOG") != "1":
        return

    log_path = os.environ.get("LOG_PATH", "api_test.log")
    log_file = Path(log_path)
    if log_file.parent:
        log_file.parent.mkdir(parents=True, exist_ok=True)
    with log_file.open("a", encoding="utf-8") as handle:
        handle.write(content)
