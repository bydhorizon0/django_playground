from __future__ import annotations

from django.contrib import admin

from forums.models import Post, Comment


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1

    fields = ("author", "content")
    readonly_fields = ("created_at", "updated_at")

    can_delete = True
    show_change_link = True


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "content", "created_at", "updated_at", "author")
    list_display_links = ("id", "title")
    list_filter = ("created_at", "updated_at")
    search_fields = ("title", "content", "author__email")
    readonly_fields = ("author", "view_count", "created_at", "updated_at")

    inlines = [CommentInline]
