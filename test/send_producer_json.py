import requests
import datetime
import json

ENDPOINT="http://localhost:8080"

class Post:

    def post(self, producer_id):
        now = datetime.datetime.now()
        now_string = now.strftime("%m/%d/%Y, %H:%M:%S")
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        data = {'producer_id': producer_id, 'timestamp': now_string}
        post_result = requests.post(ENDPOINT + "/producer_count_endpoint", data=json.dumps(data), headers=headers)
        print(post_result)

if __name__ == '__main__':
    p = Post()
    p.post(1)
    p.post(2)
    p.post(3)
