# import asyncpg

from tgbot.config import load_config

# from asyncpg.pool import Pool
from pymongo import MongoClient, ASCENDING, DESCENDING

db_conf = load_config().db


class Database:

    def __init__(self):
        self.pool: MongoClient = None

    def create(self):
        self.pool = MongoClient(db_conf.mongo)

    def addDoc(self, database: str, collection: str, document: dict or list[dict]):
        if type(document) == dict:
            res = self.pool[database][collection].insert_one(document).inserted_id
        elif type(document) == list:
            res = self.pool[database][collection].insert_many(document).inserted_ids
        return res

    def getDocs(self, database: str, collection: str, search: dict, order_by: dict = {'_id': 1}):

        # order_by = {'field1': 1, 'field2': 0}
        # sort_by = [('field1', ASCENDING), ('field2', DESCENDING)]

        sort_by = [(field, ASCENDING) if val == 1 else (field, DESCENDING) for field, val in order_by.items()]

        return list(self.pool[database][collection].find(search).sort(sort_by))

    def getDoc(self, database: str, collection: str, search: dict):
        return self.pool[database][collection].find_one(search)

    def updateDoc(self, database: str, collection: str, search: dict, update_doc):
        return self.pool[database][collection].update_one(search, {'$set': update_doc}, upsert=False)

    def getCollectionNames(self, database: str):
        return self.pool[database].list_collection_names()

    # async def __execute(self, command, *args,
    #                   fetch: bool = False,
    #                   fetchval: bool = False,
    #                   fetchrow: bool = False,
    #                   execute: bool = False
    #                   ):
    #     async with self.pool.acquire() as connection:
    #         connection: asyncpg.Connection
    #         async with connection.transaction():
    #             if fetch:
    #                 result = await connection.fetch(command, *args)
    #             elif fetchval:
    #                 result = await connection.fetchval(command, *args)
    #             elif fetchrow:
    #                 result = await connection.fetchrow(command, *args)
    #             elif execute:
    #                 result = await connection.execute(command, *args)
    #         return result
    #
    # async def create_table_users(self):
    #     sql = """
    #     CREATE TABLE IF NOT EXISTS Users (
    #     id SERIAL PRIMARY KEY,
    #     username VARCHAR(255) NULL,
    #     telegram_id BIGINT NOT NULL
    #     );
    #     """
    #     await self.__execute(sql, execute=True)
    #
    # async def create_table_meetings(self):
    #     sql = """
    #             CREATE TABLE IF NOT EXISTS Meetings (
    #             id SERIAL PRIMARY KEY,
    #             name VARCHAR(255) NULL,
    #             date DATE NOT NULL,
    #             time TIME NOT NULL
    #             );
    #             """
    #     await self.__execute(sql, execute=True)