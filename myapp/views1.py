from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils.dateparse import parse_datetime
from django.db.models import Avg, Count, Q
from django.conf import settings
from .models import *
from .views import is_merchant, is_rider, get_login_user
import os
import uuid
import time
from django.conf import settings  

ROOM_PRICE_FIELDS = {
    'single_clock': 'price_clock',
    'single_day': 'price_day',
    'double_clock': 'price_double_clock',
    'double_day': 'price_double_day',
    'special_day': 'price_special',
}

ROOM_TYPE_LABELS = {
    'single_clock': '单人间钟点房',
    'single_day': '单人间日租',
    'double_clock': '双人间钟点房',
    'double_day': '双人间日租',
    'special_day': '特色房日租',
}


def get_hotel_room_price(hotel, room_type):
    field = ROOM_PRICE_FIELDS.get(room_type)
    if not field:
        return None
    return getattr(hotel, field, None)


def update_hotel_rating(hotel):
    stats = HotelOrder.objects.filter(hotel=hotel, pos=5, score__gt=0).aggregate(
        avg_score=Avg('score'),
        count=Count('id'),
    )
    count = stats['count'] or 0
    if count == 0:
        hotel.rating = 0.0
        hotel.ratenum = 0
    else:
        hotel.rating = round(float(stats['avg_score']), 1)
        hotel.ratenum = count
    hotel.save()


def save_hotel_review(order, score, comment):
    try:
        s = float(score)
        if not (0.0 < s <= 5.0):
            return "评分必须大于0.0且小于等于5.0的数值！"
    except (TypeError, ValueError):
        return "评分必须是数值！"

    if len(comment) > 200:
        return "评论长度不能超过200个字符！"

    order.score = round(s, 1)
    order.comment = comment
    order.pos = 5
    order.save()
    update_hotel_rating(order.hotel)
    return None


