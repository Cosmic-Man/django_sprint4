from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()  # User модель


class AbstractModel(models.Model):
    title = models.CharField(
        max_length=256, verbose_name="Заголовок", default="Без названия"
    )
    is_published = models.BooleanField(
        default=True,
        verbose_name="Опубликовано",
        help_text="Снимите галочку, чтобы скрыть публикацию.",
    )
    created_at = models.DateTimeField(auto_now_add=True,
                                      verbose_name="Добавлено")

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


# Тематическая категория
class Category(AbstractModel):
    description = models.TextField(verbose_name="Описание")
    slug = models.SlugField(
        unique=True,
        verbose_name="Идентификатор",
        help_text="Идентификатор страницы для URL; "
        "разрешены символы латиницы, цифры, дефис и подчёркивание.",
    )

    class Meta:
        verbose_name = "категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.description


# Географическая метка
class Location(AbstractModel):
    name = models.CharField(max_length=256, verbose_name="Название места")

    class Meta:
        verbose_name = "местоположение"
        verbose_name_plural = "Местоположения"

    def __str__(self):
        return self.name


# Публикация
class Post(AbstractModel):
    text = models.TextField(verbose_name="Текст")
    pub_date = models.DateTimeField(
        verbose_name="Дата и время публикации",
        help_text="Если установить дату и время в будущем — "
        "можно делать отложенные публикации.",
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Автор публикации",
        related_name="user",
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Местоположение",
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL,
        null=True, verbose_name="Категория"
    )
    image = models.ImageField(
        "Изображение", upload_to="posts_images/", blank=True, null=True
    )

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "Публикации"
        ordering = ["-pub_date"]

    def __str__(self):
        return self.title


# Комментарий
class Comment(models.Model):
    text = models.TextField("Текст комментария")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="comments", verbose_name="Автор"
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        related_name="comments", verbose_name="Пост"
    )
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"

    def __str__(self):
        return f"Комментарий от {self.author.username} к {self.post.title}"
