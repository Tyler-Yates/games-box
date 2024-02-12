import os

import waitress

from application import create_flask_app


def main():
    host = os.environ.get("WAITRESS_HOST", "127.0.0.1")
    port = os.environ.get("PORT", 10000)

    waitress.serve(create_flask_app(), listen=f"{host}:{port}")


if __name__ == "__main__":
    main()
