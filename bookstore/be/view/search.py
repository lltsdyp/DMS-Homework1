#! /usr/bin/python3

from flask import Blueprint
from flask import request
from flask import jsonify
from be.model.search import Search,Filter

bp_search = Blueprint("search", __name__, url_prefix="/search")

@bp_search.route("/keyword", methods=["POST"])
def search_books():
    s=Search()
    keyword=request.json.get("keyword")
    if keyword is None:
        keyword=""
    filter=Filter()
    if request.json.get("filter") is not None:
        filter.isbn=request.json.get("filter").get("isbn")
        filter.pages[0]=request.json.get("filter").get("pages_from")
        filter.pages[1]=request.json.get("filter").get("pages_to")
        filter.price[0]=request.json.get("filter").get("price_from")
        filter.price[1]=request.json.get("filter").get("price_to")
        filter.publish_date[0]=request.json.get("filter").get("publish_date_from")
        filter.publish_date[1]=request.json.get("filter").get("publish_date_to")
        filter.stock_level[0]=request.json.get("filter").get("stock_from")
        filter.stock_level[1]=request.json.get("filter").get("stock_to")
        filter.store_id=request.json.get("filter").get("store_id")
    
    code,message,results=s.search(keyword,filter)
    return jsonify({"message": message, "count":len(results),"results": results}), code
