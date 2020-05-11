import json
import os
import unittest
from jsonpath_ng import jsonpath, parse

TOTAL_LAG = "status.totallag"
MAX_LAG_TOPIC = "status.maxlag.topic"
MAX_LAG = "status.maxlag.current_lag"

TEST_PATH = os.path.dirname(os.path.abspath(__file__))
TEST_FILE_PATH = os.path.join(TEST_PATH, "example-consumer-lag3.json")


def get_total_lag(response):
    jsonpath1 = parse(TOTAL_LAG)
    matches = jsonpath1.find(response)
    consumer_lag = int(matches[0].value)
    return consumer_lag


def get_max_lag(response):
    jsonpath1 = parse(MAX_LAG_TOPIC)
    max_lag_topic = jsonpath1.find(response)
    jsonpath2 = parse(MAX_LAG)
    max_lag = jsonpath2.find(response)
    max_lag_dict = {max_lag_topic[0].value: max_lag[0].value}
    return max_lag_dict


class TestParseBurrowResponse(unittest.TestCase):

    def setUp(self):
        super().setUp()

        with open(TEST_FILE_PATH) as file:
            self.json = json.load(file)

    def test_get_total_lag(self):
        total_lag = get_total_lag(self.json)
        print(f"total_lag: {total_lag}")
        self.assertEqual(0, total_lag)

    def test_get_max_lag(self):
        max_lag = get_max_lag(self.json)
        print(f"max_lag: {max_lag}")
        self.assertEqual(0, max_lag["sensor1"])


