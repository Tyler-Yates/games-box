from pymongo import ASCENDING, DESCENDING
from pymongo.collection import Collection
from pymongo.database import Database

from application.games.common.database import get_database

MAX_HI_SCORES = 3

# Fields used in the database
PLAYER_FIELD = "player"
SCORE_FIELD = "score"
BOARD_FIELD = "board"
ID_FIELD = "_id"


class ScrambledWordsDao:
    def __init__(self, database: Database = None):
        if database is None:
            database = get_database()

        self.database = database

        self.scrambled_words_hiscore: Collection = self.database.scrambled_words_hiscore

        self.scrambled_words_hiscore.create_index([(BOARD_FIELD, ASCENDING)])

    def record_score(self, board_id: str, score: int, player_name: str):
        # We don't want duplicate entries, so do an upsert instead of an insert
        data = {BOARD_FIELD: board_id, SCORE_FIELD: score, PLAYER_FIELD: player_name}
        self.scrambled_words_hiscore.update_one(data, {"$set": data}, upsert=True)

        self._clean_collection(board_id)

    def get_hiscore(self, board_id: str):
        top_scores = self.scrambled_words_hiscore.find({BOARD_FIELD: board_id}).sort(SCORE_FIELD, direction=DESCENDING).limit(MAX_HI_SCORES)
        return top_scores

    def _clean_collection(self, board_id: str):
        while self.scrambled_words_hiscore.find({BOARD_FIELD: board_id}).count() > MAX_HI_SCORES:
            lowest_score_doc = (
                self.scrambled_words_hiscore.find({BOARD_FIELD: board_id})
                .sort(SCORE_FIELD, direction=ASCENDING)
                .limit(1)
            )
            self.scrambled_words_hiscore.delete_one({BOARD_FIELD: board_id, SCORE_FIELD: lowest_score_doc[SCORE_FIELD]})
