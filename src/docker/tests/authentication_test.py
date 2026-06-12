import sys
from common import append_log, request, wait_for_api


def build_output(username: str, password: str, status_code: int, expected: int) -> str:
    status = "SUCCESS" if status_code == expected else "FAILURE"
    return f"""
============================
    Authentication test
============================

request done at "/permissions"
| username=\"{username}\"
| password=\"{password}\"

Expected result = {expected};
actual result = {status_code}

==>  {status}

"""


def run_test(username: str, password: str, expected: int) -> bool:
    response = request("/permissions", {"username": username, "password": password})
    output = build_output(username, password, response.status_code, expected)
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
    success &= run_test("alice", "wonderland", 200)
    success &= run_test("bob", "builder", 200)
    success &= run_test("clementine", "mandarine", 403)

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())