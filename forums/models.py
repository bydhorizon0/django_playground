from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

# 추후 Mixin을 사용해 Soft delete 적용
# class SoftDeleteQuerySet(models.QuerySet):
#     pass
#
#
# class SoftDeleteManager(models.Manager.from_queryset(SoftDeleteQuerySet)):
#     pass
#
#
# class SoftDeleteMixin(models.Model):
#     is_deleted = models.BooleanField(default=False)
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
#
#     objects = SoftDeleteManager()
#     all_objects = models.Manager()
#
#     class Meta:
#         abstract = True
#
#     def delete(self, using=None, keep_parents=False):
#         raise NotImplementedError
#
#     def hard_delete(self, *args, **kwargs):
#         return super().delete(*args, **kwargs)


class Post(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    view_count = models.PositiveIntegerField(default=0)  # 음수 방지

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="posts",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
        ]


class Comment(models.Model):
    content = models.TextField()

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="comments",
    )

    parent = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="replies",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["post", "created_at"]),  # 게시글별 댓글 목록 조회
            models.Index(fields=["parent", "created_at"]),  # 대댓글 조회
        ]

    # 대댓글 1단계 Validation
    def clean(self):
        if self.parent_id:
            parent = Comment.objects.select_related("parent").get(pk=self.parent_id)

            if parent.parent_id is not None:
                raise ValidationError("대댓글은 1단계까지만 허용됩니다.")
            if parent.post_id != self.post_id:
                raise ValidationError("같은 게시글의 댓글만 가능합니다.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
