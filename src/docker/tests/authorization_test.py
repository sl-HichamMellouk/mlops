import sys
from common import append_log, request, wait_for_api


def build_output(username: str, endpoint: str, status_code: int, expected: int) -> str:
    status = "SUCCESS" if status_code == expected else "FAILURE"
    return f"""
============================
    Authorization test
============================

request done at \"{endpoint}\"
| username=\"{username}\"
| expected result = {expected}
| actual result = {status_code}

==>  {status}

"""


def run_test(username: str, password: str, endpoint: str, expected: int) -> bool:
    response = request(endpoint, {"username": username, "password": password, "sentence": "life is beautiful"})
    output = build_output(username, endpoint, response.status_code, expected)
    print(output)
    append_log(output)
    return response.status_code == expected


def main() -> int:
    if not wait_for_api():
        failure = "API unavailable after waiting for 30 seconds."
        print(failure)
        append_log(failure + "\n")
        return 1

    success = True
    success &= run_test("bob", "builder", "/v1/sentiment", 200)
    success &= run_test("bob", "builder", "/v2/sentiment", 403)
    success &= run_test("alice", "wonderland", "/v1/sentiment", 200)
    success &= run_test("alice", "wonderland", "/v2/sentiment", 200)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())