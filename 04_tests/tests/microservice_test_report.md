# 微服务自动化测试报告

- 生成时间：2026-08-29T15:57:43
- 测试总数：24
- 公开 API 方法总数：54
- 总体结果：OK

| 服务 | 测试数 | API 方法数 | API 契约覆盖 | 结果 |
| --- | ---: | ---: | --- | --- |
| user-service | 7 | 11 | OK | OK |
| trade-service | 10 | 22 | OK | OK |
| lifestyle-service | 7 | 21 | OK | OK |

## 公开 API 覆盖清单

### user-service

| 方法 | 路径 |
| --- | --- |
| GET | `/health/live` |
| GET | `/health/ready` |
| GET | `/health/version` |
| POST | `/register` |
| POST | `/login` |
| POST | `/logout` |
| GET | `/users/<int:user_id>` |
| PATCH | `/users/<int:user_id>/profile` |
| PATCH | `/users/<int:user_id>/status` |
| PATCH | `/users/<int:user_id>/role` |
| GET | `/internal/users` |

### trade-service

| 方法 | 路径 |
| --- | --- |
| GET | `/health/live` |
| GET | `/health/ready` |
| GET | `/health/version` |
| GET | `/foods` |
| POST | `/foods` |
| GET | `/foods/<int:food_id>` |
| PATCH | `/foods/<int:food_id>/status` |
| POST | `/orders` |
| GET | `/orders/<int:order_id>` |
| POST | `/orders/<int:order_id>/comment` |
| POST | `/orders/<int:order_id>/accept` |
| POST | `/orders/<int:order_id>/prepare` |
| POST | `/orders/<int:order_id>/pickup` |
| POST | `/orders/<int:order_id>/deliver` |
| GET | `/cart` |
| POST | `/cart` |
| PATCH | `/cart/<int:item_id>` |
| DELETE | `/cart/<int:item_id>` |
| POST | `/cart/checkout` |
| POST | `/groupbuy` |
| POST | `/groupbuy/redeem` |
| GET | `/rider/orders` |

### lifestyle-service

| 方法 | 路径 |
| --- | --- |
| GET | `/health/live` |
| GET | `/health/ready` |
| GET | `/health/version` |
| GET | `/hotels` |
| POST | `/hotels` |
| GET | `/hotels/<int:hotel_id>` |
| POST | `/hotel-orders` |
| GET | `/hotel-orders/<int:order_id>` |
| POST | `/hotel-orders/<int:order_id>/comment` |
| GET | `/plays` |
| POST | `/plays` |
| GET | `/plays/<int:play_id>` |
| POST | `/play-orders` |
| GET | `/play-orders/<int:order_id>` |
| POST | `/play-orders/<int:order_id>/comment` |
| GET | `/blogs` |
| POST | `/blogs` |
| GET | `/blogs/<int:blog_id>` |
| DELETE | `/blogs/<int:blog_id>` |
| POST | `/blogs/<int:blog_id>/comments` |
| DELETE | `/comments/<int:comment_id>` |
