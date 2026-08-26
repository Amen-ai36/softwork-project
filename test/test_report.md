# 自动化测试报告

- 生成时间：2026-08-26 16:45:08
- 运行环境：Windows-11-10.0.26200-SP0
- Python：3.13.2 / Django：3.2.11
- 数据库：SQLite（food_master.test_settings）

## 结果汇总

| 项目 | 数量 |
| --- | --- |
| 测试总数 | 109 |
| 通过数 | 108 |
| 失败数 | 0 |
| 跳过数（环境原因） | 1 |
| 结果 | OK |

> 说明：任一测试失败时，`run_tests.py` 会返回非 0 退出码，
> CI/CD 流水线中后续的构建、发布镜像、部署步骤将不会执行。

## 完整输出

```text
Operations to perform:
  Synchronize unmigrated apps: messages, staticfiles
  Apply all migrations: admin, auth, contenttypes, myapp, sessions
Synchronizing apps without migrations:
  Creating tables...
    Running deferred SQL...
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK
  Applying admin.0003_logentry_add_action_flag_choices... OK
  Applying contenttypes.0002_remove_content_type_name... OK
  Applying auth.0002_alter_permission_name_max_length... OK
  Applying auth.0003_alter_user_email_max_length... OK
  Applying auth.0004_alter_user_username_opts... OK
  Applying auth.0005_alter_user_last_login_null... OK
  Applying auth.0006_require_contenttypes_0002... OK
  Applying auth.0007_alter_validators_add_error_messages... OK
  Applying auth.0008_alter_user_username_max_length... OK
  Applying auth.0009_alter_user_last_name_max_length... OK
  Applying auth.0010_alter_group_name_max_length... OK
  Applying auth.0011_update_proxy_permissions... OK
  Applying auth.0012_alter_user_first_name_max_length... OK
  Applying myapp.0001_initial... OK
  Applying myapp.0002_auto_20260601_1125... OK
  Applying myapp.0003_auto_20260601_1248... OK
  Applying myapp.0004_auto_20260601_1254... OK
  Applying myapp.0005_auto_20260601_1306... OK
  Applying myapp.0006_blog... OK
  Applying myapp.0007_blog_isdeleted_comment... OK
  Applying myapp.0008_alter_blog_id_alter_comment_id_alter_food_id_and_more... OK
  Applying myapp.0009_order_cost... OK
  Applying myapp.0010_hotel... OK
  Applying myapp.0011_user_usertype... OK
  Applying myapp.0012_hotelorder... OK
  Applying myapp.0013_food_hotel_merchant... OK
  Applying myapp.0014_order_rider_play_playorder... OK
  Applying myapp.0015_alter_user_usertype... OK
  Applying myapp.0016_groupbuycoupon... OK
  Applying myapp.0017_temp... OK
  Applying myapp.0018_order_is_abnormal... OK
  Applying myapp.0019_auto_20260610_1714... OK
  Applying sessions.0001_initial... OK
System check identified no issues (0 silenced).
阿里云 LLM API 调用失败: 500 Server Error
阿里云 LLM API 调用失败: boom
ALIYUN_API_KEY/DASHSCOPE_API_KEY is not configured
Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...

test_admin_passes_and_gets_app_admin (test.test_unit.AdminRequiredDecoratorTest.test_admin_passes_and_gets_app_admin)
主流程：管理员访问可进入，request.app_admin 指向当前管理员 ... ok
test_non_admin_redirects_to_login (test.test_unit.AdminRequiredDecoratorTest.test_non_admin_redirects_to_login)
异常分支：非管理员（普通用户）访问被重定向 ... ok
test_not_logged_in_redirects_to_login (test.test_unit.AdminRequiredDecoratorTest.test_not_logged_in_redirects_to_login)
异常分支：未登录访问被重定向到登录页 ... ok
test_group_buy_coupon_unique_constraint_enforced (test.test_unit.GroupBuyCodeRuleTest.test_group_buy_coupon_unique_constraint_enforced)
业务规则：数据库层核销码唯一约束 ... ok
test_make_group_buy_code_avoids_existing_codes (test.test_unit.GroupBuyCodeRuleTest.test_make_group_buy_code_avoids_existing_codes)
业务规则：遇到已存在的核销码应重新生成（唯一性） ... ok
test_make_group_buy_code_format (test.test_unit.GroupBuyCodeRuleTest.test_make_group_buy_code_format)
主流程：核销码为 10 位大写十六进制字符串 ... ok
test_known_room_types_return_corresponding_price (test.test_unit.HotelPriceRuleTest.test_known_room_types_return_corresponding_price)
主流程：每种合法房型都能取到正确价格 ... ok
test_none_price_returns_none (test.test_unit.HotelPriceRuleTest.test_none_price_returns_none)
异常分支：未配置价格的房型（字段为 None）应返回 None ... ok
test_room_type_field_mapping_is_consistent (test.test_unit.HotelPriceRuleTest.test_room_type_field_mapping_is_consistent)
业务规则：ROOM_PRICE_FIELDS 与 ROOM_TYPE_LABELS 的键集合应一致 ... ok
test_unknown_room_type_returns_none (test.test_unit.HotelPriceRuleTest.test_unknown_room_type_returns_none)
异常分支：未知房型应返回 None ... ok
test_save_hotel_review_above_five_rejected (test.test_unit.HotelReviewRuleTest.test_save_hotel_review_above_five_rejected)
异常分支：超过 5 分不允许 ... ok
test_save_hotel_review_comment_max_length_accepted (test.test_unit.HotelReviewRuleTest.test_save_hotel_review_comment_max_length_accepted)
边界分支：评论恰好 200 字符允许 ... ok
test_save_hotel_review_comment_too_long_rejected (test.test_unit.HotelReviewRuleTest.test_save_hotel_review_comment_too_long_rejected)
异常分支：评论超过 200 字符不允许 ... ok
test_save_hotel_review_non_numeric_rejected (test.test_unit.HotelReviewRuleTest.test_save_hotel_review_non_numeric_rejected)
异常分支：非数值评分不允许（TypeError/ValueError） ... ok
test_save_hotel_review_success_updates_order_and_hotel (test.test_unit.HotelReviewRuleTest.test_save_hotel_review_success_updates_order_and_hotel)
主流程：合法评价 → 订单 pos=5、评分保存、酒店评分/人数更新 ... ok
test_save_hotel_review_zero_score_rejected (test.test_unit.HotelReviewRuleTest.test_save_hotel_review_zero_score_rejected)
异常分支：0 分不允许 ... ok
test_update_hotel_rating_aggregates_multiple_reviews (test.test_unit.HotelReviewRuleTest.test_update_hotel_rating_aggregates_multiple_reviews)
业务规则：多订单评分取平均并四舍五入到 1 位小数 ... ok
test_update_hotel_rating_resets_when_no_reviews (test.test_unit.HotelReviewRuleTest.test_update_hotel_rating_resets_when_no_reviews)
业务规则：无有效评价时评分重置为 0 ... ok
test_food_rating_out_of_range_raises (test.test_unit.ModelValidationRuleTest.test_food_rating_out_of_range_raises)
异常分支：评分 6.0 / -0.1 触发 ValidationError ... ok
test_food_rating_within_range_ok (test.test_unit.ModelValidationRuleTest.test_food_rating_within_range_ok) ... ok
test_order_score_fields_out_of_range_raises (test.test_unit.ModelValidationRuleTest.test_order_score_fields_out_of_range_raises)
异常分支：订单评分超界触发 ValidationError ... ok
test_order_score_fields_valid (test.test_unit.ModelValidationRuleTest.test_order_score_fields_valid) ... ok
test_save_play_review_comment_too_long_rejected (test.test_unit.PlayReviewRuleTest.test_save_play_review_comment_too_long_rejected)
异常分支：评论过长被拒绝 ... ok
test_save_play_review_invalid_scores_rejected (test.test_unit.PlayReviewRuleTest.test_save_play_review_invalid_scores_rejected)
异常分支：0/超5/非数值均被拒绝 ... ok
test_save_play_review_success (test.test_unit.PlayReviewRuleTest.test_save_play_review_success)
主流程：合法评价保存并更新评分 ... ok
test_update_play_rating_aggregates (test.test_unit.PlayReviewRuleTest.test_update_play_rating_aggregates)
业务规则：多订单平均分与人数正确 ... ok
test_get_login_user_from_session (test.test_unit.UserHelperRuleTest.test_get_login_user_from_session)
主流程：session 有 user_id 时返回对应用户 ... ok
test_get_login_user_without_session_returns_none (test.test_unit.UserHelperRuleTest.test_get_login_user_without_session_returns_none)
异常分支：未登录 / 用户不存在返回 None ... ok
test_is_merchant_none_user_returns_false (test.test_unit.UserHelperRuleTest.test_is_merchant_none_user_returns_false)
异常分支：未登录（None）应返回 False ... ok
test_is_merchant_true_only_for_merchant (test.test_unit.UserHelperRuleTest.test_is_merchant_true_only_for_merchant) ... ok
test_is_rider_true_only_for_rider (test.test_unit.UserHelperRuleTest.test_is_rider_true_only_for_rider) ... ok
test_admin_blog_and_comment_actions (test.test_integration_api.AdminApiTest.test_admin_blog_and_comment_actions)
主流程：审核博客/评论（切换逻辑删除）；异常：不存在的内容 ... C:\Users\20674\Desktop\学业\大二\大二下\软件工程\soft_ware\.venv\Lib\site-packages\django\core\handlers\base.py:58: UserWarning: No directory at: C:\Users\20674\Desktop\学业\大二\大二下\软件工程\soft_ware\staticfiles\
  mw_instance = middleware(adapted_handler)
ok
test_admin_dashboard_access_control (test.test_integration_api.AdminApiTest.test_admin_dashboard_access_control)
主流程：管理员可访问；异常：普通用户被重定向 ... ok
test_admin_logout (test.test_integration_api.AdminApiTest.test_admin_logout) ... ok
test_admin_order_actions (test.test_integration_api.AdminApiTest.test_admin_order_actions)
主流程：标记已送达/异常标记；异常：已评价订单不可改、不支持的操 ... ok
test_admin_user_actions (test.test_integration_api.AdminApiTest.test_admin_user_actions)
主流程：停用用户；异常：不能停用自己、非法角色 ... ok
test_ai_chat_empty_input_rejected (test.test_integration_api.AiApiTest.test_ai_chat_empty_input_rejected)
异常流程：空输入返回 400 ... ok
test_ai_chat_main_flow_with_catalog_context (test.test_integration_api.AiApiTest.test_ai_chat_main_flow_with_catalog_context)
主流程：返回 AI 回复，系统提示词包含平台菜品/酒店/娱乐信息 ... ok
test_ai_chat_requires_login (test.test_integration_api.AiApiTest.test_ai_chat_requires_login)
异常流程：未登录被重定向到首页 ... ok
test_ai_chat_service_failure_returns_500 (test.test_integration_api.AiApiTest.test_ai_chat_service_failure_returns_500)
异常流程：外部模型返回 None 时返回 500 友好错误 ... ok
test_login_disabled_account_rejected (test.test_integration_api.AuthApiTest.test_login_disabled_account_rejected)
异常流程：被停用账号拒绝登录 ... ok
test_login_missing_or_invalid_fields (test.test_integration_api.AuthApiTest.test_login_missing_or_invalid_fields)
异常流程：缺少字段 / 非法身份值 ... ok
test_login_success_and_role_redirects (test.test_integration_api.AuthApiTest.test_login_success_and_role_redirects)
主流程：各角色登录成功后跳转到对应首页 ... ok
test_login_wrong_password_rejected (test.test_integration_api.AuthApiTest.test_login_wrong_password_rejected)
异常流程：密码错误时拒绝登录 ... ok
test_login_wrong_role_rejected (test.test_integration_api.AuthApiTest.test_login_wrong_role_rejected)
异常流程：身份选择与账号不符时拒绝登录 ... ok
test_logout_clears_session (test.test_integration_api.AuthApiTest.test_logout_clears_session)
主流程：退出登录后 session 被清空，再访问受限页被重定向 ... ok
test_register_admin_role_forbidden (test.test_integration_api.AuthApiTest.test_register_admin_role_forbidden)
异常流程：不允许通过注册页注册管理员账号 ... ok
test_register_duplicate_username_rejected (test.test_integration_api.AuthApiTest.test_register_duplicate_username_rejected)
备选/异常流程：用户名已被占用时拒绝注册 ... ok
test_register_invalid_phone_rejected (test.test_integration_api.AuthApiTest.test_register_invalid_phone_rejected)
异常流程：手机号不是 11 位数字时拒绝 ... ok
test_register_success_flow (test.test_integration_api.AuthApiTest.test_register_success_flow)
主流程：合法注册成功并跳转登录页，数据库生成用户 ... ok
test_register_weak_password_rejected (test.test_integration_api.AuthApiTest.test_register_weak_password_rejected)
异常流程：密码不满足 8-16 位且含字母数字时拒绝 ... ok
test_blog_comment_ajax_main_and_abnormal (test.test_integration_api.BlogApiTest.test_blog_comment_ajax_main_and_abnormal) ... ok
test_blog_delete_main_and_abnormal (test.test_integration_api.BlogApiTest.test_blog_delete_main_and_abnormal) ... ok
test_blog_publish_list_detail (test.test_integration_api.BlogApiTest.test_blog_publish_list_detail) ... ok
test_merchant_space_revenue_aggregation (test.test_integration_api.CrossModuleIntegrationTest.test_merchant_space_revenue_aggregation)
主流程：商家个人中心统计聚合（销售额/订单数/评价均值） ... ok
test_order_state_changes_require_post (test.test_integration_api.CrossModuleIntegrationTest.test_order_state_changes_require_post) ... ok
test_order_status_endpoint_reflects_state (test.test_integration_api.CrossModuleIntegrationTest.test_order_status_endpoint_reflects_state)
主流程：订单状态页可访问；异常：别人不能操作/非法状态流转被拒绝 ... ok
test_order_visibility_across_roles (test.test_integration_api.CrossModuleIntegrationTest.test_order_visibility_across_roles)
主流程：一个订单从下单→接单→备餐→取餐→送达→评价，各端页面同步 ... ok
test_cart_update_delete_clear_api (test.test_integration_api.FoodApiTest.test_cart_update_delete_clear_api)
购物车 API：更新（主）、删除（主）、清空下单（主）、未登录/不存在（异常） ... ok
test_food_detail_success_and_branches (test.test_integration_api.FoodApiTest.test_food_detail_success_and_branches)
主流程：详情页正常；异常分支：缺参、不存在、已下架 ... ok
test_food_list_and_search (test.test_integration_api.FoodApiTest.test_food_list_and_search)
主流程：列表返回 200 且包含菜品；备选流程：关键词搜索命中 ... ok
test_food_order_visibility_and_review_state_are_enforced (test.test_integration_api.FoodApiTest.test_food_order_visibility_and_review_state_are_enforced) ... ok
test_food_requires_login (test.test_integration_api.FoodApiTest.test_food_requires_login)
异常流程：未登录访问美食列表被重定向 ... ok
test_foodorder_add_to_cart_creates_temp (test.test_integration_api.FoodApiTest.test_foodorder_add_to_cart_creates_temp)
备选流程：加入购物车（cutlery=2）创建 Temp 购物车记录 ... ok
test_foodorder_immediate_order_creates_order (test.test_integration_api.FoodApiTest.test_foodorder_immediate_order_creates_order)
主流程：立即下单（cutlery=1）生成 Order，金额=单价×数量 ... ok
test_foodorder_validation_branches (test.test_integration_api.FoodApiTest.test_foodorder_validation_branches)
异常流程：缺参 / 售罄 / 下架 / 不存在 ... ok
test_merchant_food_action_toggles (test.test_integration_api.FoodApiTest.test_merchant_food_action_toggles)
商家商品管理 API：下架/售罄切换（主）、权限与归属（异常） ... ok
test_groupbuy_create_and_redeem_flow (test.test_integration_api.GroupBuyApiTest.test_groupbuy_create_and_redeem_flow)
主流程：生成团购券 → 商家核销成功 ... ok
test_groupbuy_redeem_exception_branches (test.test_integration_api.GroupBuyApiTest.test_groupbuy_redeem_exception_branches)
异常流程：非商家不可核销 / 空码 / 不属于自己的券 / 重复核销 ... ok
test_groupbuy_validation_branches (test.test_integration_api.GroupBuyApiTest.test_groupbuy_validation_branches)
异常流程：空数量 / 0 / 负数 / 非数字 ... ok
test_liveness_endpoint (test.test_integration_api.HealthApiTest.test_liveness_endpoint) ... ok
test_readiness_endpoint_checks_database (test.test_integration_api.HealthApiTest.test_readiness_endpoint_checks_database) ... ok
test_version_endpoint_uses_environment (test.test_integration_api.HealthApiTest.test_version_endpoint_uses_environment) ... ok
test_hotel_booking_main_and_abnormal (test.test_integration_api.HotelApiTest.test_hotel_booking_main_and_abnormal)
主流程：预订成功金额=单价×时长；异常：缺参/非法时长/非法时间/未知房型 ... ok
test_hotel_list_search_detail (test.test_integration_api.HotelApiTest.test_hotel_list_search_detail)
主流程：列表、搜索、详情 ... ok
test_hotel_orderpos_visibility (test.test_integration_api.HotelApiTest.test_hotel_orderpos_visibility)
主流程：本人可查订单状态；异常：他人查看被拒 ... ok
test_hotel_review_and_permission (test.test_integration_api.HotelApiTest.test_hotel_review_and_permission)
主流程：评价成功更新评分；异常：无权评价他人订单 ... ok
test_play_list_search_detail (test.test_integration_api.PlayApiTest.test_play_list_search_detail) ... ok
test_play_order_main_and_abnormal (test.test_integration_api.PlayApiTest.test_play_order_main_and_abnormal) ... ok
test_play_orderpos_visibility (test.test_integration_api.PlayApiTest.test_play_orderpos_visibility) ... ok
test_play_review_and_permission (test.test_integration_api.PlayApiTest.test_play_review_and_permission) ... ok
test_uc01_abnormal_branches (test.test_e2e.AccountRegistrationE2ETest.test_uc01_abnormal_branches)
备选/异常流程：非法注册被拒、非法登录被拒、游客访问受限页被拒 ... ok
test_uc01_main_flow (test.test_e2e.AccountRegistrationE2ETest.test_uc01_main_flow)
主成功流程：注册三类角色→登录→进入匹配工作台→退出会话失效 ... ok
test_full_admin_scenario (test.test_e2e.AdminE2ETest.test_full_admin_scenario) ... ok
test_uc09_abnormal_branches (test.test_e2e.AdminE2ETest.test_uc09_abnormal_branches)
异常流程：非管理员被拒、不能停用/降级自己、已评价订单不可改、目标不存在、内容恢复 ... ok
test_full_ai_assistant_scenario (test.test_e2e.AiAssistantE2ETest.test_full_ai_assistant_scenario) ... ok
test_uc08_abnormal_branches (test.test_e2e.AiAssistantE2ETest.test_uc08_abnormal_branches)
异常流程：未登录重定向、空输入 400、服务失败 500、下架/售罄不进入上下文 ... ok
test_full_blog_scenario (test.test_e2e.BlogE2ETest.test_full_blog_scenario) ... ok
test_uc07_abnormal_branches (test.test_e2e.BlogE2ETest.test_uc07_abnormal_branches)
异常流程：内容为空拒发、评论非法/不存在/未登录、越权删除、删除后不可见 ... ok
test_full_cart_scenario (test.test_e2e.CartToOrderE2ETest.test_full_cart_scenario) ... ok
test_full_food_delivery_scenario (test.test_e2e.FoodDeliveryE2ETest.test_full_food_delivery_scenario) ... ok
test_uc02_abnormal_branches (test.test_e2e.FoodDeliveryE2ETest.test_uc02_abnormal_branches)
异常流程：不可售/信息缺失拒单、越权/错误状态推进失败、非法评分与超长评价被拒 ... ok
test_full_group_buy_scenario (test.test_e2e.GroupBuyE2ETest.test_full_group_buy_scenario) ... ok
test_uc03_abnormal_branches (test.test_e2e.GroupBuyE2ETest.test_uc03_abnormal_branches)
异常流程：非法数量、非商家核销、空码/不存在/他人券、重复核销、已取消券 ... ok
test_full_hotel_scenario (test.test_e2e.HotelE2ETest.test_full_hotel_scenario) ... ok
test_uc04_abnormal_branches (test.test_e2e.HotelE2ETest.test_uc04_abnormal_branches)
异常流程：房型/时长/时间非法拒订、非本人查看与评价被拒、非法评分与超长评价被拒 ... ok
test_uc06_abnormal_branches (test.test_e2e.MerchantSupplyE2ETest.test_uc06_abnormal_branches)
备选/异常流程：非商家、字段缺失、价格/时间非法、图片非法、越权维护全部被拒 ... ok
test_uc06_main_flow (test.test_e2e.MerchantSupplyE2ETest.test_uc06_main_flow)
主成功流程：商家发布美食/酒店/娱乐 → 列表与空间可见 → 维护菜品状态并同步用户侧 ... ok
test_full_play_scenario (test.test_e2e.PlayE2ETest.test_full_play_scenario) ... ok
test_uc05_abnormal_branches (test.test_e2e.PlayE2ETest.test_uc05_abnormal_branches)
异常流程：票数/时间非法拒购、场所不存在、非本人查看与评价被拒、非法评分被拒 ... ok
test_http_error_returns_none (test.test_unit.LlmClientTest.test_http_error_returns_none)
异常分支：HTTP 非 2xx 状态码返回 None ... ok
test_network_exception_returns_none (test.test_unit.LlmClientTest.test_network_exception_returns_none)
异常分支：网络异常（如连接失败）返回 None ... ok
test_no_api_key_returns_none_without_network (test.test_unit.LlmClientTest.test_no_api_key_returns_none_without_network)
异常分支：未配置 API Key 直接返回 None，且不发起网络请求 ... ok
test_success_returns_content_and_builds_payload (test.test_unit.LlmClientTest.test_success_returns_content_and_builds_payload)
主流程：正常响应时返回模型内容，并正确构造请求参数 ... ok
test_invalid_passwords_rejected (test.test_unit.PasswordBusinessRuleTest.test_invalid_passwords_rejected)
异常分支：无字母 / 无数字 / 长度越界均不匹配 ... ok
test_valid_passwords_match (test.test_unit.PasswordBusinessRuleTest.test_valid_passwords_match) ... ok
test_imported_mysql_database_has_required_tables (test.test_database_config.DatabaseConfigTest.test_imported_mysql_database_has_required_tables)
真实环境检查：MySQL 中存在项目核心表（无法连接时跳过） ... skipped "无法连接 MySQL（ERROR 1045 (28000): Access denied for user 'root'@'localhost' (using password: YES)）。如需检查真实库，请设置 FOOD_DELIVER_DB_PASSWORD 后重试"
test_settings_defaults_missing_password_are_allowed_in_tests (test.test_database_config.DatabaseConfigTest.test_settings_defaults_missing_password_are_allowed_in_tests)
配置可用性：若通过 test_settings 运行，SQLite 配置应可加载 ... ok
test_settings_match_sql_dump_database (test.test_database_config.DatabaseConfigTest.test_settings_match_sql_dump_database)
配置一致性：settings 数据库名应与 data_hex2.sql 声明的数据库一致 ... ok

----------------------------------------------------------------------
Ran 109 tests in 0.751s

OK (skipped=1)
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
```