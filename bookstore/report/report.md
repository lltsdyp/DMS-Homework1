# 组员分工

- 徐卓一_10235102432：完成了收发货，主动取消订单，定时删除订单，查找历史订单等功能接口及其测试
- 季子墨_10235101439：提供运行环境，维护了docker容器方便开发，完成了SQLite到MongoDB的转换，实现了搜索功能及其测试

# 功能介绍

### 关键字搜索和参数化搜索

当前系统支持两类搜索方式：

- 关键字搜索：搜索图书的名称或者作者或者描述等中含有当前关键字的书籍信息
- 参数化搜索：根据用户选择的参数搜索书籍信息

两者可以结合使用

在参数化搜索中，用户可以指定一些参数，比如店铺id，库存范围，页数范围，价格范围，isbn号等，这样我们就可以更加精确的搜索出需要的书籍

其json参数如下：

| 变量名  | 类型   | 描述                   | 是否可为空 |
| ------- | ------ | ---------------------- | ---------- |
| keyword | string | 查询的关键字           | Y          |
| start   | int    | 搜索结果显示的起始位置 | N          |
| filter  | object | 搜索条件               | Y          |

filter类：

| 变量名   | 类型   | 描述                                       | 是否可为空 |
| -------- | ------ | ------------------------------------------ | ---------- |
| store_id | string | 若指定，只显示给定店铺id的结果             | Y          |
| stock    | int    | 若指定，只显示库存范围在from到to之间的结果 | Y          |
| pages    | int    | 若指定，只显示页数范围在from到to之间的结果 | Y          |
| price    | int    | 若指定，只显示价格范围在from到to之间的结果 | Y          |
| isbn     | string | 若指定，只显示相应isbn号对应的结果         | Y          |

### 创建订单(new_order)

在new_order函数中，我们需要创建订单（insert_one），同时需要维护商家的库存（这里需要区分的是，维护库存一定是在创建订单这一步做，而不是在付款或者收货后做）
另外，我们还需要维护 `new_order_detail_collection`这个字段
因为一个order可能会买多本书，而具体每种书的购买信息会在new_order_detail_collection字段里维护

```python
self.store_instance.new_order_collection.insert_one(
                {
                    "order_id":uid,
                    "store_id":store_id,
                    "user_id":user_id,
                    'create_time':now_time,
                    "status":0
                }
            )
```

### 发货(send_books)

在seller后端文件中

```python
self.store_instance.new_order_collection.update_one({
                "order_id": order_id,
            }, {
                "$set": {"status": 2}
            })
```

我们首先会进行各种有效性测试，然后最终是将状态更改为2，表示为已付款已发货，但未收货

### 收货(receive_books)

```python
self.store_instance.new_order_collection.update_one({
                "order_id": order_id,
            }, {
                "$set": {"status": 3}
            })
```

找到所有满足user_id: str, order_id: str的status为2的订单，然后将其更改为3，表示订单已完成
对于其它status则要错误处理
==测试==

1. **测试成功接收书籍 (`test_ok`)**：
   - 测试卖家成功发送书籍后，买家能否正确接收这些书籍。
2. **测试订单错误 (`test_order_error`)**：
   - 测试当买家尝试接收书籍时，如果订单ID错误，系统应返回错误。
3. **测试书籍未发送 (`test_books_not_send`)**：
   - 测试当卖家尚未发送书籍时，买家尝试接收书籍，系统应返回错误。
4. **测试重复接收书籍 (`test_books_repeat_receive`)**：
   - 测试卖家成功发送书籍后，买家重复接收书籍，系统应返回错误。

### 查看历史订单(check_hist_order)

这里我们维护了一个数组，里面维护了以下的字段

```python
order_list.append
({
	"order_id": order_id,
	"store_id": store_id,
	"status": status,
	"details": details_arr
})
```

我们通过用户id，找到这个用户的所有状态的所有订单
然后再通过找到的订单，从new_order_detail_collection中找到这个订单中的所有购买情况
最后一起append到数组里
==测试==：
测试有订单的情况，用户不存在的情况，举例如下：

