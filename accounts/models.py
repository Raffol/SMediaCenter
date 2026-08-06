from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.text import slugify


class Role(models.TextChoices):
    ADMIN = "admin", "Администратор"
    CONTENT_MANAGER = "content_manager", "Контент-менеджер"
    MEMBER = "member", "Участник"


# Числовой уровень — чтобы не писать `role in (ADMIN, CONTENT_MANAGER)`
# в двадцати местах. Больше = больше прав.
ROLE_LEVEL = {
    Role.MEMBER: 10,
    Role.CONTENT_MANAGER: 20,
    Role.ADMIN: 30,
}


class ServiceType(models.TextChoices):
    """Виды услуг. Совпадают с секцией «Чем мы занимаемся» на лендинге."""

    PHOTO = "photo", "Фотосъёмка"
    VIDEO = "video", "Видеосъёмка"
    ARTICLE = "article", "Написание статей"
    DESIGN = "design", "Дизайн"


def transliterate(text: str) -> str:
    table = {
        "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "е": "e", "ё": "e",
        "ж": "zh", "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m",
        "н": "n", "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u",
        "ф": "f", "х": "h", "ц": "c", "ч": "ch", "ш": "sh", "щ": "sch",
        "ъ": "", "ы": "y", "ь": "", "э": "e", "ю": "yu", "я": "ya",
    }
    return "".join(table.get(ch, ch) for ch in text.lower())


def make_slug(text: str, limit: int = 180) -> str:
    # slugify Django выбрасывает кириллицу целиком, поэтому сначала
    # транслитерация — иначе «Фотограф» превратится в пустую строку
    return slugify(transliterate(text))[:limit] or "item"


class Tag(models.Model):
    """Пометка участника: «фотограф», «монтажёр», «первый курс».

    service_type связывает пометку с видом услуги: заявка на фотосъёмку
    показывается людям с пометкой, у которой service_type = photo.
    Пометки без service_type (курс, статус) на подбор не влияют.
    """

    name = models.CharField("название", max_length=64, unique=True)
    slug = models.SlugField("слаг", max_length=64, unique=True, blank=True)
    service_type = models.CharField(
        "вид услуги",
        max_length=16,
        choices=ServiceType.choices,
        blank=True,
        null=True,
        db_index=True,
        help_text="Пустое — пометка не участвует в подборе заявок",
    )
    color = models.CharField(
        "цвет", max_length=7, default="#E11D2E",
        help_text="В виде #RRGGBB. Меняется здесь, без правки кода.",
    )
    description = models.CharField("описание", max_length=200, blank=True)
    is_public = models.BooleanField(
        "показывать в профиле", default=True,
        help_text="Скрытая пометка работает для подбора, но не видна на сайте",
    )
    sort_order = models.PositiveIntegerField("порядок", default=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "пометка"
        verbose_name_plural = "пометки"
        ordering = ["sort_order", "name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = make_slug(self.name, 64)
        super().save(*args, **kwargs)


class User(AbstractUser):
    """Штатник медиацентра.

    Открытой регистрации нет: аккаунты создаёт админ или контент-менеджер
    в админке, выдаёт временный пароль, при первом входе система требует
    его сменить.
    """

    full_name = models.CharField("ФИО", max_length=160)
    phone = models.CharField("телефон", max_length=32, blank=True)
    role = models.CharField(
        "роль", max_length=32, choices=Role.choices, default=Role.MEMBER
    )
    must_change_password = models.BooleanField(
        "требовать смену пароля", default=True,
        help_text="Ставится при создании аккаунта и при сбросе пароля",
    )
    is_public = models.BooleanField(
        "показывать в «Штатниках»", default=True
    )
    bio = models.TextField("о себе", max_length=500, blank=True)
    avatar = models.ImageField("аватар", upload_to="avatars/", blank=True, null=True)
    tags = models.ManyToManyField(Tag, verbose_name="пометки", blank=True, related_name="users")

    # first_name/last_name из AbstractUser не используются — есть full_name
    first_name = None
    last_name = None

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"
        ordering = ["full_name"]

    def __str__(self) -> str:
        return f"{self.full_name or self.username} ({self.username})"

    def save(self, *args, **kwargs):
        # Доступ в админку выводится из роли, а не ставится галочками
        # вручную: иначе роль и права разъезжаются, и человек с ролью
        # «участник» остаётся в админке после понижения.
        self.is_staff = ROLE_LEVEL[self.role] >= ROLE_LEVEL[Role.CONTENT_MANAGER]
        self.is_superuser = self.role == Role.ADMIN
        if not self.full_name:
            self.full_name = self.username
        super().save(*args, **kwargs)

    @property
    def level(self) -> int:
        return ROLE_LEVEL.get(self.role, 0)

    @property
    def is_content_staff(self) -> bool:
        return self.level >= ROLE_LEVEL[Role.CONTENT_MANAGER]

    @property
    def service_types(self) -> set[str]:
        """Виды услуг, которые участник может брать, по его пометкам."""
        return {t.service_type for t in self.tags.all() if t.service_type}

    @property
    def public_tags(self):
        return [t for t in self.tags.all() if t.is_public]
