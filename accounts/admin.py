from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from accounts.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # 관리자 목록 화면에서 보여질 필드
    list_display: tuple[str, ...] = ("email", "is_staff", "is_active", "created_at")

    # 상세 화면에서 필드를 그룹화하여 표시
    fieldsets = [
        (
            None,
            {
                "fields": ("email", "password"),
            },
        ),
        (
            "권한",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "중요 날짜",
            {
                "fields": (
                    "last_login",
                    "created_at",
                )
            },
        ),
    ]

    # 유저 생성 화면에서 사용할 필드(AbstractBaseUser 사용 시 필수)
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "password"),
            },
        ),
    )

    # 검색 및 정렬 설정
    search_fields = ("email",)
    ordering = ("email",)

    # 읽기 전용 필드 설정
    readonly_fields = ("created_at", "last_login")