```python
def test_non_exist_user_id(self):
        code = self.buyer.check_hist_order(self.buyer_id + 'x')
        assert code != 200
```

### 超时自动取消订单(auto_cancel_order)

为了实现这个功能我们还在new_order_collection中维护了create_time字段，然后在每次创建订单的时候都记录当前的时间，然后再引入另一个调度器定期调用 `auto_cancel_order`函数

```python
scheduler = BackgroundScheduler()
scheduler.add_job(Buyer().auto_cancel_order, 'interval', id='5_second_job', seconds=5)
scheduler.start()
```

在 `auto_cancel_order`函数中，我们设置等待时间为20s，然后每次进入这个函数的时候，就会将所有status为0的订单拿出，并计算create_time到现在的时间是否超过20s，如果超过20s我们就会将订单自动删除

```python
wait_time = 20  # 等待时间20s
            interval = datetime.utcnow() - timedelta(seconds=wait_time) # UTC时间
            orders_to_cancel = self.store_instance.new_order_collection.find({"create_time": {"$lte": interval}, "status": 0})
```

## 测试结果

![test_case](/root/DMS-Homework1/bookstore/report/image/test_case.png)

![pass](/root/DMS-Homework1/bookstore/report/image/pass.png)

# 文档数据库设计

我们在数据库中创建了如下的一些数据集：

```
new_order
new_order_detail
store
user
user_store
```

### new_order

这个文档集中存储了订单的状态，可以通过这个数据集查询订单发货，收货等状态
示例：

```
{
  _id: ObjectId('67ea5a9cabb38b6aa386709f'),
  order_id: 'buyer_5_1fada132-0e0f-11f0-8bd8-0242ac110002_store_s_1_1_1fada132-0e0f-11f0-8bd8-0242ac110002_26b3ed56-0e0f-11f0-ae0d-0242ac110002',
  store_id: 'store_s_1_1_1fada132-0e0f-11f0-8bd8-0242ac110002',
  user_id: 'buyer_5_1fada132-0e0f-11f0-8bd8-0242ac110002'
}
```

### new_order_detail

这个文档集中存储了订单的详细信息，可以通过这个数据集查询订单购买书籍的情况
示例：

```
{
  _id: ObjectId('67ea5a9cabb38b6aa386709c'),
  order_id: 'buyer_5_1fada132-0e0f-11f0-8bd8-0242ac110002_store_s_1_1_1fada132-0e0f-11f0-8bd8-0242ac110002_26b3ed56-0e0f-11f0-ae0d-0242ac110002',
  book_id: '36952611',
  count: 9,
  price: 4990
}
```

### store

这个文档集存储了店铺的信息，以及店铺中在售书籍的信息
示例：

```
{
  _id: ObjectId('67ea5a8eabb38b6aa3867023'),
  store_id: 'test_add_books_store_id_1e8129aa-0e0f-11f0-8bd8-0242ac110002',
  book_id: '30331835',
  book_info: {...}，
  stock_level: 0
}
```

### user

这个文档集存储了平台用户的信息
示例：

```
{
  _id: ObjectId('67e2c88f02204b688c00afa1'),
  user_id: 'test_add_books_seller_id_fb65f28e-098b-11f0-a90e-0242ac110002',
  password: 'test_add_books_seller_id_fb65f28e-098b-11f0-a90e-0242ac110002',
  balance: 0,
  token: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoidGVzdF9hZGRfYm9va3Nfc2VsbGVyX2lkX2ZiNjVmMjhlLTA5OGItMTFmMC1hOTBlLTAyNDJhYzExMDAwMiIsInRlcm1pbmFsIjoibXkgdGVybWluYWwiLCJ0aW1lc3RhbXAiOjE3NDI5MTU3MjcuMTUzNDExfQ.98rmcM5wQZBYlHSNFE_2hf7kddhYNYsff9Ncn9xZuuE',
  terminal: 'my terminal'
}
```

### user_store

这个文档集记录了平台和店铺的关联，用来确定卖家
示例：

