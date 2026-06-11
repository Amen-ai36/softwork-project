from django.http import HttpResponse, JsonResponse
from django.conf import settings
from .models import *
from myapp.utils.llm_client import call_aliyun_llm
import json
from django.http import JsonResponse
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
import os
import uuid
import time
from django.db.models import Sum, Max, Avg, Q
from django.core.cache import cache
import hashlib
import re
from django.shortcuts import render, redirect, HttpResponse
from django.contrib.auth import logout
from django.shortcuts import redirect

# 全局信息的缓存 key
CACHE_KEY_GLOBAL_INFO = "global_platform_info"
# 缓存时间（秒），可根据数据更新频率调整，例如 1 小时
CACHE_TIMEOUT = 3600

def update_cart_item(request, tempid):
    """更新购物车中的数量或地址"""
    if request.method == 'POST':
        try:
            user_id = request.session.get('user_id')
            if not user_id:
                return JsonResponse({'status': 'error', 'msg': '未登录'}, status=401)
            user = User.objects.get(id=user_id)
            data = json.loads(request.body)
            new_num = data.get('num')
            new_address = data.get('address')
            cart_item = Temp.objects.get(id=tempid, user=user)
            if new_num is not None:
                cart_item.num = int(new_num)
                cart_item.cost = cart_item.food.price * cart_item.num
            if new_address:
                cart_item.address = new_address
            cart_item.save()
            return JsonResponse({'status': 'ok', 'num': cart_item.num, 'address': cart_item.address, 'cost': cart_item.cost})
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'msg': '仅支持POST'}, status=405)

def delete_cart_item(request, tempid):
    """删除购物车记录"""
    if request.method == 'POST':
        try:
            user_id = request.session.get('user_id')
            if not user_id:
                return JsonResponse({'status': 'error', 'msg': '未登录'}, status=401)
            user = User.objects.get(id=user_id)
            cart_item = Temp.objects.get(id=tempid, user=user)
            cart_item.delete()
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'msg': str(e)}, status=400)
    return JsonResponse({'status': 'error', 'msg': '仅支持POST'}, status=405)

@require_POST
def clear_cart(request):
    """清空购物车：将当前用户所有购物车记录迁移到 CartHistory，然后删除"""
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'status': 'error', 'msg': '未登录'}, status=401)
    
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({'status': 'error', 'msg': '用户不存在'}, status=401)

    # 获取当前用户所有购物车项
    cart_items = Temp.objects.filter(user=user, pos=0)
    if not cart_items.exists():
        return JsonResponse({'status': 'ok', 'msg': '购物车已是空的'})

    unavailable = cart_items.filter(Q(food__is_off_shelf=True) | Q(food__is_sold_out=True)).select_related('food')
    if unavailable.exists():
        names = '、'.join(item.food.name for item in unavailable)
        return JsonResponse({'status': 'error', 'msg': f'{names} 已下架或售罄，请先从购物车删除'}, status=400)

    # 批量创建历史记录
    for item in cart_items:
        Order.objects.create(
                user=user,
                food=item.food,
                num=item.num,
                address=item.address,
                cost=item.cost*item.num,
                pos=0
            )

    # 删除原购物车记录
    cart_items.delete()

    return JsonResponse({'status': 'ok', 'msg': '购物车已清空'})

