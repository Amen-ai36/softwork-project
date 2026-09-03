"""Seed a local SQLite database for the monolith performance benchmark.

The monolith needs a populated database before it can be benchmarked and the
seed.sql dump is MySQL-only and requires container credentials. This script
creates a representative working data set through the Django ORM so the same
benchmark can run on a single host without Docker or MySQL.

The baseline monolith lives at the git tag ``monolith-start`` (its
``food_master`` package sits at the checkout root, unlike ``main`` where it
sits under ``01_source``). Two things are needed before seeding:

1. A local SQLite settings module ``food_master/sqlite_settings.py`` in that
   checkout (created below), because the baseline has no SQLite settings:

       import os
       from .settings import *  # noqa
       BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
       DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3",
                                "NAME": os.path.join(BASE_DIR, "bench_food_master.sqlite3")}}
       DEBUG = False
       ALLOWED_HOSTS = ["*"]

2. The commands below, run from the monolith checkout, with ``PYTHONPATH``
   pointing at that checkout root.

Usage:

    git worktree add .monolith-bench monolith-start
    # (create food_master/sqlite_settings.py in .monolith-bench as above)
    cd .monolith-bench
    set PYTHONPATH=<checkout_root>
    set DJANGO_SETTINGS_MODULE=food_master.sqlite_settings
    ..\\..\\<repo>\\.venv\\Scripts\\python manage.py migrate
    ..\\..\\<repo>\\.venv\\Scripts\\python <repo>\\04_tests\\performance\\seed_sqlite.py --refresh

It prints a usable ``sessionid=...`` cookie (for a logged-in ordinary user) so
the benchmark can target authenticated business endpoints.
"""

import argparse
import os
import sys
from datetime import timedelta
from pathlib import Path

from django.utils import timezone

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "food_master.sqlite_settings")

import django  # noqa: E402

django.setup()

from myapp.models import (  # noqa: E402
    Blog,
    Comment,
    Food,
    GroupBuyCoupon,
    Hotel,
    HotelOrder,
    Order,
    Play,
    PlayOrder,
    Temp,
    User,
)

ORDERS = 120
FOODS = 60
HOTELS = 30
PLAYS = 30
BLOGS = 50
COMMENTS = 120
COUPONS = 60
CART = 40

NOW = timezone.now()


def clear_all():
    for model in (Comment, Blog, PlayOrder, HotelOrder, GroupBuyCoupon, Temp, Order):
        model.objects.all().delete()
    for model in (Play, Hotel, Food):
        model.objects.all().delete()
    User.objects.all().delete()


def make_users():
    # business users (type 0), one merchant (2), one rider (1), one admin (3)
    users = []
    for index in range(6):
        users.append(
            User.objects.create(
                username=f"user{index:02d}",
                password="pass",
                phone=f"1380000{index:04d}",
                word=f"signature {index}",
            )
        )
    merchant = User.objects.create(
        username="merchant01", password="pass", phone="13899990001", usertype=2
    )
    rider = User.objects.create(
        username="rider01", password="pass", phone="13899990002", usertype=1
    )
    admin = User.objects.create(
        username="admin01", password="pass", phone="13899990003", usertype=3
    )
    return users, merchant, rider, admin


def make_catalog(merchant):
    foods = []
    for index in range(FOODS):
        foods.append(
            Food.objects.create(
                name=f"food{index:02d}",
                price=8 + (index % 20),
                image=f"/static/images/food{index % 5}.jpg",
                sale=0,
                saleperson=0,
                providor="商家",
                rating=4 + (index % 10) / 10.0,
                ratenum=10 + index,
                inf=f"description {index}",
                merchant=merchant,
            )
        )
    hotels = []
    for index in range(HOTELS):
        hotels.append(
            Hotel.objects.create(
                name=f"hotel{index:02d}",
                addr=f"address {index}",
                price_clock=30 + (index % 20),
                price_day=120 + (index % 60),
                price_double_clock=50 + (index % 20),
                price_double_day=180 + (index % 80),
                price_special=260 + (index % 100),
                image=f"/static/images/hotel{index % 5}.jpg",
                rating=4 + (index % 10) / 10.0,
                orders=0,
                ratenum=5 + index,
                inf=f"hotel info {index}",
                merchant=merchant,
            )
        )
    plays = []
    for index in range(PLAYS):
        plays.append(
            Play.objects.create(
                name=f"play{index:02d}",
                addr=f"address {index}",
                price=20 + (index % 30),
                image=f"/static/images/play{index % 5}.jpg",
                rating=4 + (index % 10) / 10.0,
                ratenum=3 + index,
                inf=f"play info {index}",
                orders=0,
                merchant=merchant,
            )
        )
    return foods, hotels, plays


