"""Seed the lifestyle-service SQLite database for benchmarking.

Mirrors the monolith hotel/blog/play seed volume so the /hotels, /blogs and
/plays endpoints can be compared on the same machine with the same script.

Usage (from the project root, using the lifestyle-service settings):

    set SERVICE_USE_SQLITE=true
    set SERVICE_SQLITE_PATH=C:\\path\\life_bench.sqlite3
    set DJANGO_SETTINGS_MODULE=services.lifestyle_service.config.settings
    python 04_tests/performance/seed_lifestyle_sqlite.py --refresh
"""

import argparse
import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_ROOT = REPO_ROOT / "01_source"
sys.path.insert(0, str(SOURCE_ROOT))

os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "services.lifestyle_service.config.settings"
)

import django  # noqa: E402

django.setup()

from services.lifestyle_service.lifestyle.models import (  # noqa: E402
    Blog,
    Comment,
    Hotel,
    HotelOrder,
    Play,
    PlayOrder,
)

HOTELS = 30
PLAYS = 30
BLOGS = 50


def clear_all():
    for model in (Comment, Blog, HotelOrder, PlayOrder, Hotel, Play):
        model.objects.all().delete()


def seed():
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
                merchant_id=1,
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
                merchant_id=1,
            )
        )
    for index in range(40):
        HotelOrder.objects.create(
            user_id=1 + (index % 6),
            hotel=hotels[index % len(hotels)],
            room_type="single",
            duration=1 + (index % 3),
            checkin_time=__import__("django").utils.timezone.now(),
            cost=100 + (index % 60),
            comment="不错" if index % 2 else "",
            score=4.8 if index % 2 else 0.0,
            pos=5 if index % 2 else 4,
        )
    for index in range(40):
        PlayOrder.objects.create(
            user_id=1 + (index % 6),
            play=plays[index % len(plays)],
            num=1 + (index % 3),
            visit_time=__import__("django").utils.timezone.now(),
            cost=30 + (index % 30),
            comment="好玩" if index % 2 else "",
            score=4.6 if index % 2 else 0.0,
            pos=5 if index % 2 else 4,
        )
    blogs = []
    for index in range(BLOGS):
        blogs.append(
            Blog.objects.create(
                title=f"blog title {index}",
                content=f"blog content {index} " + ("x" * 120),
                author_id=1 + (index % 6),
            )
        )
    for index in range(120):
        Comment.objects.create(
            blog=blogs[index % len(blogs)],
            user_id=1 + (index % 6),
            content=f"comment {index}",
        )
    print(
        f"Seeded lifestyle-service: {HOTELS} hotels, {PLAYS} plays, "
        f"{BLOGS} blogs, 120 comments."
    )


def main():
    parser = argparse.ArgumentParser(description="Seed lifestyle-service SQLite DB")
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()
    if args.refresh:
        clear_all()
    seed()


if __name__ == "__main__":
    main()
