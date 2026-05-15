from django.utils import timezone


# Фильтрация постов
def filter_published_posts(posts_queryset):
    current_time = timezone.now()

    return posts_queryset.filter(
        is_published=True,
        pub_date__lte=current_time,
        category__is_published=True
    )
