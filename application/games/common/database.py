import os

from pymongo import MongoClient
from pymongo.database import Database


def get_database() -> Database:
    username = os.environ.get("MONGO_USER")
    password = os.environ.get("MONGO_PASSWORD")
    host = os.environ.get("MONGO_HOST")
    client = MongoClient(f"mongodb+srv://{username}:{password}@{host}/test?retryWrites=true&w=majority")

    return client.games
