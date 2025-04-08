import logging
import os
# import sqlite3 as sqlite
import threading
import pymongo
import pymongo.database


class Store:
    database: str

    def __init__(self, db_path):
        # self.database = os.path.join(db_path, "be.db")
        self.client=pymongo.MongoClient("mongodb://localhost:27017")
        self.collections=self.client["bookstore"]
        self.init_tables()

    def init_tables(self):
        # try:
        #     conn = self.get_db_conn()
        #     conn.execute(
        #         "CREATE TABLE IF NOT EXISTS user ("
        #         "user_id TEXT PRIMARY KEY, password TEXT NOT NULL, "
        #         "balance INTEGER NOT NULL, token TEXT, terminal TEXT);"
        #     )

        #     conn.execute(
        #         "CREATE TABLE IF NOT EXISTS user_store("
        #         "user_id TEXT, store_id, PRIMARY KEY(user_id, store_id));"
        #     )

        #     conn.execute(
        #         "CREATE TABLE IF NOT EXISTS store( "
        #         "store_id TEXT, book_id TEXT, book_info TEXT, stock_level INTEGER,"
        #         " PRIMARY KEY(store_id, book_id))"
        #     )

        #     conn.execute(
        #         "CREATE TABLE IF NOT EXISTS new_order( "
        #         "order_id TEXT PRIMARY KEY, user_id TEXT, store_id TEXT)"
        #     )

        #     conn.execute(
        #         "CREATE TABLE IF NOT EXISTS new_order_detail( "
        #         "order_id TEXT, book_id TEXT, count INTEGER, price INTEGER,  "
        #         "PRIMARY KEY(order_id, book_id))"
        #     )

        #     conn.commit()
        # except sqlite.Error as e:
        #     logging.error(e)
        #     conn.rollback()
        self.user_collection=self.collections["user"]
        self.user_store_collection=self.collections["user_store"]
        self.store_collection=self.collections["store"]
        self.new_order_collection=self.collections["new_order"]
        self.new_order_detail_collection=self.collections["new_order_detail"]

        # 模拟sqlite中的PRIMARY KEY约束
        self.user_collection.create_index([("user_id",1)],unique=True)
        self.user_store_collection.create_index([("user_id",1),("store_id",1)],unique=True)
        self.store_collection.create_index([("store_id",1),("book_id",1)],unique=True)
        self.new_order_collection.create_index([("order_id",1)],unique=True)
        #self.new_order_detail_collection.create_index([("order_id",1),("book_id",1)],unique=True) 
        #这里的order_id应该不是唯一的，因为一个订单可以有多个商品！！！


    # def get_db_conn(self) -> sqlite.Connection:
    #     return sqlite.connect(self.database)


database_instance: Store = None
# global variable for database sync
init_completed_event = threading.Event()


def init_database(db_path):
    global database_instance
    database_instance = Store(db_path)


def get_db_conn():
    global database_instance
    return database_instance.client

def get_instance() -> Store:
    global database_instance
    return database_instance
