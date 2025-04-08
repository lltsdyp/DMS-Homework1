#! /usr/bin/python3

import re

from be.model import db_conn

class Filter:
    store_id: str
    stock_level: []
    publish_date: []
    pages: []
    price: []
    isbn: str
    
    def to_json_dict(self):
        return {
            "store_id":self.store_id,
            "stock_from":self.stock_level[0],
            "stock_to":self.stock_level[1],
            "publish_date_from":self.publish_date[0],
            "publish_date_to":self.publish_date[1],
            "pages_from":self.pages[0],
            "pages_to":self.pages[1],
            "price_from":self.price[0],
            "price_to":self.price[1],
            "isbn":self.isbn
        }
        
    def __init__(self):
        self.store_id = None
        self.stock_level = [None,None]
        self.publish_date = [None,None]
        self.pages = [None,None]
        self.price = [None,None]
        self.isbn = None

class Result:
    store_id: str
    book_id: str
    
    def __init__(self, store_id: str, book_id: str):
        self.store_id = store_id
        self.book_id = book_id
        
def check_condition(l:[]):
    for i in l:
        if i is not None:
            return True
    return False

class Search(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)
    
    def search(self, keyword: str, filter: Filter):
        regex = re.compile(f".*{re.escape(keyword)}.*", re.IGNORECASE)
        
        # 初始查询条件：匹配所有包含keyword的字段
        query = {
            "$or": [
                {"book_info.title": regex},
                {"book_info.author": regex},
                {"book_info.publisher": regex},
                {"book_info.original_title": regex},
                {"book_info.translator": regex},
                {"book_info.content": regex}
            ]
        }

        # 添加过滤条件
        if filter.store_id is not None:
            query["store_id"] = filter.store_id

        if check_condition(filter.stock_level):
            query["stock_level"]=dict()
            if filter.stock_level[0] is not None:
                query["stock_level"]["$gte"] = filter.stock_level[0]
            if filter.stock_level[1] is not None:
                query["stock_level"]["$lte"] = filter.stock_level[1]
                

        # TBD
        # if filter.publish_date is not None:
        #     query["book_info.publish_date"] = {
        #         "$gte": filter.publish_date[0],
        #         "$lte": filter.publish_date[1]
        #     }

        if check_condition(filter.pages):
            query["book_info.pages"] = dict()
            if filter.pages[0] is not None:
                query["book_info.pages"]["$gte"] = filter.pages[0]
            if filter.pages[1] is not None:
                query["book_info.pages"]["$lte"] = filter.pages[1]

        if check_condition(filter.price):
            query["book_info.price"] = dict()
            if filter.price[0] is not None:
                query["book_info.price"]["$gte"] = filter.price[0]
            if filter.price[1] is not None:
                query["book_info.price"]["$lte"] = filter.price[1]

        if filter.isbn is not None:
            query["book_info.isbn"] = filter.isbn

        # 执行查询并转换结果
        docs = self.store_instance.store_collection.find(query,{"store_id":1,"book_id":1,"_id":0})
        results=[]
        for doc in docs:
            results.append(Result(doc["store_id"],doc["book_id"]))
        return 200,"ok",results
