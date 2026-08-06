"""Стартовые данные: администратор и четыре пометки.

    python manage.py seed

Идемпотентна: повторный запуск ничего не дублирует и не сбрасывает пароли.
"""

import secrets

from django.core.management.base import BaseCommand

from accounts.models import Role, ServiceType, Tag, User

TAGS = [
    ("Фотограф", ServiceType.PHOTO, "#E11D2E", 10),
    ("Видеограф", ServiceType.VIDEO, "#1D4ED8", 20),
    ("Автор", ServiceType.ARTICLE, "#047857", 30),
    ("Дизайнер", ServiceType.DESIGN, "#7C3AED", 40),
]


class Command(BaseCommand):
    help = "Создаёт администратора и пометки под виды услуг"

    def add_arguments(self, parser):
        parser.add_argument("--login", default="admin")

    def handle(self, *args, **options):
        login = options["login"]

        created_tags = []
        for name, service_type, color, order in TAGS:
            tag, created = Tag.objects.get_or_create(
                name=name,
                defaults={
                    "service_type": service_type,
                    "color": color,
                    "sort_order": order,
                    "is_public": True,
                },
            )
            if created:
                created_tags.append(name)

        if created_tags:
            self.stdout.write(f"Пометки созданы: {', '.join(created_tags)}")
        else:
            self.stdout.write("Пометки уже были на месте")

        if User.objects.filter(username=login).exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Пользователь «{login}» уже есть. Пароль не менялся — "
                    f"для сброса используйте действие в админке."
                )
            )
            return

        password = secrets.token_urlsafe(12)
        user = User(
            username=login,
            full_name="Администратор",
            role=Role.ADMIN,
            must_change_password=True,
            is_active=True,
        )
        user.set_password(password)
        user.save()

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Администратор создан"))
        self.stdout.write(f"  логин:  {login}")
        self.stdout.write(f"  пароль: {password}")
        self.stdout.write(
            "Пароль показан один раз. При первом входе система попросит его сменить."
        )
