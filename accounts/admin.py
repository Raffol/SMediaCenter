import secrets

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html

from accounts.models import ROLE_LEVEL, Role, Tag, User


class RoleScopedAdmin(admin.ModelAdmin):
    """База для разделов, доступных персоналу.

    Удаление оставлено только администратору: контент-менеджер работает
    с содержимым, а не с необратимыми операциями.
    """

    def has_module_permission(self, request) -> bool:
        user = request.user
        return bool(user.is_authenticated and getattr(user, "is_content_staff", False))

    def has_view_permission(self, request, obj=None) -> bool:
        return self.has_module_permission(request)

    def has_add_permission(self, request) -> bool:
        return self.has_module_permission(request)

    def has_change_permission(self, request, obj=None) -> bool:
        return self.has_module_permission(request)

    def has_delete_permission(self, request, obj=None) -> bool:
        return getattr(request.user, "role", None) == Role.ADMIN


@admin.register(Tag)
class TagAdmin(RoleScopedAdmin):
    """Пометки — рабочий инструмент контент-менеджера, не системная настройка."""

    list_display = ["swatch", "name", "service_type", "is_public", "sort_order", "user_count"]
    list_editable = ["sort_order", "is_public"]
    list_filter = ["service_type", "is_public"]
    search_fields = ["name"]
    readonly_fields = ["slug"]
    fieldsets = [
        (None, {"fields": ["name", "slug", "description"]}),
        ("Подбор заявок", {
            "fields": ["service_type"],
            "description": "Пустое поле — пометка не участвует в подборе исполнителей.",
        }),
        ("Отображение", {"fields": ["color", "is_public", "sort_order"]}),
    ]

    @admin.display(description="")
    def swatch(self, obj):
        return format_html(
            '<span style="display:inline-block;width:14px;height:14px;'
            'border-radius:3px;background:{}"></span>',
            obj.color,
        )

    @admin.display(description="участников")
    def user_count(self, obj):
        return obj.users.count()


@admin.register(User)
class UserAdmin(BaseUserAdmin, RoleScopedAdmin):
    """Управление аккаунтами — только администратор.

    Поля is_staff и is_superuser здесь отсутствуют: они выводятся из роли
    в User.save(). Иначе роль и права разъезжаются, и понижённый до
    участника человек остаётся в админке.
    """

    list_display = ["username", "full_name", "role", "tag_list", "is_active", "must_change_password"]
    list_filter = ["role", "is_active", "must_change_password", "tags"]
    search_fields = ["username", "full_name", "email"]
    filter_horizontal = ["tags"]
    actions = ["reset_password"]

    fieldsets = [
        (None, {"fields": ["username", "password"]}),
        ("Профиль", {"fields": ["full_name", "email", "phone", "bio", "avatar"]}),
        ("Роль и пометки", {"fields": ["role", "tags"]}),
        ("Доступ", {"fields": ["is_active", "must_change_password", "is_public"]}),
        ("Даты", {"fields": ["last_login", "date_joined"], "classes": ["collapse"]}),
    ]

    add_fieldsets = [
        (None, {
            "fields": ["username", "full_name", "role"],
            "description": "Временный пароль сгенерируется автоматически "
                           "и будет показан один раз после сохранения.",
        }),
        ("Пометки", {"fields": ["tags"]}),
    ]

    def has_module_permission(self, request) -> bool:
        return getattr(request.user, "role", None) == Role.ADMIN

    has_view_permission = has_module_permission
    has_add_permission = has_module_permission

    def has_change_permission(self, request, obj=None) -> bool:
        return self.has_module_permission(request)

    def get_form(self, request, obj=None, **kwargs):
        # При создании пароль не спрашиваем — генерируем сами
        if obj is None:
            kwargs["fields"] = ["username", "full_name", "role", "tags"]
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        if not change:
            temp = secrets.token_urlsafe(9)
            obj.set_password(temp)
            obj.must_change_password = True
            # Показываем один раз: SMTP в локальной сети нет,
            # передавать придётся лично
            messages.warning(
                request,
                f"Временный пароль для «{obj.username}»: {temp} — "
                f"запишите сейчас, второй раз не покажем.",
            )
        super().save_model(request, obj, form, change)

    @admin.display(description="пометки")
    def tag_list(self, obj):
        names = [t.name for t in obj.tags.all()[:3]]
        extra = obj.tags.count() - len(names)
        text = ", ".join(names) or "—"
        return f"{text} +{extra}" if extra > 0 else text

    @admin.action(description="Сбросить пароль")
    def reset_password(self, request, queryset):
        if getattr(request.user, "role", None) != Role.ADMIN:
            self.message_user(request, "Недостаточно прав", level=messages.ERROR)
            return

        pairs = []
        for user in queryset:
            temp = secrets.token_urlsafe(9)
            user.set_password(temp)
            user.must_change_password = True
            user.save()
            pairs.append(f"{user.username}: {temp}")

        self.message_user(
            request,
            "Новые пароли (запишите, второй раз не покажем) — " + "; ".join(pairs),
            level=messages.WARNING,
        )
