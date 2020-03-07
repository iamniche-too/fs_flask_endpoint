import subprocess
import json
from datetime import datetime
import greenstalk

import flask
from flask import Blueprint, render_template, request, make_response, jsonify

views_blueprint = Blueprint('main_view', __name__)

consumer_throughput_queue = greenstalk.Client(host='127.0.0.1', port=12000, use='consumer_throughput')

current_filename = ""
SCRIPT_DIR="./scripts"

def bash_command_with_output(additional_args, working_directory):
  args = ['/bin/bash', '-e'] + additional_args
  print(args)
  p = subprocess.Popen(args, stdout=subprocess.PIPE, cwd=working_directory)
  p.wait()
  out = p.communicate()[0].decode("UTF-8")
  return out

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

    # is this configuration data?
    if "machine_size" in data:
        # create a new file
        current_filename = "data/consumer_" + now.strftime("%d%m%Y_%H%M%S") + ".json"
        print(f"Setting current_filename={current_filename}")
        file = open(current_filename, 'a')
        file.write(" \"configuration\": [\n")
        json.dump(data, outfile)
        file.write("],\n")
        file.write("\"values\": [\n")
        file.close()
    else:
        print(f"Using current_filename={current_filename}")
        with open(current_filename, 'a') as outfile:
            producer_count = get_producer_count()
            data["producer_count"] = producer_count
            json.dump(data, outfile)
            outfile.write(",\n")
            outfile.close()

        if consumer_throughput_queue:
            throughput = str(data["throughput"])
            print(f"Adding throughput {throughput} to consumer_throughput_queue")
            consumer_throughput_queue.put(throughput)

    success = {'timestamp': now}

    return make_response(jsonify(success), 200)
