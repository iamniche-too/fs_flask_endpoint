import json
from datetime import datetime
import greenstalk

import flask
from flask import Blueprint, render_template, request, make_response, jsonify

views_blueprint = Blueprint('main_view', __name__)

consumer_throughput_queue = greenstalk.Client(host='127.0.0.1', port=12000, use='consumer_throughput')

current_filename = ""

@views_blueprint.route('/')
def web_root():
    page_vars = {'page_name': 'Home',
                 }
    return render_template("index.html", **page_vars)

@views_blueprint.route('/consumer_reporting_endpoint', methods=['POST'])
def consumer_reporting_endpoint():
    global current_filename

    now = datetime.now()

    if not request.is_json:
        failure = {'timestamp': now}
        return make_response(jsonify(failure), 400)

    data = request.get_json(force=True)

    print(format(data))
    if "message" in data:
        # create a new file
        current_filename = "data/consumer_" + now.strftime("%d%m%Y_%H%M%S") + ".json"
        print(f"Setting current_filename={current_filename}")
        file = open(current_filename, 'a')
        file.write("{ 'values': [")
        file.close()
    else:
        print(f"Using current_filename={current_filename}")
        with open(current_filename, 'a') as outfile:
            json.dump(data, outfile)
            outfile.write(",\r\n")
            outfile.close()

        if consumer_throughput_queue:
            consumer_throughput_queue.put(json.dumps(data))
            print(f"Added {data} to consumer throughput queue")

    success = {'timestamp': now}

    return make_response(jsonify(success), 200)
