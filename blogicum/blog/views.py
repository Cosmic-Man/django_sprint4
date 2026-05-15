from django.conf import settings
from django.shortcuts import get_object_or_404
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.utils import timezone
from django.db.models import Q, Count
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, ProfileForm
from django.shortcuts import get_object_or_404, redirect

User = get_user_model()


class PostListView(ListView):
    """Главная страница со списком постов"""

    template_name = "blog/index.html"
    context_object_name = "page_obj"
    paginate_by = settings.POSTS_PER_PAGE

    def get_queryset(self):
        return (
            Post.objects.filter(
                pub_date__lte=timezone.now(),
                is_published=True,
                category__is_published=True,
            )
            .select_related("author", "category")
            .annotate(comment_count=Count("comments"))
            .order_by("-pub_date")
        )


class ProfilePostsView(ListView):
    """Страница пользователя с его постами"""

    template_name = "blog/profile.html"
    context_object_name = "page_obj"
    paginate_by = settings.POSTS_PER_PAGE

    def get_queryset(self):
        self.profile_user = get_object_or_404(User,
                                              username=self.kwargs["username"])
        if self.request.user == self.profile_user:
            return (
                Post.objects.filter(author=self.profile_user)
                .select_related("author", "category")
                .annotate(comment_count=Count("comments"))
                .order_by("-pub_date")
            )
        return (
            Post.objects.filter(
                author=self.profile_user,
                pub_date__lte=timezone.now(),
                is_published=True,
                category__is_published=True,
            )
            .select_related("author", "category")
            .annotate(comment_count=Count("comments"))
            .order_by("-pub_date")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.profile_user
        return context


class EditProfileView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование профиля пользователя"""

    model = User
    form_class = ProfileForm
    template_name = "blog/edit_profile.html"

    def get_object(self, queryset=None):
        return self.request.user

    def test_func(self):
        return self.request.user.username == self.kwargs["username"]

    def get_success_url(self):
        return reverse_lazy(
            "blog:profile", kwargs={"username": self.request.user.username}
        )


class CategoryPostsView(ListView):
    """Страница категории с постами"""

    template_name = "blog/category.html"
    context_object_name = "page_obj"
    paginate_by = settings.POSTS_PER_PAGE

    def get_queryset(self):
        self.category = get_object_or_404(
            Category, slug=self.kwargs["slug"], is_published=True
        )
        return (
            Post.objects.filter(
                category=self.category,
                pub_date__lte=timezone.now(),
                is_published=True,
                category__is_published=True,
            )
            .select_related("author", "category")
            .annotate(comment_count=Count('comments'))
            .order_by("-pub_date")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    """Создание нового поста"""

    model = Post
    form_class = PostForm
    template_name = "blog/create.html"

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "blog:profile", kwargs={"username": self.request.user.username}
        )


class PostUpdateView(LoginRequiredMixin, UpdateView):
    """Редактирование поста"""

    model = Post
    form_class = PostForm
    template_name = "blog/create.html"
    pk_url_kwarg = "pk"

    def dispatch(self, request, *args, **kwargs):
        """Проверяем права доступа перед обработкой запроса"""
        if not request.user.is_authenticated and request.method == "POST":
            post_id = self.kwargs.get("pk")
            if post_id:
                return redirect("blog:post_detail", pk=post_id)

        if request.user.is_authenticated:
            post = self.get_object()
            if post.author != request.user:
                return redirect("blog:post_detail", pk=self.kwargs.get("pk"))

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = True
        return context

    def get_success_url(self):
        return reverse_lazy("blog:post_detail", kwargs={"pk": self.object.pk})


class PostDetailView(DetailView):
    """Страница отдельного поста с комментариями"""

    model = Post
    template_name = "blog/detail.html"
    context_object_name = "post"

    def get_queryset(self):
        queryset = Post.objects.select_related("author", "category")

        if self.request.user.is_authenticated:
            return queryset.filter(
                Q(author=self.request.user)
                | Q(
                    pub_date__lte=timezone.now(),
                    is_published=True,
                    category__is_published=True,
                )
            ).distinct()

        return queryset.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context["comments"] = self.object.comments.select_related(
            "author").all()
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание комментария"""

    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs["post_id"])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("blog:post_detail",
                            kwargs={"pk": self.kwargs["post_id"]})


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование комментария"""

    model = Comment
    form_class = CommentForm
    template_name = "blog/comment.html"

    def get_queryset(self):
        """Ограничиваем выборку только комментариями текущего пользователя"""
        return Comment.objects.filter(author=self.request.user)

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        return reverse_lazy("blog:post_detail",
                            kwargs={"pk": self.kwargs["post_id"]})


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление комментария"""

    model = Comment
    template_name = "blog/comment.html"

    def get_queryset(self):
        """Ограничиваем выборку только комментариями текущего пользователя"""
        return Comment.objects.filter(author=self.request.user)

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        return reverse_lazy("blog:post_detail",
                            kwargs={"pk": self.kwargs["post_id"]})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление поста"""

    model = Post
    template_name = "blog/post_confirm_delete.html"

    def get_queryset(self):
        """Ограничиваем выборку только постами текущего пользователя"""
        return Post.objects.filter(author=self.request.user)

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def get_success_url(self):
        return reverse_lazy(
            "blog:profile", kwargs={"username": self.request.user.username}
        )
