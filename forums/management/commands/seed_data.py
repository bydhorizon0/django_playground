import random

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from faker import Faker

from forums.models import Post

User = get_user_model()


class Command(BaseCommand):
    help = "Seed dummy posts and comments"

    def handle(self, *args, **options):
        fake = Faker()
        user = User.objects.first()

        total_count = 1_000_000
        chunk_size = 10_000

        self.stdout.write(
            f"{total_count}개 데이터 생성 시작 (Chunk size: {chunk_size})"
        )

        # fake 미리 생성
        titles = [fake.sentence()[:250] for _ in range(100)]
        contents = [fake.text() for _ in range(100)]

        for i in range(0, total_count, chunk_size):
            posts = [
                Post(
                    title=random.choices(titles),
                    content=random.choices(contents),
                    author=user,
                    view_count=0,
                )
                for _ in range(chunk_size)
            ]
            Post.objects.bulk_create(posts)
            self.stdout.write(f"{i + chunk_size}개 처리 중...")

        self.stdout.write(self.style.SUCCESS(f"{total_count}건 더미 데이터 생성 완료"))
