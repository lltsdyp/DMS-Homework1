import os
import sqlite3 as sqlite
import random
import base64
import simplejson as json
from pymongo import MongoClient

class Book:
    id: str
    title: str
    author: str
    publisher: str
    original_title: str
    translator: str
    pub_year: str
    pages: int
    price: int
    currency_unit: str
    binding: str
    isbn: str
    author_intro: str
    book_intro: str
    content: str
    tags: [str]
    pictures: [bytes]

    def __init__(self):
        self.tags = []
        self.pictures = []


class BookDB:
    def __init__(self, large: bool = False):
        # parent_path = os.path.dirname(os.path.dirname(__file__))
        # self.db_s = os.path.join(parent_path, "data/book.db")
        # self.db_s = "/home/user/bookstore/fe/data/book.db"
        # self.db_l = os.path.join(parent_path, "data/book_lx.db")
        # self.db_l=self.db_s
        # if large:
        #     self.book_db = self.db_l
        # else:
        #     self.book_db = self.db_s
        
        client=MongoClient("mongodb://localhost:27017")
        self.db_s=client["book_fe_db"]
        self.db_l=client["book_fe_db_large"]
        if large:
            self.book_db = self.db_l
        else:
            self.book_db = self.db_s

    def get_book_count(self):
        # conn = sqlite.connect(self.book_db)
        # cursor = conn.execute("SELECT count(id) FROM book")
        # row = cursor.fetchone()
        # return row[0]
        return self.book_db["books"].count_documents({})

    def get_book_info(self, start, size) -> [Book]:
        # books = []
        # conn = sqlite.connect(self.book_db)
        # cursor = conn.execute(
        #     "SELECT id, title, author, "
        #     "publisher, original_title, "
        #     "translator, pub_year, pages, "
        #     "price, currency_unit, binding, "
        #     "isbn, author_intro, book_intro, "
        #     "content, tags, picture FROM book ORDER BY id "
        #     "LIMIT ? OFFSET ?",
        #     (size, start),
        # )
        # for row in cursor:
        #     book = Book()
        #     book.id = row[0]
        #     book.title = row[1]
        #     book.author = row[2]
        #     book.publisher = row[3]
        #     book.original_title = row[4]
        #     book.translator = row[5]
        #     book.pub_year = row[6]
        #     book.pages = row[7]
        #     book.price = row[8]

        #     book.currency_unit = row[9]
        #     book.binding = row[10]
        #     book.isbn = row[11]
        #     book.author_intro = row[12]
        #     book.book_intro = row[13]
        #     book.content = row[14]
        #     tags = row[15]

        #     picture = row[16]

        #     for tag in tags.split("\n"):
        #         if tag.strip() != "":
        #             book.tags.append(tag)
        #     for i in range(0, random.randint(0, 9)):
        #         if picture is not None:
        #             encode_str = base64.b64encode(picture).decode("utf-8")
        #             book.pictures.append(encode_str)
        #     books.append(book)
        #     # print(tags.decode('utf-8'))

        #     # print(book.tags, len(book.picture))
        #     # print(book)
        #     # print(tags)
        books = []
        # 使用MongoDB查询替代SQLite
        cursor = self.book_db["books"].find(
            {},  # 查询所有字段
            projection={  # 显式指定需要的字段（根据Book类字段调整）
                "id": 1,
                "title": 1,
                "author": 1,
                "publisher": 1,
                "original_title": 1,
                "translator": 1,
                "pub_year": 1,
                "pages": 1,
                "price": 1,
                "currency_unit": 1,
                "binding": 1,
                "isbn": 1,
                "author_intro": 1,
                "book_intro": 1,
                "content": 1,
                "tags": 1,
                "picture": 1,
                "_id": 0  # 排除MongoDB自动生成的_id字段
            }
        ).sort("id", 1).skip(start).limit(size)
        
        for doc in cursor:
            book = Book()
            book.id = doc.get("id")
            book.title = doc.get("title")
            book.author = doc.get("author")
            book.publisher = doc.get("publisher")
            book.original_title = doc.get("original_title")
            book.translator = doc.get("translator")
            book.pub_year = doc.get("pub_year")
            book.pages = doc.get("pages")
            book.price = doc.get("price")
            book.currency_unit = doc.get("currency_unit")
            book.binding = doc.get("binding")
            book.isbn = doc.get("isbn")
            book.author_intro = doc.get("author_intro")
            book.book_intro = doc.get("book_intro")
            book.content = doc.get("content")
            
            tags = doc.get("tags", "")
            for tag in tags.split("\n"):
                if tag.strip():
                    book.tags.append(tag)
            
            picture = doc.get("picture")
            if picture:
                for _ in range(random.randint(0, 9)):
                    encode_str = base64.b64encode(picture).decode("utf-8")
                    book.pictures.append(encode_str)
            
            books.append(book)
        return books
