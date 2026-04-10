import random

from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.db import transaction
from faker import Faker

from forums.models import Post, Comment

User = get_user_model()


class Command(BaseCommand):
    help = "Seed 1000 dummy posts and comments"

    def handle(self, *args, **options):
        fake = Faker()
        user = User.objects.first()

        if user is None:
            self.stdout.write(self.style.ERROR("유저가 없습니다."))
            return

        self.stdout.write("데이터 생성 시작...")

        with transaction.atomic():
            posts: list[Post] = [
                Post(
                    title=fake.sentence(),
                    content=fake.text(),
                    author=user,
                    view_count=random.randint(0, 500),
                )
                for _ in range(100_000_0)
            ]
            created_posts = Post.objects.bulk_create(posts)
            self.stdout.write(f"Post {len(created_posts)}개 생성 완료")

            # # 부모 댓글 생성 (Post당 5개씩 총 500개 생성)
            # parent_comments: list[Comment] = []
            # for post in created_posts:
            #     for _ in range(5):
            #         parent_comments.append(
            #             Comment(
            #                 content=fake.sentence(), author=user, post=post, parent=None
            #             )
            #         )
            #
            # # bulk_create는 save()나 clean()을 호출하지 않으므로 빠르다.
            # created_parents = Comment.objects.bulk_create(parent_comments)
            # self.stdout.write(f"부모 Comment {len(created_parents)}개 생성 완료")
            #
            # replies: list[Comment] = [
            #     Comment(
            #         content=fake.word(), author=user, post=parent.post, parent=parent
            #     )
            #     for parent in created_parents
            # ]
            # created_replies = Comment.objects.bulk_create(replies)
            # self.stdout.write(f"대댓글 {len(created_replies)}개 생성 완료")

        self.stdout.write(self.style.SUCCESS("더미 데이터 생성 완료"))
