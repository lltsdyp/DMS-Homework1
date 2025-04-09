import pytest
import uuid

from fe import conf
from fe.access.new_seller import register_new_seller
from fe.access import book
from fe.access.search import Search

from be.model import search

class TestSearchKeyword:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.seller_id = "test_add_books_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_add_books_store_id_{}".format(str(uuid.uuid1()))
        self.password = self.seller_id
        self.seller = register_new_seller(self.seller_id, self.password)

        code = self.seller.create_store(self.store_id)
        assert code == 200
        book_db = book.BookDB(conf.Use_Large_DB)
        self.books = book_db.get_book_info(0, 5)
        
        yield
        
    def test_ok(self):
        s=Search(conf.URL)
        code=s.search_books(self.books[0].title[:1],search.Filter())
        assert code==200
    
    def test_empty(self):
        s=Search(conf.URL)
        code=s.search_books("",search.Filter())
        assert code==200
