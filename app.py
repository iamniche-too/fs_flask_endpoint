from flask import Flask


def create_app(settings_class):
    app = Flask(__name__)
    app.config.from_object(settings_class)

    from views import views_blueprint
    app.register_blueprint(views_blueprint)

    return app


if __name__ == '__main__':
    app = create_app('settings.local_config.Config')
    app.run(debug=app.config['DEBUG'], use_reloader=False, port=5000)
