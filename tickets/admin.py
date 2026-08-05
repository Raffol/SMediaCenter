from django.contrib import admin
from django.utils import timezone

from accounts.admin import RoleScopedAdmin
from tickets.models import Reply, ReplyStatus, Request, RequestStatus


class ReplyInline(admin.TabularInline):
    """Отклики прямо внутри страницы заявки.

    Это то, чего не хватало в Starlette-Admin: там связанные объекты
    правились только отдельным разделом с фильтром.
    """

    model = Reply
    extra = 0
    fields = ["member", "message", "status", "decision_comment", "created_at"]
    readonly_fields = ["member", "message", "created_at"]
    can_delete = False

    def has_add_permission(self, request, obj=None) -> bool:
        # Отклик оставляет участник через сайт, а не персонал в админке
        return False


@admin.register(Request)
class RequestAdmin(RoleScopedAdmin):
    list_display = [
        "public_number", "client_name", "service_type", "status",
        "event_date", "reply_count", "assignee", "created_at",
    ]
    list_filter = ["status", "service_type", "created_at"]
    search_fields = ["public_number", "client_name", "client_phone"]
    date_hierarchy = "created_at"
    readonly_fields = ["public_number", "created_at", "updated_at"]
    inlines = [ReplyInline]
    actions = ["mark_done", "mark_in_progress"]

    fieldsets = [
        (None, {"fields": ["public_number", "status", "assignee"]}),
        ("Клиент", {"fields": ["client_name", "client_phone", "client_contact_extra"]}),
        ("Задача", {"fields": ["service_type", "description", "event_date", "location"]}),
        ("Отклонение", {"fields": ["reject_reason"], "classes": ["collapse"]}),
        ("Даты", {"fields": ["created_at", "updated_at"], "classes": ["collapse"]}),
    ]

    def has_add_permission(self, request) -> bool:
        # Заявки приходят с публичной формы. Ручное создание ломает
        # нумерацию и контакты — не даём.
        return False

    @admin.display(description="откликов")
    def reply_count(self, obj):
        return obj.replies.count()

    @admin.action(description="Отметить выполненными")
    def mark_done(self, request, queryset):
        updated = queryset.update(status=RequestStatus.DONE, updated_at=timezone.now())
        self.message_user(request, f"Обновлено заявок: {updated}")

    @admin.action(description="Вернуть в работу")
    def mark_in_progress(self, request, queryset):
        updated = queryset.update(status=RequestStatus.IN_PROGRESS, updated_at=timezone.now())
        self.message_user(request, f"Обновлено заявок: {updated}")


@admin.register(Reply)
class ReplyAdmin(RoleScopedAdmin):
    list_display = ["id", "request", "member", "status", "created_at"]
    list_filter = ["status", "created_at"]
    search_fields = ["member__full_name", "request__public_number"]
    readonly_fields = ["request", "member", "message", "created_at"]

    def has_add_permission(self, request) -> bool:
        return False
