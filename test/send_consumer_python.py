import datetime
import json

import requests

ENDPOINT = "http://localhost:8080"

class Post:

    def post(self, consumer_id, throughput, **kwargs):
        is_init = kwargs["init"]
        now = datetime.datetime.now()
        now_string = now.strftime("%m/%d/%Y, %H:%M:%S")
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

        # {"consumer_id": "1", "timestamp": "18-02-2020 15:28", "throughput": "75"}
        if is_init:
            data = {"message": "consumer initialized", 'consumer_id': consumer_id, 'timestamp': now_string}
        else:
            data = {'consumer_id': consumer_id, 'timestamp': now_string, 'throughput': throughput}

        post_result = requests.post(ENDPOINT + "/consumer_reporting_endpoint", data=json.dumps(data), headers=headers)
        print(post_result)

if __name__ == '__main__':
    p = Post()
    p.post(1, 75, init=True)
    p.post(1, 75, init=False)
    p.post(1, 75, init=False)