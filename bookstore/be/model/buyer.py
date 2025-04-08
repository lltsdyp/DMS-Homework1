# import sqlite3 as sqlite
import pymongo
import uuid
import json
import logging

import pymongo.errors
from datetime import datetime, timedelta
from be.model import db_conn
from be.model import error


class Buyer(db_conn.DBConn):
    def __init__(self):
        db_conn.DBConn.__init__(self)

    def new_order(
        self, user_id: str, store_id: str, id_and_count: [(str, int)]
    ) -> (int, str, str):
        # order_id = ""
        # try:
        #     if not self.user_id_exist(user_id):
        #         return error.error_non_exist_user_id(user_id) + (order_id,)
        #     if not self.store_id_exist(store_id):
        #         return error.error_non_exist_store_id(store_id) + (order_id,)
        #     uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

        #     for book_id, count in id_and_count:
        #         cursor = self.conn.execute(
        #             "SELECT book_id, stock_level, book_info FROM store "
        #             "WHERE store_id = ? AND book_id = ?;",
        #             (store_id, book_id),
        #         )
        #         row = cursor.fetchone()
        #         if row is None:
        #             return error.error_non_exist_book_id(book_id) + (order_id,)

        #         stock_level = row[1]
        #         book_info = row[2]
        #         book_info_json = json.loads(book_info)
        #         price = book_info_json.get("price")

        #         if stock_level < count:
        #             return error.error_stock_level_low(book_id) + (order_id,)

        #         cursor = self.conn.execute(
        #             "UPDATE store set stock_level = stock_level - ? "
        #             "WHERE store_id = ? and book_id = ? and stock_level >= ?; ",
        #             (count, store_id, book_id, count),
        #         )
        #         if cursor.rowcount == 0:
        #             return error.error_stock_level_low(book_id) + (order_id,)

        #         self.conn.execute(
        #             "INSERT INTO new_order_detail(order_id, book_id, count, price) "
        #             "VALUES(?, ?, ?, ?);",
        #             (uid, book_id, count, price),
        #         )

        #     self.conn.execute(
        #         "INSERT INTO new_order(order_id, store_id, user_id) "
        #         "VALUES(?, ?, ?);",
        #         (uid, store_id, user_id),
        #     )
        #     self.conn.commit()
        #     order_id = uid
        # except sqlite.Error as e:
        #     logging.info("528, {}".format(str(e)))
        #     return 528, "{}".format(str(e)), ""
        # except BaseException as e:
        #     logging.info("530, {}".format(str(e)))
        #     return 530, "{}".format(str(e)), ""

        # return 200, "ok", order_id
        order_id=""
        if not self.user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id) + (order_id,)
        if not self.store_id_exist(store_id):
            return error.error_non_exist_store_id(store_id) + (order_id,)
        uid="{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))
        
        try:
            for book_id, count in id_and_count:
                book_query = self.store_instance.store_collection.find_one  ({"store_id":store_id,"book_id":book_id})
                if not book_query:
                    return error.error_non_exist_book_id(book_id) + (order_id,)

                stock_level=book_query["stock_level"]
                book_info=book_query["book_info"]
                book_info_json=json.loads(book_info)
                price=book_info_json.get("price")

                if stock_level<count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                # 感觉不需要再再查找条件中加入stock_level大小比较，因为上面已经比较过了
                update_result = self.store_instance.store_collection.update_one(
                    {"store_id":store_id,"book_id":book_id},
                    {"$inc":{"stock_level":-count}}
                )
                if update_result.modified_count != 1:
                    return error.error_stock_level_low(book_id) +(order_id,)

                self.store_instance.new_order_detail_collection.insert_one(
                    {
                        "order_id":uid,
                        "book_id":book_id,
                        "count":count,
                        "price":price
                    }
                )
            #维护时间，方便后面判断超时
            now_time = datetime.datetime.now()
            #在new_order_collection增加三个字段，create_time和status
            #status=0表示未支付，1表示已支付
            self.store_instance.new_order_collection.insert_one(
                {
                    "order_id":uid,
                    "store_id":store_id,
                    "user_id":user_id,
                    'create_time':now_time,
                    "status":0
                }
            )
            order_id=uid
        except pymongo.errors.PyMongoError as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            return 530, "{}".format(str(e)), ""
        
        return 200, "ok", order_id

    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        # conn = self.conn
        # try:
        #     cursor = conn.execute(
        #         "SELECT order_id, user_id, store_id FROM new_order WHERE order_id = ?",
        #         (order_id,),
        #     )
        #     row = cursor.fetchone()
        #     if row is None:
        #         return error.error_invalid_order_id(order_id)

        #     order_id = row[0]
        #     buyer_id = row[1]
        #     store_id = row[2]

        #     if buyer_id != user_id:
        #         return error.error_authorization_fail()

        #     cursor = conn.execute(
        #         "SELECT balance, password FROM user WHERE user_id = ?;", (buyer_id,)
        #     )
        #     row = cursor.fetchone()
        #     if row is None:
        #         return error.error_non_exist_user_id(buyer_id)
        #     balance = row[0]
        #     if password != row[1]:
        #         return error.error_authorization_fail()

        #     cursor = conn.execute(
        #         "SELECT store_id, user_id FROM user_store WHERE store_id = ?;",
        #         (store_id,),
        #     )
        #     row = cursor.fetchone()
        #     if row is None:
        #         return error.error_non_exist_store_id(store_id)

        #     seller_id = row[1]

        #     if not self.user_id_exist(seller_id):
        #         return error.error_non_exist_user_id(seller_id)

        #     cursor = conn.execute(
        #         "SELECT book_id, count, price FROM new_order_detail WHERE order_id = ?;",
        #         (order_id,),
        #     )
        #     total_price = 0
        #     for row in cursor:
        #         count = row[1]
        #         price = row[2]
        #         total_price = total_price + price * count

        #     if balance < total_price:
        #         return error.error_not_sufficient_funds(order_id)

        #     cursor = conn.execute(
        #         "UPDATE user set balance = balance - ?"
        #         "WHERE user_id = ? AND balance >= ?",
        #         (total_price, buyer_id, total_price),
        #     )
        #     if cursor.rowcount == 0:
        #         return error.error_not_sufficient_funds(order_id)

        #     cursor = conn.execute(
        #         "UPDATE user set balance = balance + ?" "WHERE user_id = ?",
        #         (total_price, seller_id),
        #     )

        #     if cursor.rowcount == 0:
        #         return error.error_non_exist_user_id(seller_id)

        #     cursor = conn.execute(
        #         "DELETE FROM new_order WHERE order_id = ?", (order_id,)
        #     )
        #     if cursor.rowcount == 0:
        #         return error.error_invalid_order_id(order_id)

        #     cursor = conn.execute(
        #         "DELETE FROM new_order_detail where order_id = ?", (order_id,)
        #     )
        #     if cursor.rowcount == 0:
        #         return error.error_invalid_order_id(order_id)

        #     conn.commit()

        # except sqlite.Error as e:
        #     return 528, "{}".format(str(e))

        # except BaseException as e:
        #     return 530, "{}".format(str(e))

        # return 200, "ok"
        try:
            order = self.store_instance.new_order_collection.find_one({"order_id": order_id})
            if order is None:
                return error.error_invalid_order_id(order_id) 

            buyer_id = order["user_id"]
            store_id = order["store_id"]

            if buyer_id != user_id:
                return error.error_authorization_fail() 

            user = self.store_instance.user_collection.find_one({"user_id": buyer_id})
            if not user:
                return error.error_non_exist_user_id(buyer_id) 
            balance = user["balance"]
            if password != user.get("password"):
                return error.error_authorization_fail() 

            store_info = self.store_instance.user_store_collection.find_one(
                {"store_id": store_id}
            )
            if not store_info:
                return error.error_non_exist_store_id(store_id) 
            seller_id = store_info["user_id"]

            details = (
                self.store_instance.new_order_detail_collection.find(
                    {"order_id": order_id}
                )
            )
            total_price = 0
            for detail in details:
                count = detail["count"]
                price = detail["price"]
                total_price += count * price

            buyer_filter = {
                "user_id": buyer_id,
                "balance": {"$gte": total_price},
            }
            buyer_update = {"$inc": {"balance": -total_price}}
            buyer_result = self.store_instance.user_collection.update_one(
                buyer_filter, buyer_update
            )
            if buyer_result.modified_count != 1:
                return error.error_not_sufficient_funds(order_id) 

            seller_filter = {"user_id": seller_id}
            seller_update = {"$inc": {"balance": total_price}}
            seller_result = self.store_instance.user_collection.update_one(
                seller_filter, seller_update
            )
            if seller_result.modified_count != 1:
                return error.error_non_exist_user_id(seller_id) 

            #将删除订单改为修改订单状态
            """ delete_order_result = self.store_instance.new_order_collection.delete_one(
                {"order_id": order_id}
            )
            if delete_order_result.deleted_count != 1:
                return error.error_invalid_order_id(order_id) """ 
            update_status_result = self.store_instance.new_order_collection.update_one(
                {"order_id": order_id, "status": 0},
                {"$set": {"status": 1}}
            )
            if update_status_result.modified_count != 1:
                return error.error_invalid_order_id(order_id)
            
            # order_detail不可以删除的，在后续删除订单时，需要知道订单详情，所以这里不删除
            """ delete_detail_result = (
                self.store_instance.new_order_detail_collection.delete_many(
                    {"order_id": order_id}
                )
            )
            if delete_detail_result.deleted_count < 1:
                return error.error_invalid_order_id(order_id)  """

        except pymongo.errors.PyMongoError as e:
            return 528, f"MongoDB error: {str(e)}", ""
        # except BaseException as e:
        #     return 530, f"Unexpected error: {str(e)}", ""

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        # try:
        #     cursor = self.conn.execute(
        #         "SELECT password  from user where user_id=?", (user_id,)
        #     )
        #     row = cursor.fetchone()
        #     if row is None:
        #         return error.error_authorization_fail()

        #     if row[0] != password:
        #         return error.error_authorization_fail()

        #     cursor = self.conn.execute(
        #         "UPDATE user SET balance = balance + ? WHERE user_id = ?",
        #         (add_value, user_id),
        #     )
        #     if cursor.rowcount == 0:
        #         return error.error_non_exist_user_id(user_id)

        #     self.conn.commit()
        # except sqlite.Error as e:
        #     return 528, "{}".format(str(e))
        # except BaseException as e:
        #     return 530, "{}".format(str(e))

        # return 200, "ok"
        try:
            user = self.store_instance.user_collection.find_one({"user_id": user_id})
            if not user:
                return error.error_non_exist_user_id(user_id) + ("",)

            if password != user.get("password"):
                return error.error_authorization_fail() + ("",)

            update_filter = {"user_id": user_id}
            update_operation = {"$inc": {"balance": add_value}}
            result = self.store_instance.user_collection.update_one(update_filter, update_operation)

            if result.modified_count != 1:
                return error.error_non_exist_user_id(user_id) + ("",)

        except pymongo.errors.PyMongoError as e:
            return 528, f"MongoDB error: {str(e)}", ""
        except BaseException as e:
            return 530, f"Unexpected error: {str(e)}", ""

        return 200, "ok", ""
    
    #更改订单状态，status=2表示已发货
    # 3表示已收货，已完成的订单
    def receive_books(self, user_id: str, order_id: str) -> (int, str):
        # 检查用户ID是否存在
        if not self.user_id_exist(user_id):
            return error.error_non_exist_user_id(user_id)
        
        #在new_order_collection中找到同时满足user_id和order_id同时满足的文档
        result=self.store_instance.new_order_collection.find_one({
            "order_id": order_id,
            "user_id": user_id,
            "status": 2
        })
        if result is None:
            return error.error_invalid_order_id(order_id)
        #将status改为3
        try:
            self.store_instance.new_order_collection.update_one({
                "order_id": order_id,
            }, {
                "$set": {"status": 3}
            })
        except pymongo.errors.PyMongoError as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200,"ok"
    
    def cancel_order(self, user_id: str, order_id: str) -> (int, str):
        try:
            #未付款
            store_id = ""
            result = self.store_instance.new_order_collection.find_one({
                "order_id": order_id,
                "user_id": user_id,
                "status": 0
            })
            if result:
                #不能删除订单，选择修改状态即可，保留订单历史
                #self.store_instance.new_order_collection.delete_one({"order_id": order_id, "user_id": user_id, "status": 0})
                store_id = result["store_id"]
                
            #已付款
            else:
                result = self.store_instance.new_order_collection.find_one({
                    "$or": [
                        {"order_id": order_id, "user_id": user_id, "status": 1},
                        {"order_id": order_id, "user_id": user_id, "status": 2},
                        {"order_id": order_id, "user_id": user_id, "status": 3},
                    ]
                })
                if result:
                    #恢复余额
                        #找到卖家的user_id
                    store_id = result["store_id"]
                    result1 = self.store_instance.user_store_collection.find_one({"store_id": store_id})
                    store_user_id = ""
                    if result1:
                        store_user_id = result1["user_id"]
                    else:
                        return error.error_non_exist_store_id(store_id)
                    details = self.store_instance.new_order_detail_collection.find({"order_id": order_id})
                    for detail in details:
                        book_id = detail["book_id"]
                        count = detail["count"]
                        price = detail["price"]
                        self.store_instance.user_collection.update_one({"user_id": user_id}, {"$inc": {"balance": price * count}})
                        self.store_instance.user_collection.update_one({"user_id": store_user_id}, {"$inc": {"balance": -price * count}})
                    #不能删除订单，选择修改状态即可，保留订单历史
                    #self.store_instance.new_order_collection.delete_one({"order_id": order_id, "user_id": user_id})

                else:
                    return error.error_invalid_order_id(order_id)
            #恢复库存
            details = self.store_instance.new_order_detail_collection.find({"order_id": order_id})
            for book in details:
                book_id = book["book_id"]
                count = book["count"]
                self.store_instance.store_collection.update_one({"store_id": store_id, "book_id": book_id}, {"$inc": {"count": count}})
            #修改订单状态，而不是删除订单，status=4表示取消的订单
            self.store_instance.new_order_collection.update_one({"order_id": order_id, "user_id": user_id}, {"$set": {"status": 4}})
        except BaseException as e:
            return 528, "{}".format(str(e))
        return 200, "ok"        