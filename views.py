import subprocess
import json
from datetime import datetime
import greenstalk

import flask
import requests
from flask import Blueprint, render_template, request, make_response, jsonify

views_blueprint = Blueprint('main_view', __name__)

consumer_throughput_queue = greenstalk.Client(host='127.0.0.1', port=12000, use='consumer_throughput')

current_filename = ""
# this will be queried at run-time
burrow_ip = None
SCRIPT_DIR = "./scripts"
BURROW_DIR = "../fs-burrow-k8s"


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


def get_consumer_lag(consumer_id):
    global burrow_ip

    burrow_cluster_name = "mykafka"

    # see https://github.com/linkedin/Burrow/wiki/http-request-get-consumer-detail
    if burrow_ip:
        endpoint_url = f"http://{burrow_ip}/v3/kafka/{burrow_cluster_name}/consumer/{consumer_id}"
        response = requests.get(endpoint_url)
        print(response)
    return 0


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
            data["consumer_lag"] = consumer_lag
        else
            print("Burrow IP not set so ignoring consumer lag...")

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
