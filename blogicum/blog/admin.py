from django.contrib import admin
from .models import Post, Category, Location, Comment


# Категория
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("title", "slug", "is_published", "created_at")
    list_display_links = ("title",)
    search_fields = ("title", "slug", "description")
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ("is_published", "created_at")
    fieldsets = (
        (None, {"fields": ("title", "slug", "description")}),
        (
            "Параметры публикации",
            {"fields": ("is_published", "created_at"),
             "classes": ("collapse",)},
        ),
    )


# Локация
@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ("name", "is_published", "created_at")
    list_display_links = ("name",)
    search_fields = ("name",)
    list_filter = ("is_published", "created_at")
    fieldsets = (
        (None, {"fields": ("name",)}),
        (
            "Параметры публикации",
            {"fields": ("is_published", "created_at"),
             "classes": ("collapse",)},
        ),
    )


# Пост
@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "category",
        "location",
        "pub_date",
        "is_published",
        "created_at",
    )
    list_display_links = ("title",)
    search_fields = (
        "title",
        "text",
        "author__username",
        "category__title",
        "location__name",
    )
    list_filter = ("is_published",
                   "pub_date",
                   "category",
                   "location",
                   "author")
    list_editable = ("is_published",)
    readonly_fields = ("created_at",)
    fieldsets = (
        (None, {"fields": ("title", "text")}),
        ("Публикация", {"fields": ("pub_date", "author",
                                   "category", "location")}),
        (
            "Параметры",
            {"fields": ("is_published", "created_at"),
             "classes": ("collapse",)},
        ),
    )
    date_hierarchy = "pub_date"


# Комментарий
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "text",
        "author",
        "post",
        "created_at",
    )

    list_display_links = ("text",)

    search_fields = (
        "text",
        "author__username",
        "post__title",
    )

    list_filter = (
        "created_at",
        "author",
    )

    readonly_fields = ("created_at",)

    fieldsets = (
        (None, {"fields": ("text",)}),
        (
            "Связи",
            {
                "fields": (
                    "author",
                    "post",
                )
            },
        ),
        ("Дата создания", {"fields": ("created_at",),
                           "classes": ("collapse",)}),
    )

    date_hierarchy = "created_at"