```
{
  _id: ObjectId('67e2c88f02204b688c00afa2'),
  store_id: 'test_add_books_store_id_fb65f504-098b-11f0-a90e-0242ac110002',
  user_id: 'test_add_books_seller_id_fb65f28e-098b-11f0-a90e-0242ac110002'
}
```

# API接口设计

## Search

## 搜索

- 关键字搜索：搜索图书的名称或者作者或者描述等中含有当前关键字的书籍信息
- 参数化搜索：根据用户选择的参数搜索书籍信息
  两者可以结合使用

#### URL

POST http://[address]/search/detailed

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

| 变量名  | 类型   | 描述                   | 是否可为空 |
| ------- | ------ | ---------------------- | ---------- |
| keyword | string | 查询的关键字           | Y          |
| start   | int    | 搜索结果显示的起始位置 | N          |
| filter  | object | 搜索条件               | Y          |

filter类：

| 变量名       | 类型   | 描述                                       | 是否可为空 |
| ------------ | ------ | ------------------------------------------ | ---------- |
| store_id     | string | 若指定，只显示给定店铺id的结果             | Y          |
| stock        | int    | 若指定，只显示库存范围在from到to之间的结果 | Y          |
| publish_date | string | 若指定，只显示出版日期在from到to之间的结果 | Y          |
| pages        | int    | 若指定，只显示页数范围在from到to之间的结果 | Y          |
| price        | int    | 若指定，只显示价格范围在from到to之间的结果 | Y          |
| isbn         | string | 若指定，只显示相应isbn号对应的结果         | Y          |

#### Response

Status Code:

| 码  | 描述             |
| --- | ---------------- |
| 200 | 成功获取搜索结果 |
| 5XX | 服务器错误       |

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

## buyer

## 买家下单

#### URL：

POST http://[address]/buyer/new_order

#### Request

##### Header:

| key   | 类型   | 描述               | 是否可为空 |
| ----- | ------ | ------------------ | ---------- |
| token | string | 登录产生的会话标识 | N          |

##### Body:

```json
{
  "user_id": "buyer_id",
  "store_id": "store_id",
  "books": [
    {
      "id": "1000067",
      "count": 1
    },
    {
      "id": "1000134",
      "count": 4
    }
  ]
}
```

##### 属性说明：

| 变量名   | 类型   | 描述         | 是否可为空 |
| -------- | ------ | ------------ | ---------- |
| user_id  | string | 买家用户ID   | N          |
| store_id | string | 商铺ID       | N          |
| books    | class  | 书籍购买列表 | N          |

books数组：

| 变量名 | 类型   | 描述     | 是否可为空 |
| ------ | ------ | -------- | ---------- |
| id     | string | 书籍的ID | N          |
| count  | string | 购买数量 | N          |

#### Response

Status Code:

| 码  | 描述             |
| --- | ---------------- |
| 200 | 下单成功         |
| 5XX | 买家用户ID不存在 |
| 5XX | 商铺ID不存在     |
| 5XX | 购买的图书不存在 |
| 5XX | 商品库存不足     |

##### Body:

```json
{
  "order_id": "uuid"
}
```

##### 属性说明：

| 变量名   | 类型   | 描述                        | 是否可为空 |
| -------- | ------ | --------------------------- | ---------- |
| order_id | string | 订单号，只有返回200时才有效 | N          |

## 买家付款

#### URL：

POST http://[address]/buyer/payment

#### Request

##### Body:

```json
{
  "user_id": "buyer_id",
  "order_id": "order_id",
  "password": "password"
}
```

##### 属性说明：

| 变量名   | 类型   | 描述         | 是否可为空 |
| -------- | ------ | ------------ | ---------- |
| user_id  | string | 买家用户ID   | N          |
| order_id | string | 订单ID       | N          |
| password | string | 买家用户密码 | N          |

#### Response

Status Code:

| 码  | 描述         |
| --- | ------------ |
| 200 | 付款成功     |
| 5XX | 账户余额不足 |
| 5XX | 无效参数     |
| 401 | 授权失败     |

## 买家充值

#### URL：