def get_global_info():
    """从缓存获取全局菜品/酒店/娱乐信息，若失效则重新生成"""
    global_info = cache.get(CACHE_KEY_GLOBAL_INFO)
    if global_info is None:
        # 生成全局信息字符串（这部分只在缓存过期时执行一次）
        foods = Food.objects.filter(is_off_shelf=False, is_sold_out=False)
        foods_info = "【以下是当前平台菜品清单】\n"
        for idx, food in enumerate(foods, 1):
            foods_info += f"{idx}. {food.name} | 价格: ¥{food.price} | 简介: {food.inf}\n"
            foods_info += f"| 评分: {food.rating if food.ratenum > 0 else '暂无'} | 售出: {food.sale}份 | 下单人数: {food.saleperson}人\n"
        
        hotels = Hotel.objects.all()
        hotels_info = "【以下是当前平台酒店清单】\n"
        for idx, hotel in enumerate(hotels, 1):
            hotels_info += f"{idx}. {hotel.name} | 价格: 单人间钟点房¥{hotel.price_clock}，日租¥{hotel.price_day}，双人间稍贵 | 简介: {hotel.inf}\n"
            hotels_info += f"地址: {hotel.addr} | 评分: {hotel.rating if hotel.ratenum > 0 else '暂无'} | 订单数: {hotel.orders}单\n"
        
        plays = Play.objects.all()
        plays_info = "【以下是当前平台娱乐清单】\n"
        for idx, play in enumerate(plays, 1):
            plays_info += f"{idx}. {play.name} | 价格: ¥{play.price} | 简介: {play.inf}\n"
            plays_info += f"地址: {play.addr} | 评分: {play.rating if play.ratenum > 0 else '暂无'} | 订单数: {play.orders}单\n"
        
        global_info = {
            "foods_info": foods_info,
            "hotels_info": hotels_info,
            "plays_info": plays_info,
        }
        cache.set(CACHE_KEY_GLOBAL_INFO, global_info, CACHE_TIMEOUT)
    return global_info

@ensure_csrf_cookie
def ai_chat_view(request):
    if request.method == "POST":
        user_id = request.session.get('user_id')
        if not user_id:
            return redirect('/index/')
        
        user = User.objects.filter(id=user_id).first()
        user_input = request.POST.get("user_input", "").strip()
        if not user_input:
            return JsonResponse({"error": "输入不能为空"}, status=400)
        
        # 构建用户动态信息（无法缓存，因为每个用户不同）
        user_info = f"【以下是当前用户状态】\n用户ID: {user.id}, 简介: {user.word}\n该用户订单记录如下：\n"
        orders = Order.objects.filter(user=user)
        for idx, order in enumerate(orders, 1):
            user_info += f"{idx}. {order.food.name} | 该用户评分: {order.scoretofood} | 该用户评价: {order.comment}\n"
        
        # 从缓存获取全局信息
        global_info = get_global_info()
        
        # 构建系统提示（使用缓存的全局信息）
        system_prompt = f"""你是这个平台的助手，擅长回答关于美食、娱乐和住宿规划的问题。
        {user_info}; {global_info['foods_info']}; {global_info['hotels_info']}; {global_info['plays_info']}
        你可以根据用户的提问和用户的背景信息，从菜品清单、酒店清单和娱乐清单中推荐相关商品服务，或者解答用户的疑问。
        如果用户的订单记录为空，请以“欢迎新用户！”开头回答，简要介绍该平台的服务，再回答用户的提问
        请尽量提供详细且有用的回答，帮助用户更好地了解和选择商品。"""
        
        reply = call_aliyun_llm(user_input, system_prompt=system_prompt)
        if reply is None:
            return JsonResponse({"error": "AI 服务暂时不可用，请稍后重试"}, status=500)
        return JsonResponse({"reply": reply})
    
    return render(request, "ai_chat.html")


