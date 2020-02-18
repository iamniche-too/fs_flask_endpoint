# fs_flask_endpoint

Getting Started:

In the project root directory:
```
$> export PYTHONPATH=`pwd`
$> cp settings/local_config_example.py settings/local_config_<your_name>.py
$> ln -s local_config_<your_name>.py local_config.py
# make changes to your settings
$> cd ..
$> pipenv shell
$> pipenv install --dev
```

Start the server:

```
$> python app.py local
```

Go to:

```
http://127.0.0.1:5000/
```