POST http://[address]/buyer/add_funds

#### Request

##### Body:

```json
{
  "user_id": "user_id",
  "password": "password",
  "add_value": 10
}
```

##### 属性说明：

| key       | 类型   | 描述                 | 是否可为空 |
| --------- | ------ | -------------------- | ---------- |
| user_id   | string | 买家用户ID           | N          |
| password  | string | 用户密码             | N          |
| add_value | int    | 充值金额，以分为单位 | N          |

Status Code:

| 码  | 描述     |
| --- | -------- |
| 200 | 充值成功 |
| 401 | 授权失败 |
| 5XX | 无效参数 |

## 买家收货

#### URL：

POST http://[address]/buyer/receive_books

#### Request

##### Body:

```json
{
    "user_id": "self.user_id",
    "order_id": "order_id",
}
```

##### 属性说明：

| key      | 类型   | 描述       | 是否可为空 |
| -------- | ------ | ---------- | ---------- |
| user_id  | string | 买家用户ID | N          |
| order_id | string | 订单ID     | N          |

Status Code:

| 码  | 描述       |
| --- | ---------- |
| 200 | 收货成功   |
| 511 | 无效用户名 |
| 518 | 无效订单号 |

## 买家取消订单

#### URL：

POST http://[address]/buyer/cancel_order

#### Request

##### Body:

```json
{
    "user_id": "self.user_id",
    "order_id": "order_id",
}
```

##### 属性说明：

| key      | 类型   | 描述       | 是否可为空 |
| -------- | ------ | ---------- | ---------- |
| user_id  | string | 买家用户ID | N          |
| order_id | string | 订单ID     | N          |

Status Code:

| 码  | 描述       |
| --- | ---------- |
| 200 | 取消成功   |
| 511 | 无效用户名 |
| 518 | 无效订单号 |
| 513 | 无效商店ID |

## 查看历史订单

#### URL：

POST http://[address]/buyer/check_hist_order

#### Request

##### Body:

```json
{
    "user_id": "self.user_id"
}
```

##### 属性说明：

| key     | 类型   | 描述       | 是否可为空 |
| ------- | ------ | ---------- | ---------- |
| user_id | string | 买家用户ID | N          |

Status Code:

| 码  | 描述                   |
| --- | ---------------------- |
| 200 | 查看成功，包含有和没有 |
| 511 | 无效用户名             |

## 定时取消订单

#### URL：

POST http://[address]/buyer/auto_cancel_order

#### Request

##### Body:

```json
{
    "user_id": "self.user_id"
}
```

##### 属性说明：

| key     | 类型   | 描述       | 是否可为空 |
| ------- | ------ | ---------- | ---------- |
| user_id | string | 买家用户ID | N          |

Status Code:

| 码  | 描述     |
| --- | -------- |
| 200 | 取消成功 |
| 517 | 库存问题 |

## Seller

## 创建商铺

#### URL

POST http://[address]/seller/create_store

#### Request

Headers:

| key   | 类型   | 描述               | 是否可为空 |
| ----- | ------ | ------------------ | ---------- |
| token | string | 登录产生的会话标识 | N          |

Body:

```json
{
  "user_id": "$seller id$",
  "store_id": "$store id$"
}
```

| key      | 类型   | 描述       | 是否可为空 |
| -------- | ------ | ---------- | ---------- |
| user_id  | string | 卖家用户ID | N          |
| store_id | string | 商铺ID     | N          |

#### Response

Status Code:

| 码  | 描述         |
| --- | ------------ |
| 200 | 创建商铺成功 |
| 5XX | 商铺ID已存在 |

## 商家添加书籍信息

#### URL：

POST http://[address]/seller/add_book

#### Request

Headers:

| key   | 类型   | 描述               | 是否可为空 |
| ----- | ------ | ------------------ | ---------- |
| token | string | 登录产生的会话标识 | N          |

Body:

```json
{
  "user_id": "$seller user id$",
  "store_id": "$store id$",
  "book_info": {
    "tags": [
      "tags1",
      "tags2",
      "tags3",
      "..."
    ],
    "pictures": [
      "$Base 64 encoded bytes array1$",
      "$Base 64 encoded bytes array2$",
      "$Base 64 encoded bytes array3$",
      "..."
    ],
    "id": "$book id$",
    "title": "$book title$",
    "author": "$book author$",
    "publisher": "$book publisher$",
    "original_title": "$original title$",
    "translator": "translater",
    "pub_year": "$pub year$",
    "pages": 10,
    "price": 10,
    "binding": "平装",
    "isbn": "$isbn$",
    "author_intro": "$author introduction$",
    "book_intro": "$book introduction$",
    "content": "$chapter1 ...$"
  },
  "stock_level": 0
}
```

属性说明：

| 变量名      | 类型   | 描述                | 是否可为空 |
| ----------- | ------ | ------------------- | ---------- |
| user_id     | string | 卖家用户ID          | N          |
| store_id    | string | 商铺ID              | N          |
| book_info   | class  | 书籍信息            | N          |
| stock_level | int    | 初始库存，大于等于0 | N          |

book_info类：

| 变量名         | 类型   | 描述             | 是否可为空 |
| -------------- | ------ | ---------------- | ---------- |
| id             | string | 书籍ID           | N          |
| title          | string | 书籍题目         | N          |
| author         | string | 作者             | Y          |
| publisher      | string | 出版社           | Y          |
| original_title | string | 原书题目         | Y          |
| translator     | string | 译者             | Y          |
| pub_year       | string | 出版年月         | Y          |
| pages          | int    | 页数             | Y          |
| price          | int    | 价格(以分为单位) | N          |
| binding        | string | 装帧，精状/平装  | Y          |
| isbn           | string | ISBN号           | Y          |
| author_intro   | string | 作者简介         | Y          |
| book_intro     | string | 书籍简介         | Y          |
| content        | string | 样章试读         | Y          |
| tags           | array  | 标签             | Y          |
| pictures       | array  | 照片             | Y          |

tags和pictures：

tags 中每个数组元素都是string类型
picture 中每个数组元素都是string（base64表示的bytes array）类型

#### Response

Status Code:

| 码  | 描述             |
| --- | ---------------- |
| 200 | 添加图书信息成功 |
| 5XX | 卖家用户ID不存在 |
| 5XX | 商铺ID不存在     |
| 5XX | 图书ID已存在     |

## 商家添加书籍库存

#### URL

POST http://[address]/seller/add_stock_level

#### Request

Headers:

| key   | 类型   | 描述               | 是否可为空 |
| ----- | ------ | ------------------ | ---------- |
| token | string | 登录产生的会话标识 | N          |

Body:

```json
{
  "user_id": "$seller id$",
  "store_id": "$store id$",
  "book_id": "$book id$",
  "add_stock_level": 10
}
```

| key             | 类型   | 描述         | 是否可为空 |
| --------------- | ------ | ------------ | ---------- |
| user_id         | string | 卖家用户ID   | N          |
| store_id        | string | 商铺ID       | N          |
| book_id         | string | 书籍ID       | N          |
| add_stock_level | int    | 增加的库存量 | N          |

#### Response

Status Code:

| 码  | 描述         |
| --- | :----------- |
| 200 | 创建商铺成功 |
| 5XX | 商铺ID不存在 |
| 5XX | 图书ID不存在 |

## 商家发货

#### URL

POST http://[address]/seller/send_books

#### Request

Body:

```json
{
  "user_id": "$seller id$",
  "order_id": "$order id$",
}
```

| key      | 类型   | 描述       | 是否可为空 |
| -------- | ------ | ---------- | ---------- |
| user_id  | string | 卖家用户ID | N          |
| order_id | string | 订单ID     | N          |

#### Response

Status Code:

| 码  | 描述         |
| --- | :----------- |
| 200 | 发货成功     |
| 511 | 用户ID不存在 |
| 518 | 订单ID不存在 |

## Auth

## 注册用户

#### URL：

POST http://$address$/auth/register

#### Request

Body:

```
{
    "user_id":"$user name$",
    "password":"$user password$"
}
```

| 变量名   | 类型   | 描述     | 是否可为空 |
| -------- | ------ | -------- | ---------- |
| user_id  | string | 用户名   | N          |
| password | string | 登陆密码 | N          |

#### Response

Status Code:

| 码  | 描述                 |
| --- | -------------------- |
| 200 | 注册成功             |
| 5XX | 注册失败，用户名重复 |

Body:

```
{
    "message":"$error message$"
}
```

| 变量名  | 类型   | 描述                       | 是否可为空 |
| ------- | ------ | -------------------------- | ---------- |
| message | string | 返回错误消息，成功时为"ok" | N          |

## 注销用户

#### URL：

POST http://$address$/auth/unregister

#### Request

Body:

```
{
    "user_id":"$user name$",
    "password":"$user password$"
}
```

| 变量名   | 类型   | 描述     | 是否可为空 |
| -------- | ------ | -------- | ---------- |
| user_id  | string | 用户名   | N          |
| password | string | 登陆密码 | N          |

#### Response

Status Code:

| 码  | 描述                               |
| --- | ---------------------------------- |
| 200 | 注销成功                           |
| 401 | 注销失败，用户名不存在或密码不正确 |

Body:

```
{
    "message":"$error message$"
}
```

| 变量名  | 类型   | 描述                       | 是否可为空 |
| ------- | ------ | -------------------------- | ---------- |
| message | string | 返回错误消息，成功时为"ok" | N          |

## 用户登录

#### URL：

POST http://$address$/auth/login

#### Request

Body:

```
{
    "user_id":"$user name$",
    "password":"$user password$",
    "terminal":"$terminal code$"
}
```

| 变量名   | 类型   | 描述     | 是否可为空 |
| -------- | ------ | -------- | ---------- |
| user_id  | string | 用户名   | N          |
| password | string | 登陆密码 | N          |
| terminal | string | 终端代码 | N          |

#### Response

Status Code:

| 码  | 描述                       |
| --- | -------------------------- |
| 200 | 登录成功                   |
| 401 | 登录失败，用户名或密码错误 |

Body:

```
{
    "message":"$error message$",
    "token":"$access token$"
}
```

| 变量名  | 类型   | 描述                                                              | 是否可为空   |
| ------- | ------ | ----------------------------------------------------------------- | ------------ |
| message | string | 返回错误消息，成功时为"ok"                                        | N            |
| token   | string | 访问token，用户登录后每个需要授权的请求应在headers中传入这个token | 成功时不为空 |

#### 说明

1.terminal标识是哪个设备登录的，不同的设备拥有不同的ID，测试时可以随机生成。

2.token是登录后，在客户端中缓存的令牌，在用户登录时由服务端生成，用户在接下来的访问请求时不需要密码。token会定期地失效，对于不同的设备，token是不同的。token只对特定的时期特定的设备是有效的。

## 用户更改密码

#### URL：

POST http://$address$/auth/password

#### Request

Body:

```
{
    "user_id":"$user name$",
    "oldPassword":"$old password$",
    "newPassword":"$new password$"
}
```

| 变量名      | 类型   | 描述         | 是否可为空 |
| ----------- | ------ | ------------ | ---------- |
| user_id     | string | 用户名       | N          |
| oldPassword | string | 旧的登陆密码 | N          |
| newPassword | string | 新的登陆密码 | N          |

#### Response

Status Code:

| 码  | 描述         |
| --- | ------------ |
| 200 | 更改密码成功 |
| 401 | 更改密码失败 |

Body:

```
{
    "message":"$error message$",
}
```

| 变量名  | 类型   | 描述                       | 是否可为空 |
| ------- | ------ | -------------------------- | ---------- |
| message | string | 返回错误消息，成功时为"ok" | N          |

## 用户登出

#### URL：

POST http://$address$/auth/logout

#### Request

Headers:

| key   | 类型   | 描述      |
| ----- | ------ | --------- |
| token | string | 访问token |

Body:

```
{
    "user_id":"$user name$"
}
```

