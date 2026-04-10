from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.db.models import Count, Prefetch, OuterRef, Subquery, Q, QuerySet
from django.db.models.fields import IntegerField
from django.db.models.functions import Coalesce
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
    ListView,
)

from forums.forms import PostForm, CommentForm
from forums.models import Post, Comment


class PostListView(ListView):
    model = Post
    template_name = "posts/post_list.html"
    context_object_name = "posts"
    paginate_by = 15

    def get_queryset(self):
        comment_count_subquery = (
            Comment.objects.filter(post_id=OuterRef("pk"))
            .values("post_id")
            .annotate(count=Count("id"))
            .values("count")
        )

        queryset = (
            super()
            .get_queryset()
            .select_related("author")
            .annotate(
                comment_count=Coalesce(
                    Subquery(
                        comment_count_subquery,
                        output_field=IntegerField(),
                    ),
                    0,
                )
            )
            .defer("content")
            .only(
                "id",
                "title",
                "created_at",
                "view_count",
                "author_id",
                "author__email",
            )
            .order_by("-created_at", "-id")  # 보조 정렬로 -id 유지
        )

        # 커서 기반 필터링 (ID 기반)
        cursor = self.request.GET.get("cursor")
        if cursor:
            try:
                cursor_id = int(cursor)
                queryset = queryset.filter(id__lt=cursor_id)
            except ValueError:
                raise Http404("Invalid cursor")

        return queryset[: self.paginate_by + 1]

    # 템플릿에 넘길 데이터(dict)를 만드는 단계
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        posts: QuerySet[Post] = self.object_list

        # 다음 페이지 커서 생성 (ID 사용)
        if len(posts) > self.paginate_by:
            last_post = posts[self.paginate_by - 1]
            next_cursor = str(last_post.id)
            context["next_cursor"] = next_cursor
            context[self.context_object_name] = posts[: self.paginate_by]
        else:
            context["next_cursor"] = None
            context[self.context_object_name] = posts

        return context


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = "posts/post_detail.html"
    context_object_name = "post"

    def get_queryset(self):
        return super().get_queryset().select_related("author")

    def get_object(self, queryset=None):
        post: Post = super().get_object(queryset)

        # 조회수 증가 (Atomic update)
        Post.objects.filter(pk=post.pk).update(view_count=models.F("view_count") + 1)
        # 2. 메모리 값 갱신 (SELECT 쿼리 대체)
        # 이 한 줄이 refresh_from_db()의 역할을 완벽히 대신하며 쿼리를 1개 아낍니다.
        post.view_count += 1
        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        reply_queryset = Comment.objects.select_related("author").order_by("created_at")

        # 댓글 + 대댓글 한 번에 fetch
        comments = (
            Comment.objects.filter(post=self.object, parent=None)
            .select_related("author")
            .prefetch_related(Prefetch("replies", queryset=reply_queryset))
            .order_by("created_at")
        )

        context["comments"] = comments
        context["comment_form"] = CommentForm()
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = "posts/post_form.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("forum:post-detail", kwargs={"pk": self.object.pk})


class PostUpdateView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = "posts/post_form.html"

    def dispatch(self, request, *args, **kwargs):
        post: Post = self.get_object()
        if post.author != request.user:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("forum:post-detail", kwargs={"pk": self.object.pk})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    success_url = reverse_lazy("forum:post-list")

    def dispatch(self, request, *args, **kwargs):
        post: Post = self.get_object()

        if post.author != request.user:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


# -- Comment -- #
class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form: CommentForm):
        post = get_object_or_404(Post, pk=self.kwargs["post_id"])
        form.instance.author = self.request.user
        form.instance.post = post
        form.instance.parent_id = self.request.POST.get("parent_id") or None
        return super().form_valid(form)

    # 유효성 실패 시 에러를 들고 상세 페이지로 복귀
    def form_invalid(self, form):
        return redirect(
            reverse("forum:post-detail", kwargs={"pk": self.kwargs["post_id"]})
        )

    def get_success_url(self):
        return reverse("forum:post-detail", kwargs={"pk": self.kwargs["post_id"]})


class CommentUpdateView(LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = "posts/comment_form.html"

    def dispatch(self, request, *args, **kwargs):
        comment: Comment = self.get_object()
        if comment.author != request.user:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("forum:post-detail", kwargs={"pk": self.object.post_id})


class CommentDeleteView(LoginRequiredMixin, DeleteView):
    model = Comment

    def dispatch(self, request, *args, **kwargs):
        comment: Comment = self.get_object()
        if comment.author != request.user:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse("forum:post-detail", kwargs={"pk": self.object.post_id})