def get_login_user(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return None
    return User.objects.filter(id=user_id).first()


def is_merchant(user):
    return user is not None and user.usertype == 2

def is_rider(user):
    return user is not None and user.usertype == 1

def make_group_buy_code():
    while True:
        code = uuid.uuid4().hex[:10].upper()
        if not GroupBuyCoupon.objects.filter(code=code).exists():
            return code

def index(request):
    return render(request, 'index.html')

def login(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        usertype = request.POST.get('usertype')
        if not u or not p:
            return HttpResponse("请填写用户名和密码！")
        if usertype not in ('0', '1', '2', '3'):
            return HttpResponse("请选择身份！")
        
        # 后端密码校验：8-16位字符，必须包含字母和数字
        import re
        if not re.match(r'^(?=.*[a-zA-Z])(?=.*\d).{8,16}$', p):
            return HttpResponse("密码不符合要求：必须在8-16位之间，且必须同时包含英文字母和数字！")
        
        usertype = int(usertype)
        user = User.objects.filter(username=u).first()
        if not user:
            return render(request, 'register.html', {'error': '用户未注册'})
        else:
            # 老用户，检索密码和身份
            if user.password != p:
                return HttpResponse('<script>alert("用户名或者密码错误");history.back();</script>')
            if user.usertype != usertype:
                return HttpResponse('<script>alert("用户的身份选择错误");history.back();</script>')
            if user.isDelete:
                return HttpResponse('<script>alert("该账号已被停用，请联系管理员");history.back();</script>')
            request.session['user_id'] = user.id
            if usertype == 3:
                return redirect('/manage/')
            if usertype == 1:
                return redirect('/rider/')
            return redirect('/food/')
    return render(request, 'login.html')

def logout_view(request):
    logout(request)          # Django 内置的注销函数，会删除 session 中的用户信息
    response = redirect('/index/')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    response['Clear-Site-Data'] = '"cache"'
    
    return response

def register(request):
    """
    用户注册视图
    GET: 显示注册页面
    POST: 处理注册请求，成功后自动登录并跳转
    """
    if request.method == 'POST':
        # 获取表单数据
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        usertype = request.POST.get('usertype', '')
        phone = request.POST.get('phone', '').strip()

        # 1. 校验必填字段
        if not username or not password or not usertype:
            return render(request, 'register.html', {'error': '用户名、密码和用户类型不能为空'})

        # 2. 校验用户类型（不允许注册管理员）
        try:
            usertype = int(usertype)
        except ValueError:
            return render(request, 'register.html', {'error': '无效的用户类型'})
        if usertype not in (0, 1, 2):
            return render(request, 'register.html', {'error': '用户类型只能为普通用户、骑手或商家'})

        # 3. 校验用户名是否已被使用（排除已逻辑删除的用户）
        if User.objects.filter(username=username, isDelete=False).exists():
            return render(request, 'register.html', {'error': '用户名已被注册，请换一个'})

        # 4. 密码强度校验：8-16位，必须包含字母和数字
        if not re.match(r'^(?=.*[a-zA-Z])(?=.*\d).{8,16}$', password):
            return render(request, 'register.html', 
                          {'error': '密码必须在8-16位之间，且同时包含英文字母和数字'})

        # 5. 手机号校验（可选，但如果填写则必须为11位数字）
        if phone and not re.match(r'^\d{11}$', phone):
            return render(request, 'register.html', {'error': '手机号必须是11位数字'})
        
        if usertype == 3:
                return HttpResponse("管理员账号不能通过登录页注册，请使用管理命令创建！")

        # 6. 创建用户（密码明文存储，与现有系统保持一致）
        user = User.objects.create(
            username=username,
            password=password,
            phone=phone,
            usertype=usertype,
            isDelete=False
        )

        return redirect('/account/login/')

    # GET 请求：显示注册页面
    return render(request, 'register.html')

@ensure_csrf_cookie
def food(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('/index/')
    
    user = User.objects.filter(id=user_id).first()
    keyword = request.GET.get('q', '').strip()
    foods = Food.objects.filter(is_off_shelf=False)

    if keyword:
        foods = foods.filter(
            Q(name__icontains=keyword) | Q(providor__icontains=keyword) | Q(inf__icontains=keyword)
        )
    foods_json = list(foods.values('id', 'name', 'price', 'providor', 'sale', 'rating', 'ratenum', 'is_sold_out'))
    return render(request, 'food/food.html', {
        'foods': foods,
        'foods_json': foods_json,
        'user_id': user_id,
        'is_merchant': is_merchant(user),
        'keyword': keyword,
    })

def foodsend(request):
    user = get_login_user(request)
    if not user:
        return redirect('/index/')
    if not is_merchant(user):
        return HttpResponse("只有商家可以添加美食！")

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        price = request.POST.get('price', '').strip()
        providor = request.POST.get('providor', '').strip()
        inf = request.POST.get('inf', '').strip()

        if not name or not price or not providor:
            return HttpResponse("请填写完整的美食信息！")
        
        uploaded_file = request.FILES.get('image')
        
        # 校验文件是否存在
        if not uploaded_file:
            return render(request, 'food/foodsend.html', {'error': '请上传图片'})
        
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
        if uploaded_file.content_type not in allowed_types:
            return render(request, 'food/foodsend.html', {'error': '只支持 JPG 或 PNG 格式图片'})
        
        if uploaded_file.size > 2 * 1024 * 1024:  # 2MB 限制
            return render(request, 'food/foodsend.html', {'error': '图片大小不能超过 2MB'})
        
        ext = os.path.splitext(uploaded_file.name)[1]  # 如 .jpg
        new_filename = f"{uuid.uuid4().hex}_{int(time.time())}{ext}"
        
        # 目标子目录（相对于 MEDIA_ROOT）
        sub_dir = 'images/food/'
        SAVE_DIR = os.path.join(settings.BASE_DIR, 'static', 'images', 'food')
        os.makedirs(SAVE_DIR, exist_ok=True)   # 加上这一行
        save_path = os.path.join(SAVE_DIR, new_filename)
        with open(save_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        # 数据库存储的相对路径（用于模板中生成 URL）
        relative_path = f"{sub_dir}{new_filename}"

        try:
            price = float(price)
        except ValueError:
            return HttpResponse("价格必须是数字！")

        Food.objects.create(
            name=name,
            price=price,
            image=relative_path,
            providor=providor,
            inf=inf,
            merchant=user,
        )
        return redirect('/food/')

    return render(request, 'food/foodsend.html', {'user_id': user.id})

@require_POST
def merchant_food_action(request):
    user = get_login_user(request)
    if not user:
        return redirect('/index/')
    if not is_merchant(user):
        return HttpResponse("只有商家可以管理商品状态！")

    food = Food.objects.filter(id=request.POST.get('food_id'), merchant=user).first()
    if not food:
        return HttpResponse("商品不存在或不属于当前商家！")

    action = request.POST.get('action')
    if action == 'toggle_off_shelf':
        food.is_off_shelf = not food.is_off_shelf
        food.save(update_fields=['is_off_shelf'])
    elif action == 'toggle_sold_out':
        food.is_sold_out = not food.is_sold_out
        food.save(update_fields=['is_sold_out'])
    else:
        return HttpResponse("不支持的商品操作！")
    return redirect('/space/')

def space(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('/index/')

    user = User.objects.get(id=user_id)

    if request.method == 'POST':
        phone = request.POST.get('phone', '')
        word = request.POST.get('word', '')
        user.phone = phone
        user.word = word
        user.save()
        return redirect('/space/')

    context = {
        'user': user,
        'is_merchant': is_merchant(user),
        'is_rider': is_rider(user),
    }

    if is_rider(user):
        # 骑手：已接订单(pos=1,2,4) 和 已完成订单(pos=5)
        context['rider_active_orders'] = Order.objects.filter(
            rider=user, pos__in=[1, 2, 3, 4]
        ).select_related('food', 'user').order_by('-time')
        context['rider_done_orders'] = Order.objects.filter(
            rider=user, pos=5
        ).select_related('food', 'user').order_by('-time')
        return render(request, 'space.html', context)

    if is_merchant(user):
        merchant_foods = []
        for food in Food.objects.filter(merchant=user):
            orders = Order.objects.filter(food=food)
            agg = orders.aggregate(
                total_num=Sum('num'),
                total_cost=Sum('cost'),
                latest_time=Max('time'),
                avg_score=Avg('scoretofood', filter=Q(scoretofood__gt=0)),
            )
            latest_order = orders.order_by('-time').first()
            merchant_foods.append({
                'food': food,
                'total_num': agg['total_num'] or 0,
                'total_cost': agg['total_cost'] or 0,
                'address': latest_order.address if latest_order else food.providor,
                'latest_time': agg['latest_time'],
                'avg_score': agg['avg_score'],
            })
        context['merchant_foods'] = merchant_foods
        context['merchant_hotels'] = Hotel.objects.filter(merchant=user)
        context['merchant_plays'] = Play.objects.filter(merchant=user)
        # 商家：当前订单(pos=1，骑手已接单待出餐) 和 已完成订单(pos=2,4,5)
        context['merchant_current_orders'] = Order.objects.filter(
            food__merchant=user, pos__in=[0, 1]
        ).select_related('food', 'user', 'rider').order_by('-time')
        context['merchant_done_orders'] = Order.objects.filter(
            food__merchant=user, pos__in=[2, 4, 5]
        ).select_related('food', 'user', 'rider').order_by('-time')
        context['merchant_group_coupons'] = GroupBuyCoupon.objects.filter(
            food__merchant=user
        ).select_related('food', 'user').order_by('-time')
        food_revenue = Order.objects.filter(food__merchant=user).aggregate(total=Sum('cost'))['total'] or 0
        hotel_revenue = HotelOrder.objects.filter(hotel__merchant=user).aggregate(total=Sum('cost'))['total'] or 0
        play_revenue = PlayOrder.objects.filter(play__merchant=user).aggregate(total=Sum('cost'))['total'] or 0
        groupbuy_revenue = GroupBuyCoupon.objects.filter(
            food__merchant=user, status=1
        ).aggregate(total=Sum('cost'))['total'] or 0
        context['merchant_revenue'] = {
            'food': food_revenue,
            'hotel': hotel_revenue,
            'play': play_revenue,
            'groupbuy': groupbuy_revenue,
            'total': food_revenue + hotel_revenue + play_revenue + groupbuy_revenue,
            'food_orders': Order.objects.filter(food__merchant=user).count(),
            'hotel_orders': HotelOrder.objects.filter(hotel__merchant=user).count(),
            'play_orders': PlayOrder.objects.filter(play__merchant=user).count(),
            'used_group_coupons': GroupBuyCoupon.objects.filter(food__merchant=user, status=1).count(),
        }
    else:
        context['orders'] = Order.objects.filter(user=user)
        context['hotel_orders'] = HotelOrder.objects.filter(user=user)
        context['play_orders'] = PlayOrder.objects.filter(user=user)
        context['group_coupons'] = GroupBuyCoupon.objects.filter(
            user=user
        ).select_related('food').order_by('-time')
        context['blogs'] = Blog.objects.filter(authorid=user, isdeleted=False)
        context['temps'] = Temp.objects.filter(user=user, pos=0)

    return render(request, 'space.html', context)

def fooddetails(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('/index/')
        
    food_id = request.GET.get('foodid')
    
    if not food_id:
        return HttpResponse("参数错误！")
        
    food = Food.objects.filter(id=food_id).first()
    if not food:
        return HttpResponse("食物不存在！")
    if food.is_off_shelf:
        return HttpResponse("该商品已下架！")
        
    # 查询当前用户在此食物上的订单记录
    orders = Order.objects.filter(user_id=user_id, food_id=food_id)
    order_times = orders.count()
    total_copies = orders.aggregate(Sum('num'))['num__sum'] or 0
    records = Order.objects.filter(food_id=food_id)

    context = {
        'food': food,
        'user_id': user_id,
        'order_times': order_times,
        'total_copies': total_copies,
        'records': records
    }
    
    return render(request, 'food/fooddetails.html', context)

def foodorder(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('/index/')
        
    food_id = request.GET.get('foodid')
    
    if not food_id:
        return HttpResponse("参数错误！")
        
    food = Food.objects.filter(id=food_id).first()
    if not food:
        return HttpResponse("食物不存在！")
    if food.is_off_shelf:
        return HttpResponse("该商品已下架！")
    if food.is_sold_out:
        return HttpResponse("该商品已售罄！")

    if request.method == 'POST':
        num = request.POST.get('num')
        address = request.POST.get('address')
        cutlery = request.POST.get('cutlery')  # 是否需要餐具，前端传递 "on" 或 None
        
        if not num or not address:
            return HttpResponse("请填写完整的下单信息！")
            
        if cutlery == "1":
            Order.objects.create(
                user_id=user_id,
                food_id=food_id,
                num=num,
                address=address,
                cost=food.price * int(num),
                pos=0
            )

        else:
            Temp.objects.create(
                user_id=user_id,
                food_id=food_id,
                num=num,
                address=address,
                cost=food.price, # 这里是单价所以不要乘以数量!!!!
                pos=0
            )

        return redirect(f'/fooddetails/?userid={user_id}&foodid={food_id}')
        
    return render(request, 'food/foodorder.html', {'food': food, 'user_id': user_id})

def groupbuyorder(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('/index/')

    food_id = request.GET.get('foodid')
    if not food_id:
        return HttpResponse("参数错误！")

    food = Food.objects.filter(id=food_id).first()
    if not food:
        return HttpResponse("食物不存在！")
    if food.is_off_shelf:
        return HttpResponse("该商品已下架！")
    if food.is_sold_out:
        return HttpResponse("该商品已售罄！")

    if request.method == 'POST':
        num = request.POST.get('num')
        if not num:
            return HttpResponse("请填写团购数量！")
        try:
            num = int(num)
            if num <= 0:
                return HttpResponse("团购数量必须大于0！")
        except (TypeError, ValueError):
            return HttpResponse("团购数量必须是正整数！")

        coupon = GroupBuyCoupon.objects.create(
            user_id=user_id,
            food=food,
            num=num,
            cost=round(food.price * num, 2),
            code=make_group_buy_code(),
            status=0,
        )
        food.saleperson += 1
        food.sale += num
        food.save(update_fields=['saleperson', 'sale'])
        return render(request, 'food/groupbuy_success.html', {'coupon': coupon, 'user_id': user_id})

    return render(request, 'food/groupbuy_order.html', {'food': food, 'user_id': user_id})

def groupbuy_redeem(request):
    user = get_login_user(request)
    if not user:
        return redirect('/index/')
    if not is_merchant(user):
        return HttpResponse("只有商家可以核销团购券！")
    if request.method != 'POST':
        return redirect('/space/')

    code = request.POST.get('code', '').strip().upper()
    if not code:
        return HttpResponse("请输入核销码！")

    coupon = GroupBuyCoupon.objects.filter(code=code, food__merchant=user).select_related('food', 'user').first()
    if not coupon:
        return HttpResponse('<script>alert("核销码不存在或不属于您的商品");history.back();</script>')
    if coupon.status == 1:
        return HttpResponse('<script>alert("该团购券已核销");history.back();</script>')
    if coupon.status == 2:
        return HttpResponse('<script>alert("该团购券已取消");history.back();</script>')

    coupon.status = 1
    coupon.used_at = timezone.now()
    coupon.save(update_fields=['status', 'used_at'])
    return redirect('/space/')

def orderpos(request):
    if not request.session.get('user_id'):
        return redirect('/index/')
        
    order_id = request.GET.get('orderid') 
    if not order_id:
        return HttpResponse("参数错误！")
        
    order = Order.objects.filter(id=order_id).first()
    if not order:
        return HttpResponse("订单不存在！")
    
    return render(request, 'foodorder/orderpos.html', {'orders': order})

def ordercomment(request):
    if not request.session.get('user_id'):
        return redirect('/index/')
        
    order_id = request.GET.get('orderid')
    if not order_id:
        return HttpResponse("参数错误！")
        
    order = Order.objects.filter(id=order_id).first()
    if not order:
        return HttpResponse("订单不存在！")
        
    if request.method == 'POST':
        scoretofood = request.POST.get('scoretofood')
        scoretodeliver = request.POST.get('scoretodeliver')
        comment = request.POST.get('comment', '')
        
        # 基本校验
        try:
            sf = float(scoretofood)
            sd = float(scoretodeliver)
            if not (0.0 < sf <= 5.0) or not (0.0 < sd <= 5.0):
                return HttpResponse("评分必须大于0.0且小于等于5.0的数值！")
        except (TypeError, ValueError):
            return HttpResponse("评分必须是数值！")
            
        if len(comment) > 200:
            return HttpResponse("评论长度不能超过200个字符！")
            
        # 记录评分信息，并且修改 pos 为 5
        order.scoretofood = round(sf, 1)
        order.scoretodeliver = round(sd, 1)
        order.comment = comment
        order.pos = 5
        order.save()

        return redirect('/space/')
        
    return render(request, 'foodorder/ordercomment.html', {'orders': order})

@ensure_csrf_cookie
def blog(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('/index/')
    
    keyword = request.GET.get('q', '').strip()
    blogs = Blog.objects.filter(isdeleted=False)
    if keyword:
        blogs = blogs.filter(
            Q(title__icontains=keyword)
            | Q(content__icontains=keyword)
        )
    return render(request, 'blog/blogs.html', {
        'blogs': blogs,
        'user_id': user_id,
        'keyword': keyword,
    })

def blogsend(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('/index/')
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        content = request.POST.get('content', '').strip()
        if not title or not content:
            return HttpResponse("标题和内容不能为空！")
        
        Blog.objects.create(
            title=title,
            content=content,
            authorid_id=user_id
        )
        return redirect('/blog/')
    
    return render(request, 'blog/blogsend.html')

def blogsdetails(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('/index/')
        
    blog_id = request.GET.get('blogid')
    if not blog_id:
        return HttpResponse("参数错误！")
        
    blog = Blog.objects.filter(id=blog_id, isdeleted=False).first()
    if not blog:
        return HttpResponse("博客不存在！")
    
    # blog.authorid 已经是 User 对象（如果外键字段名为 authorid）
    author = blog.authorid
    author_name = author.username if author else "未知作者"
    comments = Comment.objects.filter(blogid=blog, isdeleted=False).order_by('-created_at')
    for comment in comments:
        user = User.objects.filter(id=comment.userid).first()
        comment.username = user.username if user else '匿名用户'

    print(f"blog.authorid.id: {blog.authorid.id}")
    print(f"user_id: {user_id}")
    print(type(blog.authorid.id))
    print(type(user_id))
    
    return render(request, 'blog/blogsdetails.html', {'blog': blog, 'user_id': user_id, 'author_name': author_name, 'comments': comments})

@require_http_methods(["POST"])
@ensure_csrf_cookie
def blogcomment(request):
    """
    处理博客评论的 AJAX 请求
    请求体 JSON: {"blog_id": int, "content": str}
    返回 JSON: {"status": "ok"} 或 {"error": "错误信息"}
    """
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'error': '未登录，请先登录'}, status=401)
        
    try:
        # 解析 JSON 数据
        data = json.loads(request.body)
        blog_id = data.get('blog_id')
        content = data.get('content', '').strip()
    except json.JSONDecodeError:
        return JsonResponse({'error': '无效的请求数据'}, status=400)

    # 基本验证
    if not blog_id:
        return JsonResponse({'error': '缺少博客ID'}, status=400)
    if not content:
        return JsonResponse({'error': '评论内容不能为空'}, status=400)
    if len(content) > 500:
        return JsonResponse({'error': '评论内容不能超过500字'}, status=400)

    # 获取博客对象
    try:
        blog = Blog.objects.get(id=blog_id)
    except Blog.DoesNotExist:
        return JsonResponse({'error': '博客不存在'}, status=404)

    # 创建评论（假设 BlogComment 模型有 blog, user, content, created_at 字段）
    comment = Comment.objects.create(
        blogid=blog,
        userid=user_id,
        content=content
    )

    # 返回成功响应
    return JsonResponse({
        'status': 'ok',
        'message': '评论发布成功',
        'comment_id': comment.id,
        # 可选：返回评论的部分信息供前端动态追加
        'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S')
    })

@csrf_exempt
def delete_blog(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'error': '未登录，请先登录'}, status=401)
        
    if request.method == 'DELETE':
        try:
            uid = user_id
            user = User.objects.filter(id=uid).first()
            blog_id_str = request.GET.get('blogid')
            blog_id = int(blog_id_str) if blog_id_str and blog_id_str.isdigit() else None
            blog = Blog.objects.get(id=blog_id, authorid=user)
            blog.isdeleted = True
            blog.save()
            return JsonResponse({'success': True})
        except Blog.DoesNotExist:
            return JsonResponse({'error': '博客不存在或无删除权限'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': '请求方式错误'}, status=405)

@csrf_exempt
def delete_comment(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return JsonResponse({'error': '未登录，请先登录'}, status=401)
        
    if request.method == 'DELETE':
        try:
            uid = user_id
            comment_id_str = request.GET.get('commentid')
            comment_id = int(comment_id_str) if comment_id_str and comment_id_str.isdigit() else None
            comment = Comment.objects.get(id=comment_id, userid=uid)
            comment.isdeleted = True
            comment.save()
            return JsonResponse({'success': True})
        except Comment.DoesNotExist:
            return JsonResponse({'error': '评论不存在或无删除权限'}, status=404)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': '请求方式错误'}, status=405)