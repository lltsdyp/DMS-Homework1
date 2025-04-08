## 搜索

- 关键字搜索：搜索图书的名称或者作者或者描述等中含有当前关键字的书籍信息
- 参数化搜索：根据用户选择的参数搜索书籍信息
两者可以结合使用

#### URL

POST http://[address]/search/keyword

#### Request
Headers:

Body:
```json
{
    "keyword":"key",
    "start": 0,
    "filter": {
        "store_id": "store_id",
        "stock_from":0,
        "stock_to":200,
        "publish_date_from": "publish_date",
        "publish_date_to": "publish_date",
        "pages_from":0,
        "pages_to":200,
        "price_from":0,
        "price_to":200,
        "isbn":"isbn",
    }
}
```

属性说明

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
keyword | string | 查询的关键字| Y
start | int | 搜索结果显示的起始位置 | N
filter| object | 搜索条件 | Y

filter类：

变量名 | 类型 | 描述 | 是否可为空
---|---|---|---
store_id | string | 若指定，只显示给定店铺id的结果 | Y
stock | int | 若指定，只显示库存范围在from到to之间的结果 | Y
publish_date | string | 若指定，只显示出版日期在from到to之间的结果 | Y
pages | int | 若指定，只显示页数范围在from到to之间的结果 | Y
price | int | 若指定，只显示价格范围在from到to之间的结果 | Y
isbn | string | 若指定，只显示相应isbn号对应的结果 | Y


#### Response
Status Code:

码 | 描述
--- | ---
200 | 成功获取搜索结果
5XX | 服务器错误

```json
{
    "message":"ok",
    "count": 10,
    "results":[
        {
            "book_id": "book_id",
            "store_id": "store_id",
        }
    ]
}
```