def make_orders(users, foods, rider):
    orders = []
    for index in range(ORDERS):
        food = foods[index % len(foods)]
        owner = users[index % len(users)]
        pos = index % 6  # 0..5
        orders.append(
            Order.objects.create(
                user=owner,
                food=food,
                rider=rider if pos >= 1 else None,
                num=1 + (index % 3),
                cost=food.price * (1 + (index % 3)),
                address=f"address {index}",
                comment=("好评" if pos == 5 else ""),
                pos=pos,
                scoretofood=5.0 if pos == 5 else 0.0,
                scoretodeliver=4.5 if pos == 5 else 0.0,
            )
        )
    return orders


def make_coupons(users, foods):
    coupons = []
    for index in range(COUPONS):
        coupons.append(
            GroupBuyCoupon.objects.create(
                user=users[index % len(users)],
                food=foods[index % len(foods)],
                num=1 + (index % 2),
                cost=20 + (index % 20),
                code=f"GB{index:06d}",
                status=index % 3,
                used_at=NOW if index % 3 == 1 else None,
            )
        )
    return coupons


def make_content(users, foods, hotels, plays):
    blogs = []
    for index in range(BLOGS):
        blogs.append(
            Blog.objects.create(
                title=f"blog title {index}",
                content=f"blog content {index} " + ("x" * 120),
                authorid=users[index % len(users)],
            )
        )
    comments = []
    for index in range(COMMENTS):
        comments.append(
            Comment.objects.create(
                blogid=blogs[index % len(blogs)],
                userid=users[index % len(users)].id,
                content=f"comment {index} @ {NOW:%H%M}",
            )
        )
    hotel_orders = []
    for index in range(40):
        hotel_orders.append(
            HotelOrder.objects.create(
                user=users[index % len(users)],
                hotel=hotels[index % len(hotels)],
                room_type=("single" if index % 2 else "double"),
                duration=1 + (index % 3),
                checkin_time=NOW + timedelta(days=index % 7),
                cost=100 + (index % 60),
                comment=("不错" if index % 2 else ""),
                score=4.8 if index % 2 else 0.0,
                pos=5 if index % 2 else 4,
            )
        )
    play_orders = []
    for index in range(40):
        play_orders.append(
            PlayOrder.objects.create(
                user=users[index % len(users)],
                play=plays[index % len(plays)],
                num=1 + (index % 3),
                visit_time=NOW + timedelta(days=index % 7),
                cost=30 + (index % 30),
                comment=("好玩" if index % 2 else ""),
                score=4.6 if index % 2 else 0.0,
                pos=5 if index % 2 else 4,
            )
        )
    cart = []
    for index in range(CART):
        cart.append(
            Temp.objects.create(
                user=users[index % len(users)],
                food=foods[index % len(foods)],
                num=1 + (index % 2),
                cost=foods[index % len(foods)].price,
                address=f"address {index}",
            )
        )
    return blogs, comments, hotel_orders, play_orders, cart


def make_session(user):
    from django.contrib.sessions.backends.db import SessionStore

    store = SessionStore()
    store["user_id"] = user.id
    store.create()
    return store.session_key


def main():
    parser = argparse.ArgumentParser(description="Seed monolith SQLite DB")
    parser.add_argument(
        "--refresh", action="store_true", help="Delete existing rows first"
    )
    parser.add_argument(
        "--session-user", default="user00", help="Username for the benchmark session"
    )
    args = parser.parse_args()

    if args.refresh:
        clear_all()

    users, merchant, rider, admin = make_users()
    foods, hotels, plays = make_catalog(merchant)
    make_orders(users, foods, rider)
    make_coupons(users, foods)
    make_content(users, foods, hotels, plays)

    target = User.objects.filter(username=args.session_user).first() or users[0]
    key = make_session(target)
    print(
        f"Seeded: {FOODS} foods, {HOTELS} hotels, {PLAYS} plays, "
        f"{BLOGS} blogs, {ORDERS} orders."
    )
    print(f"Session cookie for {target.username}: sessionid={key}")


if __name__ == "__main__":
    main()
