from pymongo import MongoClient
import os

class Database():
    def __init__(self) -> None:
        self.client = MongoClient(str(os.environ['MONGO_URL']))
        self.db = self.client.test.cookie

    def setCookie(self, author_id: str, discordName: str, ssid: str):
        data = {
            'discord_name': discordName,
            'author_id': author_id,
            'ssid': ssid
        }
        return self.db.update_one({'author_id': author_id}, {'$set': data}, upsert=True)

    def getCookie(self, author_id: str):
        return self.db.find({'author_id': author_id})[0]['ssid']