from django.conf import settings
from django.shortcuts import get_object_or_404, redirect
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
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm, ProfileForm
from .utils import get_visible_posts_for_user

User = get_user_model()


class PostListView(ListView):
    """Главная страница со списком постов"""

    template_name = "blog/index.html"
    context_object_name = "page_obj"
    paginate_by = settings.POSTS_PER_PAGE

    def get_queryset(self):
        """Возвращает только опубликованные посты"""
        return get_visible_posts_for_user(
            user=self.request.user,
        )


class ProfilePostsView(ListView):
    """Страница пользователя с его постами"""

    template_name = "blog/profile.html"
    context_object_name = "page_obj"
    paginate_by = settings.POSTS_PER_PAGE

    def get_queryset(self):
        self.profile_user = get_object_or_404(User,
                                              username=self.kwargs["username"])

        return get_visible_posts_for_user(
            user=self.request.user,
            queryset=self.profile_user.posts.all(),
            author=self.profile_user,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile"] = self.profile_user
        return context


class CategoryPostsView(ListView):
    """Страница категории с постами"""

    template_name = "blog/category.html"
    context_object_name = "page_obj"
    paginate_by = settings.POSTS_PER_PAGE

    def get_queryset(self):
        self.category = get_object_or_404(
            Category, slug=self.kwargs["slug"], is_published=True
        )

        return get_visible_posts_for_user(
            user=self.request.user,
            queryset=self.category.posts.all(),
            category=self.category,
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class PostDetailView(DetailView):
    """Страница отдельного поста с комментариями"""

    model = Post
    template_name = "blog/detail.html"
    context_object_name = "post"
    pk_url_kwarg = "post_id"

    def get_object(self, queryset=None):
        """Получает пост с проверкой прав доступа"""
        return get_visible_posts_for_user(
            user=self.request.user, post_id=self.kwargs[self.pk_url_kwarg]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = CommentForm()
        context["comments"] = self.object.comments.select_related(
            "author").all()
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
    pk_url_kwarg = "post_id"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("login")

        post = self.get_object()
        if post.author != request.user:
            return redirect("blog:post_detail",
                            post_id=self.kwargs.get("post_id"))

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["is_edit"] = True
        return context

    def get_success_url(self):
        return reverse_lazy("blog:post_detail",
                            kwargs={"post_id": self.object.pk})


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление поста"""

    model = Post
    template_name = "blog/post_confirm_delete.html"
    pk_url_kwarg = "post_id"

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


class CommentCreateView(LoginRequiredMixin, CreateView):
    """Создание комментария"""

    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(Post, pk=self.kwargs["post_id"])
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail", kwargs={"post_id": self.kwargs["post_id"]}
        )


class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Редактирование комментария"""

    model = Comment
    form_class = CommentForm
    template_name = "blog/comment.html"
    pk_url_kwarg = "comment_id"

    def get_queryset(self):
        """Ограничиваем выборку только комментариями текущего пользователя"""
        return Comment.objects.filter(author=self.request.user)

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail", kwargs={"post_id": self.kwargs["post_id"]}
        )


class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Удаление комментария"""

    model = Comment
    template_name = "blog/comment.html"
    pk_url_kwarg = "comment_id"

    def get_queryset(self):
        """Ограничиваем выборку только комментариями текущего пользователя"""
        return Comment.objects.filter(author=self.request.user)

    def test_func(self):
        comment = self.get_object()
        return self.request.user == comment.author

    def get_success_url(self):
        return reverse_lazy(
            "blog:post_detail", kwargs={"post_id": self.kwargs["post_id"]}
        )


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
