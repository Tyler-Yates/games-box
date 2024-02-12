# game-box
A collection of simple web games.

## Technologies
Socketio is used to send messages from client to server.

## Running the application
You can run the application by executing the following command:
`python3 -m application`

The webapp should be accessible at [http://127.0.0.1:10000]()

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
