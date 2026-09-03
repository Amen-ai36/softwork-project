"""Seed the trade-service SQLite database with food data for benchmarking.

The trade-service is a standalone Django app (services.trade_service); it needs
a populated database before /foods can be benchmarked. This mirrors the
monolith seed volume (60 foods) so the two food-listing interfaces can be
compared on the same machine with the same script and similar data.

Usage (from the project root, using the trade-service settings):

    set SERVICE_USE_SQLITE=true
    set SERVICE_SQLITE_PATH=C:\\path\\trade_bench.sqlite3
    set DJANGO_SETTINGS_MODULE=services.trade_service.config.settings
    python 04_tests/performance/seed_trade_sqlite.py --refresh
"""

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPO_ROOT / "01_source"
sys.path.insert(0, str(SOURCE_ROOT))

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "services.trade_service.config.settings"
)

import django  # noqa: E402

django.setup()

from services.trade_service.trade.models import (  # noqa: E402
    CartItem,
    Food,
    GroupBuyCoupon,
    Order,
)

FOODS = 60
ORDERS = 120


def clear_all():
    for model in (GroupBuyCoupon, CartItem, Order, Food):
        model.objects.all().delete()


def seed():
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
                ratenum=10 + index,
                rating=4 + (index % 10) / 10.0,
                inf=f"description {index}",
                merchant_id=1,
            )
        )
    for index in range(ORDERS):
        food = foods[index % len(foods)]
        Order.objects.create(
            user_id=1 + (index % 6),
            rider_id=1 if index % 2 else None,
            food=food,
            num=1 + (index % 3),
            cost=food.price * (1 + (index % 3)),
            address=f"address {index}",
            comment=("好评" if index % 6 == 5 else ""),
            pos=index % 6,
        )
    for index in range(60):
        GroupBuyCoupon.objects.create(
            user_id=1 + (index % 6),
            food=foods[index % len(foods)],
            num=1 + (index % 2),
            cost=20 + (index % 20),
            code=f"GB{index:06d}",
            status=index % 3,
        )
    print(f"Seeded trade-service: {FOODS} foods, {ORDERS} orders, 60 coupons.")


def main():
    parser = argparse.ArgumentParser(description="Seed trade-service SQLite DB")
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    if args.refresh:
        clear_all()
    seed()


if __name__ == "__main__":
    main()