| 变量名  | 类型   | 描述   | 是否可为空 |
| ------- | ------ | ------ | ---------- |
| user_id | string | 用户名 | N          |

#### Response

Status Code:

| 码  | 描述                        |
| --- | --------------------------- |
| 200 | 登出成功                    |
| 401 | 登出失败，用户名或token错误 |

Body:

```
{
    "message":"$error message$"
}
```

| 变量名  | 类型   | 描述                       | 是否可为空 |
| ------- | ------ | -------------------------- | ---------- |
| message | string | 返回错误消息，成功时为"ok" | N          |

# 工作亮点

## 索引设计

最开始，我们暂未使用索引，但是发现这会带来一些问题：
![error](./image/no-index-error.png)
首先，如果没有索引，`fe/test/test_register.py::TestRegister::test_unregister_error_authorization `将会出错，因为我们没有限制 `user_id`的唯一性（同样的，还有 `store_id`）
![time](./image/no-index-time.png)
此外，这样的查询性能可能会很差，尤其是我们在test_bench的过程中会消耗特别长的时间

为了解决这些问题，我们可以在数据库上建立索引，从而优化性能同时解决bug

我们使用mongotop检查性能瓶颈
![time1](./image/no-index-top1.png)
![time2](./image/no-index-top2.png)
可以看出，主要的读写时间都消耗在 `store`文档集以及 `new_order_detail`文档集上。

因此，我们需要在 `store.store_id`,`user.user_id`上建立Unique索引，保证其唯一性，而在 `new_order_detail`文档集上建立索引来提升查询性能。

进行上述操作后，我们再运行一次测试脚本，可以看出性能有了明显的提升
![optimized-1](./image/final.png)

同时，性能瓶颈的时间消耗也显著减少
![optimized-2](./image/final-top.png)

## docker容器与git使用

### docker容器应用

我们为了统一python依赖和数据库环境，在实验开始前维护了一个docker容器
对于每一个组员只需要直接拿到容器使用，而不需要再重复配置环境，同时也避免了测试环境的差异

```docker
FROM ubuntu:22.04
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Asia/Shanghai

# Basic utility packages
RUN sed -i 's@http://archive.ubuntu.com/@http://mirrors.tuna.tsinghua.edu.cn/@g' /etc/apt/sources.list && \
    sed -i 's@http://security.ubuntu.com/@http://mirrors.tuna.tsinghua.edu.cn/@g' /etc/apt/sources.list && \
    apt clean &&\
    apt update &&\
    apt install -y sudo bash git cmake vim tar openssh-server rsync python3.10 python3-pip gnupg curl

# Install MongoDB
RUN curl -fsSL https://www.mongodb.org/static/pgp/server-8.0.asc | \
    gpg -o /usr/share/keyrings/mongodb-server-8.0.gpg \
    --dearmor &&\
    echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-8.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/8.0 multiverse" | tee /etc/apt/sources.list.d/mongodb-org-8.0.list
# This step takes a long time because of the large size of the MongoDB package
RUN apt update &&\
    apt install -y mongodb-org

EXPOSE 27017

# add user and initialize mongodb
RUN mkdir -p /data/db /var/log/mongodb &&\
    useradd -ms /bin/bash -G sudo user &&\
    passwd -d user &&\
    chown -R user:user /data/db /var/log/mongodb

COPY docker/mongod.conf /etc/mongod.conf

VOLUME /home/user/bookstore
USER user
WORKDIR /home/user
CMD ["/bin/bash"]
```

## git仓库应用

我们在小组分工以后确定自己要完成的部分，然后每次完成一部分后就push到远程仓库中，然后merge以后再同步进行阶段测试，然后开始下一部分的开发
git操作方便了bug出现以后的版本回退，以及同步的代码开发，减小沟通成本，冲突问题可以在merge的时候发现并调整
![git_use](/root/DMS-Homework1/bookstore/report/image/git_use.png)

# 仓库地址
[lltsdyp/DMS-Homework1: 数据管理系统大作业1仓库](https://github.com/lltsdyp/DMS-Homework1)

