# game-box
A collection of simple web games.

## Technologies
This webapp is a Flask application.
Socketio is used to send messages from client to server as well as run the webserver.

## Setup
To preserve consistency with running in the cloud, this application uses HTTPS even when running locally.
You will need to run the following commands from the root of the repo to get ready for HTTPS:
```
mkdir ssl
cd ssl
openssl req -nodes -new -x509 -keyout server.key -out server.crt \
    -subj "/C=GB/ST=London/L=London/O=Local/OU=Local/CN=127.0.0.1"
```
The `ssl` folder is ignored by `git` so you should not need to worry about committing the
generated key and certificate.

After generating the key and certificate, you are ready to run the application.

## Running the application
Your run configuration should look like the following:
```
python3 -m application
```
Make sure to run the application with the working directory set at the root of the repo.

The webapp should be accessible at [https://127.0.0.1:5000]()

You will most likely need to tell your browser to accept the self-signed certificate.

## Dependencies
This project's dependencies are laid out in the `requirements.in` file in the root of the repo.
These dependencies are not pinned to a particular version unless absolutely necessary.

To support repeatable builds, the `requirements.in` file is "compiled" to the frozen `requirements.txt` file.
This file pins every dependency to a particular version.

To update the `requirements.txt` file, use `pip-tools`:
```
pip install pip-tools
pip-compile --output-file=requirements.txt requirements.in
```

After updating the `requirements.txt` file, you should update your venv:
```
pip-sync requirements.txt
```
