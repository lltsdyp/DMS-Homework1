# import sqlite3 as sqlite
import pymongo
import pymongo.errors
from be.model import error
from be.model import db_conn


class Seller(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def add_book(
        self,
        user_id: str,
        store_id: str,
        book_id: str,
        book_json_str: str,
        stock_level: int,
    ):
        # try:
        #     if not self.user_id_exist(user_id):
        #         return error.error_non_exist_user_id(user_id)
        #     if not self.store_id_exist(store_id):
        #         return error.error_non_exist_store_id(store_id)
        #     if self.book_id_exist(store_id, book_id):
        #         return error.error_exist_book_id(book_id)

        #     self.conn.execute(
        #         "INSERT into store(store_id, book_id, book_info, stock_level)"
        #         "VALUES (?, ?, ?, ?)",
        #         (store_id, book_id, book_json_str, stock_level),
        #     )
        #     self.conn.commit()
        # except sqlite.Error as e:
        #     return 528, "{}".format(str(e))
        # except BaseException as e:
        #     return 530, "{}".format(str(e))
        # return 200, "ok"
        if not self.user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id)
        if not self.store_id_exist(store_id):
            return error.error_non_exist_store_id(store_id)
        if self.book_id_exist(store_id, book_id):
            return error.error_exist_book_id(book_id)
        
        try:
            self.store_instance.store_collection.insert_one({
                "store_id": store_id,
                "book_id": book_id,
                "book_info": book_json_str,
                "stock_level": stock_level,
            })
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200,"ok"

    def add_stock_level(
        self, user_id: str, store_id: str, book_id: str, add_stock_level: int
    ):
        # try:
        #     if not self.user_id_exist(user_id):
        #         return error.error_non_exist_user_id(user_id)
        #     if not self.store_id_exist(store_id):
        #         return error.error_non_exist_store_id(store_id)
        #     if not self.book_id_exist(store_id, book_id):
        #         return error.error_non_exist_book_id(book_id)

        #     self.conn.execute(
        #         "UPDATE store SET stock_level = stock_level + ? "
        #         "WHERE store_id = ? AND book_id = ?",
        #         (add_stock_level, store_id, book_id),
        #     )
        #     self.conn.commit()
        # except sqlite.Error as e:
        #     return 528, "{}".format(str(e))
        # except BaseException as e:
        #     return 530, "{}".format(str(e))
        # return 200, "ok"
        if not self.user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id)
        if not self.store_id_exist(store_id):
            return error.error_non_exist_store_id(store_id)
        if not self.book_id_exist(store_id, book_id):
            return error.error_non_exist_book_id(book_id)
        
        try:
            self.store_instance.store_collection.update_one({
                "store_id": store_id,
                "book_id": book_id,
            }, {
                "$inc": {"stock_level": add_stock_level}
            })
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
           return 530, "{}".format(str(e))
        return 200,"ok"
        

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        # try:
        #     if not self.user_id_exist(user_id):
        #         return error.error_non_exist_user_id(user_id)
        #     if self.store_id_exist(store_id):
        #         return error.error_exist_store_id(store_id)
        #     self.conn.execute(
        #         "INSERT into user_store(store_id, user_id)" "VALUES (?, ?)",
        #         (store_id, user_id),
        #     )
        #     self.conn.commit()
        # except sqlite.Error as e:
        #     return 528, "{}".format(str(e))
        # except BaseException as e:
        #     return 530, "{}".format(str(e))
        # return 200, "ok"
        if not self.user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id)
        if self.store_id_exist(store_id):
            return error.error_exist_store_id(store_id)
        
        try:
            self.store_instance.user_store_collection.insert_one({
                "store_id": store_id,
                "user_id": user_id, 
            })
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200,"ok"

    #更改订单状态
    # 1表示已支付，2表示已发货
    def send_books(self, user_id: str, order_id: str) -> (int, str):
        # 检查用户ID是否存在
        if not self.user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id)
        
        #在new_order_collection中找到同时满足user_id和order_id同时满足的文档
        result=self.store_instance.new_order_collection.find_one({
            "order_id": order_id,
            "user_id": user_id,
            "status": 1
        })
        if result is None:
            return error.error_invalid_order_id(order_id)
        #将status改为2
        try:
            self.store_instance.new_order_collection.update_one({
                "order_id": order_id,
            }, {
                "$set": {"status": 2}
            })
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200,"ok"
        
        