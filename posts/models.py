from django.db import models
from django.utils import timezone

from accounts.models import make_slug


class PostCategory(models.TextChoices):
    NEWS = "news", "Новость"
    WORK = "work", "Работа в портфолио"


class Post(models.Model):
    """Новость или работа в портфолио.

    Одна модель на две сущности: две почти одинаковые таблицы с двумя
    наборами эндпоинтов дороже одного поля с выбором.
    """

    slug = models.SlugField("слаг", max_length=200, unique=True, blank=True)
    title = models.CharField("заголовок", max_length=200)
    excerpt = models.CharField(
        "короткое описание", max_length=300, blank=True,
        help_text="Для карточки в ленте. Пусто — возьмём начало текста.",
    )
    body = models.TextField("текст")
    category = models.CharField(
        "категория", max_length=16, choices=PostCategory.choices,
        default=PostCategory.NEWS, db_index=True,
    )

    cover = models.ImageField("обложка", upload_to="posts/", blank=True, null=True)
    cover_alt = models.CharField(
        "описание обложки", max_length=200, blank=True,
        help_text="Обязательно, если есть обложка: попадает в alt для скринридеров",
    )

    is_published = models.BooleanField("опубликована", default=False, db_index=True)
    published_at = models.DateTimeField("дата публикации", blank=True, null=True)

    author = models.ForeignKey(
        "accounts.User", verbose_name="автор", on_delete=models.SET_NULL,
        blank=True, null=True, related_name="posts",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "публикация"
        verbose_name_plural = "публикации"
        ordering = ["-published_at", "-id"]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = make_slug(self.title, 190)
            slug, n = base, 2
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{n}"
                n += 1
            self.slug = slug

        # published_at ставится один раз, при первой публикации — иначе
        # правка текста будет поднимать пост в ленте наверх
        if self.is_published and self.published_at is None:
            self.published_at = timezone.now()

        super().save(*args, **kwargs)
