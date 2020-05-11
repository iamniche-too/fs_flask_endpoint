import json
import os
import unittest
from jsonpath_ng import jsonpath, parse

STATUS_TOTALLAG = "status.totallag"

TEST_PATH = os.path.dirname(os.path.abspath(__file__))
TEST_FILE_PATH = os.path.join(TEST_PATH, "example-consumer-lag.json")


def parse_response(response):
    jsonpath_expression = parse(STATUS_TOTALLAG)
    consumer_lag_match = jsonpath_expression.find(response)
    print(f"consumer_lag_match[0].value: {consumer_lag_match[0].value}")
    consumer_lag = int(consumer_lag_match[0].value)
    return consumer_lag


class TestParseBurrowResponse(unittest.TestCase):

    def setUp(self):
        super().setUp()

        with open(TEST_FILE_PATH) as file:
            self.json = json.load(file)

    def test_parse_response(self):
        response = parse_response(self.json)
        self.assertEqual(3585, response)
