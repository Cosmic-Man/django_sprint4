from django.utils import timezone
from django.db.models import Count
from django.shortcuts import get_object_or_404
from django.http import Http404
from .models import Post


def filter_published_posts(posts_queryset):
    """Фильтрация только опубликованных постов"""
    current_time = timezone.now()
    return posts_queryset.filter(
        is_published=True,
        pub_date__lte=current_time,
        category__is_published=True
    )


def annotate_with_comment_count(posts_queryset):
    """Подсчет комментариев к каждому посту"""
    return posts_queryset.annotate(comment_count=Count("comments"))


def optimize_post_queryset(posts_queryset):
    """Оптимизация queryset подгрузкой связанных объектов"""
    return posts_queryset.select_related("author",
                                         "category").order_by("-pub_date")


def get_posts_queryset(
    queryset=None,
    author=None,
    category=None,
    filter_published=True
):
    """
    Универсальная функция для получения queryset постов
    с настройками фильтрации
    """
    if queryset is None:
        queryset = Post.objects.all()

    queryset = optimize_post_queryset(queryset)

    if author:
        queryset = queryset.filter(author=author)

    if category:
        queryset = queryset.filter(category=category)

    if filter_published:
        queryset = filter_published_posts(queryset)

    queryset = annotate_with_comment_count(queryset)

    return queryset


def get_visible_posts_for_user(
    user, queryset=None, author=None, category=None, post_id=None
):
    """Получение постов с учетом прав пользователя"""
    if post_id is not None:
        post = get_object_or_404(Post, pk=post_id)

        current_time = timezone.now()
        is_published = (
            post.is_published
            and post.pub_date <= current_time
            and post.category.is_published
        )

        is_author = user.is_authenticated and post.author == user

        if not (is_published or is_author):
            raise Http404("Пост не найден")

        return post

    if user.is_authenticated and author == user:
        return get_posts_queryset(
            queryset=queryset,
            author=author,
            category=category,
            filter_published=False
        )

    return get_posts_queryset(
        queryset=queryset,
        author=author,
        category=category,
        filter_published=True
    )
