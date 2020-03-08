from flask import Flask
import subprocess

SCRIPT_DIR="./scripts"
CLUSTER_NAME="gke-kafka-cluster"
CLUSTER_ZONE="europe-west2-a"

def bash_command_with_wait(additional_args, working_directory):
  args = ['/bin/bash', '-e'] + additional_args
  print(args)
  try:
    subprocess.check_call(args, stderr=subprocess.STDOUT, cwd=working_directory)
  except subprocess.CalledProcessError as e:
    # There was an error - command exited with non-zero code
    print(e.output)
    return False

  return True

# run a script to configure gcloud
def configure_gcloud(cluster_name, cluster_zone):
  print(f"configure_gcloud, cluster_name={cluster_name}, cluster_zone={cluster_zone}")
  filename = "./configure-gcloud.sh"
  args = [filename, cluster_name, cluster_zone]
  bash_command_with_wait(args, SCRIPT_DIR)

def create_app(settings_class):
    app = Flask(__name__)
    app.config.from_object(settings_class)

    from views import views_blueprint
    app.register_blueprint(views_blueprint)

    return app


if __name__ == '__main__':
    # configure gcloud (output is kubeconfig.yaml)
    configure_gcloud(CLUSTER_NAME, CLUSTER_ZONE)

    app = create_app('settings.local_config.Config')
    # app.run(host='0.0.0.0', debug=app.config['DEBUG'], use_reloader=False, port=8080)
    app.run(host='0.0.0.0', debug=app.config['DEBUG'], use_reloader=True, port=9000)
