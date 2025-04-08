import pytest
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.book import Book
import uuid

import random

class Testhistoryorder:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.buyer_id = "test_check_hist_order_buyer_id_{}".format(str(uuid.uuid1()))
        self.password = self.buyer_id

        b = register_new_buyer(self.buyer_id, self.password)
        self.buyer = b
        yield

    def test_non_exist_user_id(self):
        code = self.buyer.check_hist_order(self.buyer_id + 'x')
        assert code != 200

