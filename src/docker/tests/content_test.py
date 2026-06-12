import sys
from common import append_log, parse_score, request, wait_for_api


def build_output(endpoint: str, sentence: str, actual_score, expected_sign: str) -> str:
    status = "FAILURE"
    if actual_score is not None:
        status = "SUCCESS" if (expected_sign == "positive" and actual_score > 0) or (expected_sign == "negative" and actual_score < 0) else "FAILURE"
    return f"""
============================
    Content test
============================

request done at \"{endpoint}\"
| sentence=\"{sentence}\"

Expected result = {expected_sign}
actual score = {actual_score}

==>  {status}

"""


def run_test(endpoint: str, sentence: str, expected_sign: str) -> bool:
    response = request(endpoint, {"username": "alice", "password": "wonderland", "sentence": sentence})
    score = parse_score(response)
    output = build_output(endpoint, sentence, score, expected_sign)
    print(output)
    append_log(output)
    if score is None:
        return False
    return (expected_sign == "positive" and score > 0) or (expected_sign == "negative" and score < 0)


def main() -> int:
    if not wait_for_api():
        failure = "API unavailable after waiting for 30 seconds."
        print(failure)
        append_log(failure + "\n")
        return 1

    success = True
    success &= run_test("/v1/sentiment", "life is beautiful", "positive")
    success &= run_test("/v1/sentiment", "that sucks", "negative")
    success &= run_test("/v2/sentiment", "life is beautiful", "positive")
    success &= run_test("/v2/sentiment", "that sucks", "negative")

    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())