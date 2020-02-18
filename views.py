import json
from datetime import datetime

import flask
from flask import Blueprint, render_template, request, make_response, jsonify

views_blueprint = Blueprint('main_view', __name__)


@views_blueprint.route('/')
def web_root():
    page_vars = {'page_name': 'Home',
                 }
    return render_template("index.html", **page_vars)


@views_blueprint.route('/consumer_reporting_endpoint', methods=['POST'])
def consumer_reporting_endpoint():

    now = datetime.now()

    if not request.is_json:
        failure = {'timestamp': now}
        return make_response(jsonify(failure), 400)

    data = request.get_json(force=True)

    # print(format(data))

    filename = "data/consumer-" + now.strftime("%d%m%Y-%H%M%S") + ".json"
    with open(filename, 'w') as outfile:
        json.dump(data, outfile)

    success = {'timestamp': now}

    return make_response(jsonify(success), 200)