def hotel(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('/index/')

    user = User.objects.filter(id=user_id).first()
    keyword = request.GET.get('q', '').strip()
    hotels = Hotel.objects.all()
    if keyword:
        hotels = hotels.filter(
            Q(name__icontains=keyword)
        )

    hotels_json = list(hotels.values('id', 'name', 'addr', 'price_clock', 'price_day', 'rating', 'ratenum'))

    return render(request, 'hotel/hotel.html', {
        'hotels': hotels,
        'hotels_json': hotels_json,
        'user_id': user_id,
        'is_merchant': is_merchant(user),
        'keyword': keyword,
    })

def hotelsend(request):
    user = get_login_user(request)
    if not user:
        return redirect('/index/')
    if not is_merchant(user):
        return HttpResponse("只有商家可以添加酒店！")

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        addr = request.POST.get('addr', '').strip()
        inf = request.POST.get('inf', '').strip()
        price_clock = request.POST.get('price_clock', '').strip()
        price_day = request.POST.get('price_day', '').strip()
        price_double_clock = request.POST.get('price_double_clock', '').strip()
        price_double_day = request.POST.get('price_double_day', '').strip()
        price_special = request.POST.get('price_special', '').strip()

        if not name or not addr:
            return HttpResponse("请填写酒店名称、地址和图片路径！")
        
        uploaded_file = request.FILES.get('image')
        
        # 校验文件是否存在
        if not uploaded_file:
            return render(request, 'hotel/hotelsend.html', {'error': '请上传图片'})
        
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
        if uploaded_file.content_type not in allowed_types:
            return render(request, 'hotel/hotelsend.html', {'error': '只支持 JPG 或 PNG 格式图片'})
        
        if uploaded_file.size > 2 * 1024 * 1024:  # 2MB 限制
            return render(request, 'hotel/hotelsend.html', {'error': '图片大小不能超过 2MB'})
        
        ext = os.path.splitext(uploaded_file.name)[1]  # 如 .jpg
        new_filename = f"{uuid.uuid4().hex}_{int(time.time())}{ext}"
        
        # 目标子目录（相对于 MEDIA_ROOT）
        sub_dir = 'images/hotel/'
        SAVE_DIR = os.path.join(settings.BASE_DIR, 'static', 'images', 'hotel')
        os.makedirs(SAVE_DIR, exist_ok=True)   # 加上这一行
        save_path = os.path.join(SAVE_DIR, new_filename)
        with open(save_path, 'wb+') as destination:
            for chunk in uploaded_file.chunks():
                destination.write(chunk)
        
        # 数据库存储的相对路径（用于模板中生成 URL）
        relative_path = f"{sub_dir}{new_filename}"

        def parse_price(value):
            if not value:
                return None
            try:
                return float(value)
            except ValueError:
                return None

        Hotel.objects.create(
            name=name,
            addr=addr,
            image=relative_path,
            inf=inf,
            price_clock=parse_price(price_clock),
            price_day=parse_price(price_day),
            price_double_clock=parse_price(price_double_clock),
            price_double_day=parse_price(price_double_day),
            price_special=parse_price(price_special),
            merchant=user,
        )
        return redirect('/hotel/')

    return render(request, 'hotel/hotelsend.html', {'user_id': user.id})

def hoteldetails(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('/index/')
    
    hotel_id = request.GET.get('hotelid')
    if not hotel_id:
        return HttpResponse("酒店不存在！")
    
    hotel = Hotel.objects.filter(id=hotel_id).first()
    if not hotel:
        return HttpResponse("酒店不存在！")

    records = HotelOrder.objects.filter(hotel_id=hotel_id, pos=5).select_related('user').order_by('-time')
    return render(request, 'hotel/hoteldetails.html', {
        'hotel': hotel,
        'user_id': user_id,
        'records': records,
    })

def hotelorder(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('/index/')

    hotel_id = request.GET.get('hotelid')
    if not hotel_id:
        return HttpResponse("参数错误！")

    hotel = Hotel.objects.filter(id=hotel_id).first()
    if not hotel:
        return HttpResponse("酒店不存在！")

    if request.method == 'POST':
        checkin_time = request.POST.get('checkin_time')
        duration = request.POST.get('duration')
        room_type = request.POST.get('room_type')

        if not checkin_time or not duration or not room_type:
            return HttpResponse("请填写完整的订房信息！")

        price = get_hotel_room_price(hotel, room_type)
        if price is None:
            return HttpResponse("所选房型不存在！")

        try:
            duration = int(duration)
            if duration <= 0:
                return HttpResponse("入住时间长度必须大于0！")
        except (TypeError, ValueError):
            return HttpResponse("入住时间长度必须是正整数！")

        checkin_dt = parse_datetime(checkin_time)
        if not checkin_dt:
            return HttpResponse("入住时间格式不正确！")

        cost = price * duration
        HotelOrder.objects.create(
            user_id=user_id,
            hotel_id=hotel_id,
            room_type=room_type,
            duration=duration,
            checkin_time=checkin_dt,
            cost=cost,
            pos=4,
        )
        hotel.orders += 1
        hotel.save()

        return redirect(f'/hoteldetails/?hotelid={hotel_id}')

    return render(request, 'hotel/hotelorder.html', {'hotel': hotel, 'user_id': user_id})

def hotelcomment(request):
    if not request.session.get('user_id'):
        return redirect('/index/')

    order_id = request.GET.get('orderid')
    if not order_id:
        return HttpResponse("参数错误！")

    order = HotelOrder.objects.filter(id=order_id).first()
    if not order:
        return HttpResponse("订单不存在！")

    if order.user_id != request.session.get('user_id'):
        return HttpResponse("无权评价该订单！")

    if request.method == 'POST':
        score = request.POST.get('score')
        comment = request.POST.get('comment', '')

        error = save_hotel_review(order, score, comment)
        if error:
            return HttpResponse(error)

        return redirect('/space/')

    return render(request, 'hotelorder/hotelcomment.html', {'order': order})

def hotelorderpos(request):
    if not request.session.get('user_id'):
        return redirect('/index/')

    order_id = request.GET.get('orderid')
    if not order_id:
        return HttpResponse("参数错误！")

    order = HotelOrder.objects.filter(id=order_id).select_related('hotel').first()
    if not order:
        return HttpResponse("订单不存在！")

    if order.user_id != request.session.get('user_id'):
        return HttpResponse("无权查看该订单！")

    if request.method == 'POST':
        score = request.POST.get('score')
        comment = request.POST.get('comment', '')

        error = save_hotel_review(order, score, comment)
        if error:
            return HttpResponse(error)

        return redirect('/space/')

    room_type_label = ROOM_TYPE_LABELS.get(order.room_type, order.room_type)
    review_status = '已评价' if order.pos == 5 else '待评价'

    return render(request, 'hotelorder/hotelorderpos.html', {
        'order': order,
        'room_type_label': room_type_label,
        'review_status': review_status,
    })


# ==================== 娱乐活动模块 ====================

def update_play_rating(play):
    """重新计算并更新娱乐场所的评分和评分人数"""
    stats = PlayOrder.objects.filter(play=play, pos=5, score__gt=0).aggregate(
        avg_score=Avg('score'),
        count=Count('id'),
    )
    count = stats['count'] or 0
    if count == 0:
        play.rating = 0.0
        play.ratenum = 0
    else:
        play.rating = round(float(stats['avg_score']), 1)
        play.ratenum = count
    play.save()


def save_play_review(order, score, comment):
    """校验并保存娱乐订单评价，返回错误信息或 None"""
    try:
        s = float(score)
        if not (0.0 < s <= 5.0):
            return "评分必须大于0.0且小于等于5.0的数值！"
    except (TypeError, ValueError):
        return "评分必须是数值！"

    if len(comment) > 200:
        return "评论长度不能超过200个字符！"

    order.score = round(s, 1)
    order.comment = comment
    order.pos = 5
    order.save()
    update_play_rating(order.play)
    return None


def play(request):
    """娱乐场所列表页"""
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('/index/')

    user = User.objects.filter(id=user_id).first()
    keyword = request.GET.get('q', '').strip()
    plays = Play.objects.all()
    if keyword:
        plays = plays.filter(
            Q(name__icontains=keyword)
        )

    plays_json = list(plays.values('id', 'name', 'addr', 'price', 'start_time', 'open_time', 'rating', 'ratenum'))
    return render(request, 'play/play.html', {
        'plays': plays,
        'plays_json': plays_json,
        'user_id': user_id,
        'is_merchant': is_merchant(user),
        'keyword': keyword,
    })


def playsend(request):
    """商家添加娱乐场所"""
    user = get_login_user(request)
    if not user:
        return redirect('/index/')
    if not is_merchant(user):
        return HttpResponse("只有商家可以添加娱乐场所！")

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        addr = request.POST.get('addr', '').strip()
        price = request.POST.get('price', '').strip()
        start_time = request.POST.get('start_time', '').strip() or '09:00'
        open_time = request.POST.get('open_time', '').strip() or '24h'
        inf = request.POST.get('inf', '').strip()

        if not name or not addr or not price:
            return HttpResponse("请填写完整的娱乐场所信息！")
        
        uploaded_file = request.FILES.get('image')
        
        # 校验文件是否存在
        if not uploaded_file:
            return render(request, 'play/playsend.html', {'error': '请上传图片'})
        
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
        if uploaded_file.content_type not in allowed_types:
            return render(request, 'play/playsend.html', {'error': '只支持 JPG 或 PNG 格式图片'})
        
        if uploaded_file.size > 2 * 1024 * 1024:  # 2MB 限制
            return render(request, 'play/playsend.html', {'error': '图片大小不能超过 2MB'})
        
        ext = os.path.splitext(uploaded_file.name)[1]  # 如 .jpg
        new_filename = f"{uuid.uuid4().hex}_{int(time.time())}{ext}"
        
        # 目标子目录（相对于 MEDIA_ROOT）
        sub_dir = 'images/play/'
        SAVE_DIR = os.path.join(settings.BASE_DIR, 'static', 'images', 'play')
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
            return HttpResponse("门票价格必须是数字！")

        import re
        m = re.match(r'^(\d{2}):(\d{2})$', start_time)
        if not m:
            return HttpResponse('<script>alert("开始营业时间格式不正确！请使用 HH:MM 格式，例如：09:00、14:30");history.back();</script>')
        hh, mm = int(m.group(1)), int(m.group(2))
        if hh >= 24 or mm >= 60:
            return HttpResponse('<script>alert("开始营业时间不合法！小时必须小于24，分钟必须小于60");history.back();</script>')
        if not re.match(r'^\d+h$', open_time):
            return HttpResponse('<script>alert("运营时间格式不正确！请使用 数字+h 格式，例如：1h、8h、24h");history.back();</script>')

        Play.objects.create(
            name=name,
            addr=addr,
            price=price,
            start_time=start_time,
            open_time=open_time,
            image=relative_path,
            inf=inf,
            merchant=user,
        )
        return redirect('/play/')

    return render(request, 'play/playsend.html', {'user_id': user.id})


def playdetails(request):
    """娱乐场所详情页"""
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('/index/')

    play_id = request.GET.get('playid')
    if not play_id:
        return HttpResponse("参数错误！")

    play = Play.objects.filter(id=play_id).first()
    if not play:
        return HttpResponse("娱乐场所不存在！")

    records = PlayOrder.objects.filter(play_id=play_id, pos=5).select_related('user').order_by('-time')
    return render(request, 'play/playdetails.html', {
        'play': play,
        'user_id': user_id,
        'records': records,
    })


def playorder(request):
    """购买门票"""
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('/index/')

    play_id = request.GET.get('playid')
    if not play_id:
        return HttpResponse("参数错误！")

    play = Play.objects.filter(id=play_id).first()
    if not play:
        return HttpResponse("娱乐场所不存在！")

    if request.method == 'POST':
        visit_time = request.POST.get('visit_time')
        num = request.POST.get('num')

        if not visit_time or not num:
            return HttpResponse("请填写完整的购票信息！")

        try:
            num = int(num)
            if num <= 0:
                return HttpResponse("购买票数必须大于0！")
        except (TypeError, ValueError):
            return HttpResponse("购买票数必须是正整数！")

        visit_dt = parse_datetime(visit_time)
        if not visit_dt:
            return HttpResponse("预定时间格式不正确！")

        cost = play.price * num
        PlayOrder.objects.create(
            user_id=user_id,
            play_id=play_id,
            num=num,
            visit_time=visit_dt,
            cost=cost,
            pos=4,
        )
        play.orders += 1
        play.save()

        return redirect(f'/playdetails/?playid={play_id}')

    return render(request, 'play/playorder.html', {'play': play, 'user_id': user_id})


def playcomment(request):
    """门票订单评价"""
    if not request.session.get('user_id'):
        return redirect('/index/')

    order_id = request.GET.get('orderid')
    if not order_id:
        return HttpResponse("参数错误！")

    order = PlayOrder.objects.filter(id=order_id).first()
    if not order:
        return HttpResponse("订单不存在！")

    if order.user_id != request.session.get('user_id'):
        return HttpResponse("无权评价该订单！")

    if request.method == 'POST':
        score = request.POST.get('score')
        comment = request.POST.get('comment', '')

        error = save_play_review(order, score, comment)
        if error:
            return HttpResponse(error)

        return redirect('/space/')

    return render(request, 'play/playcomment.html', {'order': order})


def playorderpos(request):
    """门票订单状态/详情"""
    if not request.session.get('user_id'):
        return redirect('/index/')

    order_id = request.GET.get('orderid')
    if not order_id:
        return HttpResponse("参数错误！")

    order = PlayOrder.objects.filter(id=order_id).select_related('play').first()
    if not order:
        return HttpResponse("订单不存在！")

    if order.user_id != request.session.get('user_id'):
        return HttpResponse("无权查看该订单！")

    if request.method == 'POST':
        score = request.POST.get('score')
        comment = request.POST.get('comment', '')

        error = save_play_review(order, score, comment)
        if error:
            return HttpResponse(error)

        return redirect('/space/')

    review_status = '已评价' if order.pos == 5 else '待评价'

    return render(request, 'play/playorderpos.html', {
        'order': order,
        'review_status': review_status,
    })


# ==================== 骑手模块 ====================

def rider_orders(request):
    """骑手订单中心：展示所有可接的订单(pos=0)"""
    user = get_login_user(request)
    if not user:
        return redirect('/index/')
    if not is_rider(user):
        return HttpResponse("只有骑手可以访问此页面！")

    # 所有待接单的订单
    available_orders = Order.objects.filter(pos=0).select_related('food', 'user')
    return render(request, 'rider_orders.html', {
        'user_id': user.id,
        'orders': available_orders,
    })


def rider_accept(request):
    """骑手接单：pos=0 → pos=1，绑定骑手"""
    user = get_login_user(request)
    if not user:
        return redirect('/index/')
    if not is_rider(user):
        return HttpResponse("只有骑手可以接单！")

    order_id = request.GET.get('orderid')
    if not order_id:
        return HttpResponse("参数错误！")

    order = Order.objects.filter(id=order_id, pos=0).first()
    if not order:
        return HttpResponse('<script>alert("该订单已被其他骑手接走或不存在！");history.back();</script>')

    order.pos = 1
    order.rider = user
    order.save()
    return redirect('/rider/')


def rider_deliver(request):
    """骑手已送达：pos=3 → pos=4"""
    user = get_login_user(request)
    if not user:
        return redirect('/index/')
    if not is_rider(user):
        return HttpResponse("只有骑手可以操作！")

    order_id = request.GET.get('orderid')
    if not order_id:
        return HttpResponse("参数错误！")

    order = Order.objects.filter(id=order_id, pos=3, rider=user).first()
    if not order:
        return HttpResponse('<script>alert("该订单无法操作或不属于您！");history.back();</script>')

    order.pos = 4
    order.save()
    return redirect('/space/')

def rider_get(request):
    """骑手已取餐：pos=2 → pos=3"""
    user = get_login_user(request)
    if not user:
        return redirect('/index/')
    if not is_rider(user):
        return HttpResponse("只有骑手可以操作！")

    order_id = request.GET.get('orderid')
    if not order_id:
        return HttpResponse("参数错误！")

    order = Order.objects.filter(id=order_id, pos=2, rider=user).first()
    if not order:
        return HttpResponse('<script>alert("该订单无法操作或不属于您！");history.back();</script>')

    order.pos = 3
    order.save()
    return redirect('/space/')


def merchant_prepare(request):
    """商家完成食物准备：pos=1 → pos=2"""
    user = get_login_user(request)
    if not user:
        return redirect('/index/')
    if not is_merchant(user):
        return HttpResponse("只有商家可以操作！")

    order_id = request.GET.get('orderid')
    if not order_id:
        return HttpResponse("参数错误！")

    order = Order.objects.filter(id=order_id, pos=1, food__merchant=user).first()
    if not order:
        return HttpResponse('<script>alert("该订单无法操作或不属于您的商品！");history.back();</script>')

    order.pos = 2
    order.save()
    return redirect('/space/')
