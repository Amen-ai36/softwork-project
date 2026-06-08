from functools import wraps

from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from .models import Blog, Comment, Food, Hotel, HotelOrder, Order, Play, PlayOrder, User


def admin_required(view_func):
    @wraps(view_func)
    def wrapped(request, *args, **kwargs):
        user_id = request.session.get('user_id')
        user = User.objects.filter(id=user_id, usertype=3, isDelete=False).first()
        if not user:
            return redirect('/account/login/')
        request.app_admin = user
        return view_func(request, *args, **kwargs)
    return wrapped


@admin_required
def admin_dashboard(request):
    section = request.GET.get('section', 'overview')
    valid_sections = {'overview', 'users', 'orders', 'content', 'blogs'}
    if section not in valid_sections:
        section = 'overview'

    keyword = request.GET.get('q', '').strip()
    users = User.objects.all().order_by('id')
    orders = Order.objects.select_related('user', 'food', 'rider').order_by('-time')
    blogs = Blog.objects.select_related('authorid').annotate(
        comment_count=Count('comment')
    ).order_by('-created_at')

    if keyword:
        users = users.filter(Q(username__icontains=keyword) | Q(phone__icontains=keyword))
        orders = orders.filter(
            Q(user__username__icontains=keyword)
            | Q(food__name__icontains=keyword)
            | Q(address__icontains=keyword)
        )
        blogs = blogs.filter(
            Q(title__icontains=keyword) | Q(authorid__username__icontains=keyword)
        )

    revenue = Order.objects.aggregate(total=Sum('cost'))['total'] or 0
    context = {
        'admin_user': request.app_admin,
        'section': section,
        'keyword': keyword,
        'users': users,
        'orders': orders,
        'blogs': blogs,
        'foods': Food.objects.select_related('merchant').order_by('-id'),
        'hotels': Hotel.objects.select_related('merchant').order_by('-id'),
        'plays': Play.objects.select_related('merchant').order_by('-id'),
        'comments': Comment.objects.order_by('-created_at')[:100],
        'stats': {
            'active_users': User.objects.filter(isDelete=False).count(),
            'orders': Order.objects.count(),
            'pending_orders': Order.objects.filter(pos__lt=4).count(),
            'revenue': revenue,
            'foods': Food.objects.count(),
            'hotels': Hotel.objects.count(),
            'plays': Play.objects.count(),
            'blogs': Blog.objects.filter(isdeleted=False).count(),
            'hotel_orders': HotelOrder.objects.count(),
            'play_orders': PlayOrder.objects.count(),
        },
        'recent_orders': Order.objects.select_related('user', 'food', 'rider').order_by('-time')[:8],
    }
    return render(request, 'manage/dashboard.html', context)


@admin_required
@require_POST
def admin_user_action(request):
    target = User.objects.filter(id=request.POST.get('user_id')).first()
    if not target:
        messages.error(request, '用户不存在。')
        return redirect('/manage/?section=users')

    action = request.POST.get('action')
    if action == 'toggle_active':
        if target.id == request.app_admin.id:
            messages.error(request, '不能停用当前登录的管理员账号。')
        else:
            target.isDelete = not target.isDelete
            target.save(update_fields=['isDelete'])
            messages.success(request, '用户状态已更新。')
    elif action == 'change_role':
        try:
            role = int(request.POST.get('role'))
        except (TypeError, ValueError):
            role = -1
        if role not in (0, 1, 2, 3):
            messages.error(request, '无效的用户角色。')
        elif target.id == request.app_admin.id and role != 3:
            messages.error(request, '不能移除当前账号的管理员权限。')
        else:
            target.usertype = role
            target.save(update_fields=['usertype'])
            messages.success(request, '用户角色已更新。')
    else:
        messages.error(request, '不支持的用户操作。')
    return redirect('/manage/?section=users')


@admin_required
@require_POST
def admin_order_action(request):
    order = Order.objects.filter(id=request.POST.get('order_id')).first()
    if not order:
        messages.error(request, '订单不存在。')
        return redirect('/manage/?section=orders')

    if order.pos == 5:
        messages.error(request, '已评价订单不能由管理员修改。')
    elif request.POST.get('action') != 'complete':
        messages.error(request, '管理员只能将订单标记为已送达。')
    elif order.pos == 4:
        messages.info(request, '该订单已经是已送达状态。')
    else:
        order.pos = 4
        order.save(update_fields=['pos'])
        messages.success(request, '订单状态已更新，评价状态仍由用户提交评价后产生。')
    return redirect('/manage/?section=orders')


@admin_required
@require_POST
def admin_blog_action(request):
    item_type = request.POST.get('item_type')
    item_id = request.POST.get('item_id')
    if item_type == 'blog':
        item = Blog.objects.filter(id=item_id).first()
    elif item_type == 'comment':
        item = Comment.objects.filter(id=item_id).first()
    else:
        item = None

    if not item:
        messages.error(request, '内容不存在。')
    else:
        item.isdeleted = not item.isdeleted
        item.save(update_fields=['isdeleted'])
        messages.success(request, '内容审核状态已更新。')
    return redirect('/manage/?section=blogs')


@admin_required
@require_POST
def admin_logout(request):
    request.session.flush()
    return redirect('/account/login/')