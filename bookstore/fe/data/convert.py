#! /usr/bin/python3

import sqlite3
from pymongo import MongoClient
from bson.binary import Binary

# 将SQLite数据库转换为MongoDB
# sqlite_db_path: sqlite数据库的位置
# mongo_uri: mongodb的uri
# db_name: mongodb数据库的名字
# collection_name: mongodb集合的名字
def sqlite_to_mongodb(sqlite_db_path: str, mongo_uri: str, db_name: str, collection_name: str):
    sqlite_conn = sqlite3.connect(sqlite_db_path)
    sqlite_cursor = sqlite_conn.cursor()

    mongo_client = MongoClient(mongo_uri)
    db = mongo_client[db_name]
    collection = db[collection_name]

    try:
        sqlite_cursor.execute("SELECT * FROM book")
        columns = [column[0] for column in sqlite_cursor.description]
    
        documents = []
        for row in sqlite_cursor.fetchall():
            doc = {}
            for idx, col in enumerate(columns):
                value = row[idx]
                
                # BLOB的特殊处理
                if col == "picture" and value is not None:
                    doc[col] = Binary(value)
                else:
                    doc[col] = value
            documents.append(doc)

        collection.delete_many({})

        if documents:
            collection.insert_many(documents)
            print(f"Count: {len(documents)}")

    except Exception as e:
        print(f"Error occurred: {str(e)}")
    finally:
        sqlite_cursor.close()
        sqlite_conn.close()
        mongo_client.close()

if __name__ == "__main__":
    SQLITE_DB_PATH = input("Please enter small sqlite db path:") 
    MONGO_URI = "mongodb://localhost:27017"  
    DB_NAME = "book_fe_db"         
    COLLECTION_NAME = "books"        

    sqlite_to_mongodb(SQLITE_DB_PATH, MONGO_URI, DB_NAME, COLLECTION_NAME)
    
    SQLITE_DB_PATH = input("Please enter large sqlite db path:") 
    MONGO_URI = "mongodb://localhost:27017"  
    DB_NAME = "book_fe_db_large"         
    COLLECTION_NAME = "books"        

    sqlite_to_mongodb(SQLITE_DB_PATH, MONGO_URI, DB_NAME, COLLECTION_NAME)
