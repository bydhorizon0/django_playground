from django.urls import path

from forums import views

app_name = "forum"

urlpatterns = [
    # posts
    path("posts/", views.PostOffsetBasedListView.as_view(), name="post-list"),
    path("posts/<int:pk>/", views.PostDetailView.as_view(), name="post-detail"),
    path("posts/new/", views.PostCreateView.as_view(), name="post-create"),
    path("posts/<int:pk>/edit/", views.PostUpdateView.as_view(), name="post-update"),
    path("posts/<int:pk>/delete/", views.PostDeleteView.as_view(), name="post-delete"),
    # comments
    path(
        "posts/<int:post_id>/comments/new/",
        views.CommentCreateView.as_view(),
        name="comment-create",
    ),
    path(
        "comments/<int:pk>/edit/",
        views.CommentUpdateView.as_view(),
        name="comment-update",
    ),
    path(
        "comments/<int:pk>/delete/",
        views.CommentDeleteView.as_view(),
        name="comment-delete",
    ),
]
