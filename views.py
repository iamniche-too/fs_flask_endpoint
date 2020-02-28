import json
from datetime import datetime
import greenstalk

import flask
from flask import Blueprint, render_template, request, make_response, jsonify

views_blueprint = Blueprint('main_view', __name__)

consumer_throughput_queue = greenstalk.Client(host='127.0.0.1', port=12000, use='consumer_throughput')
producer_count_queue = greenstalk.Client(host='127.0.0.1', port=12000, use='producer_count')

producer_id_set = set([])

@views_blueprint.route('/')
def web_root():
    page_vars = {'page_name': 'Home',
                 }
    return render_template("index.html", **page_vars)


@views_blueprint.route('/producer_count_endpoint', methods=['POST'])
def producer_count_endpoint():
    now = datetime.now()

    if not request.is_json:
        failure = {'timestamp': now}
        return make_response(jsonify(failure), 400)

    data = request.get_json(force=True)

    # print(data)

    producer_id = data["producer_id"]
    producer_id_set.add(producer_id)

    # print(f"producer_id_set={producer_id_set}")

    producer_id_count = len(producer_id_set)
    # print(f"producer_id_count={producer_id_count}")

    if producer_count_queue:
        producer_count_queue.put(str(producer_id_count))
        print(f"Added {producer_id_count} to producer count queue")

    success = {'timestamp': now}

    return make_response(jsonify(success), 200)

@views_blueprint.route('/consumer_reporting_endpoint', methods=['POST'])
def consumer_reporting_endpoint():

    now = datetime.now()

    if not request.is_json:
        failure = {'timestamp': now}
        return make_response(jsonify(failure), 400)

    data = request.get_json(force=True)

    # print(format(data))

    filename = "data/consumer-" + now.strftime("%d%m%Y") + ".json"
    with open(filename, 'a') as outfile:
        json.dump(data, outfile)

    if consumer_throughput_queue:
        consumer_throughput_queue.put(json.dump(data))
        print(f"Added {data} to consumer throughput queue")

    success = {'timestamp': now}

    return make_response(jsonify(success), 200)
