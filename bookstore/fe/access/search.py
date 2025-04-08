from urllib.parse import urljoin
import requests

from be.model.search import Filter

class Search:
    def __init__(self,url_prefix):
        self.url_prefix=urljoin(url_prefix,"search/")

    def search_books(self,keyword: str,filter: Filter):
        json={
            "keyword":keyword,
            "filter":filter.to_json_dict()
        }
        url=urljoin(self.url_prefix,"keyword")
        r=requests.post(url,json=json)
        if r.status_code!=200:
            raise RuntimeError(r.json()["message"])
        return r.status_code
