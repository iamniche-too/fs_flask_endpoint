import subprocess
import json
import time
from datetime import datetime
import greenstalk

import flask
import requests
from flask import Blueprint, render_template, request, make_response, jsonify
from jsonpath_ng import jsonpath, parse

views_blueprint = Blueprint('main_view', __name__)

consumer_throughput_queue = greenstalk.Client(host='127.0.0.1', port=12000, use='consumer_throughput')

current_filename = ""
# this will be queried at run-time
burrow_ip = None
SCRIPT_DIR = "./scripts"
BURROW_DIR = "../fs-burrow-k8s"

TOTAL_LAG = "status.totallag"
MAX_LAG_TOPIC = "status.maxlag.topic"
MAX_LAG = "status.maxlag.current_lag"


def bash_command_with_output(additional_args, working_directory):
    args = ['/bin/bash', '-e'] + additional_args
    print(args)
    p = subprocess.Popen(args, stdout=subprocess.PIPE, cwd=working_directory)
    p.wait()
    out = p.communicate()[0].decode("UTF-8")
    return out


def set_burrow_ip():
    global burrow_ip

    filename = "./get-burrow-external-ip.sh"
    args = [filename]

    try:
        burrow_ip = bash_command_with_output(args, BURROW_DIR)
        print(f"burrow_ip={burrow_ip}")
    except ValueError:
        pass

    return burrow_ip


def get_producer_count():
    filename = "./get-producers-count.sh"
    args = [filename]

    producer_count = 0
    try:
        producer_count = int(bash_command_with_output(args, SCRIPT_DIR))
    except ValueError:
        pass

    print(f"reported_producer_count={producer_count}")
    return producer_count


producer_id = 0


@views_blueprint.route('/')
def web_root():
    page_vars = {'page_name': 'Home',
                 }
    return render_template("index.html", **page_vars)


# Endpoint for producers to query for an id
@views_blueprint.route('/producer_id')
def producer_id_endpoint():
    global producer_id
    producer_id += 1
    success = {'producer_id': producer_id}
    return make_response(jsonify(success), 200)


def get_total_lag(response):
    jsonpath1 = parse(TOTAL_LAG)
    matches = jsonpath1.find(response)

    total_lag = 0
    if matches:
        total_lag = int(matches[0].value)

    total_lag_dict = {"total_lag": total_lag}
    return total_lag_dict


def get_max_lag(response):
    jsonpath1 = parse(MAX_LAG_TOPIC)
    max_lag_topic = jsonpath1.find(response)
    jsonpath2 = parse(MAX_LAG)
    max_lag = jsonpath2.find(response)

    max_lag_dict = {}
    if max_lag_topic and max_lag:
        max_lag_dict = {max_lag_topic[0].value: max_lag[0].value}

    return max_lag_dict


def parse_burrow_response(response):
    max_lag_dict = get_max_lag(response.json())
    total_lag = get_total_lag(response.json())
    max_lag_dict.update(total_lag)
    return max_lag_dict


def get_consumer_lag(consumer_id):
    global burrow_ip

    consumer_lag = {}

    burrow_cluster_name = "mykafka"

    # see https://github.com/linkedin/Burrow/wiki/http-request-get-consumer-detail
    if burrow_ip:
        endpoint_url = f"http://{burrow_ip}:8000/v3/kafka/{burrow_cluster_name}/consumer/{consumer_id}/lag"
        print(endpoint_url)
        try:
            response = requests.get(endpoint_url)
            if response.status_code == 200:  # success
                consumer_lag = parse_burrow_response(response)
            else:
                print(response)
        except requests.ConnectionError as e:
            print(e)
            # try getting the IP again?
            burrow_ip = set_burrow_ip()

    return consumer_lag


@views_blueprint.route('/test', methods=['POST'])
def test_endpoint():
    now = datetime.now()

    if not request.is_json:
        failure = {'timestamp': now}
        return make_response(jsonify(failure), 400)

    data = request.get_json(force=True)

    print(data)

    success = {'timestamp': now}
    return make_response(jsonify(success), 200)


@views_blueprint.route('/test-with-timeout', methods=['POST'])
def test_with_timeout_endpoint():
    now = datetime.now()

    if not request.is_json:
        failure = {'timestamp': now}
        return make_response(jsonify(failure), 400)

    data = request.get_json(force=True)

    print(data)

    # now sleep for more than default timeout of 5 seconds
    time.sleep(10)

    success = {'timestamp': now}
    return make_response(jsonify(success), 200)


# 2020-05-20 14:12:32,438
def format_date(timestamp):
    timestamp = datetime.fromtimestamp(timestamp)
    return timestamp.strftime('%Y-%m-%d %H:%M:%S')


@views_blueprint.route('/consumer_reporting_endpoint', methods=['POST'])
def consumer_reporting_endpoint():
    global current_filename, burrow_ip

    if not burrow_ip:
        set_burrow_ip()

    now = datetime.now()

    if not request.is_json:
        failure = {'timestamp': now}
        return make_response(jsonify(failure), 400)

    data = request.get_json(force=True)

    print(format(data))

    # is this configuration data?
    if "machine_size" in data:
        # create a new file
        current_filename = "data/consumer_" + now.strftime("%d%m%Y_%H%M%S") + ".json"
        print(f"Setting current_filename={current_filename}")
        file = open(current_filename, 'a')
        file.write("[{ \"configuration\": [\n")
        json.dump(data, file)
        file.write("],\n")
        file.write("\"values\": [\n")
        file.close()
    else:
        print(f"Writing data to current_filename={current_filename}")

        producer_count = get_producer_count()
        data["producer_count"] = producer_count

        if burrow_ip:
            consumer_id = data["consumer_id"]
            consumer_lag = get_consumer_lag(consumer_id)

            # append to dict
            data.update(consumer_lag)
        else:
            print("Burrow IP not set so ignoring consumer lag...")

        # convert timestamp to date format
        data["timestamp"] = format_date(data["timestamp"])

        # write out to file
        with open(current_filename, 'a') as outfile:
            json.dump(data, outfile)
            outfile.write(",\n")
            outfile.close()

        # write to queue
        if consumer_throughput_queue:
            json_payload = json.dumps(data)
            print(f"Sending {json_payload} to consumer_throughput_queue")
            consumer_throughput_queue.put(json_payload)

    success = {'timestamp': now}

    return make_response(jsonify(success), 200)
