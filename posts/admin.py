from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from accounts.admin import RoleScopedAdmin
from posts.models import Post


@admin.register(Post)
class PostAdmin(RoleScopedAdmin):
    list_display = ["thumb", "title", "category", "is_published", "published_at", "author"]
    list_filter = ["category", "is_published", "published_at"]
    search_fields = ["title", "body"]
    readonly_fields = ["slug", "published_at", "created_at", "updated_at", "preview"]
    actions = ["publish", "unpublish"]

    fieldsets = [
        (None, {"fields": ["title", "slug", "category"]}),
        ("Содержание", {"fields": ["excerpt", "body"]}),
        ("Обложка", {
            "fields": ["cover", "cover_alt", "preview"],
            "description": "Описание обязательно, если есть обложка: "
                           "оно попадает в alt для скринридеров.",
        }),
        ("Публикация", {"fields": ["is_published", "published_at", "author"]}),
        ("Даты", {"fields": ["created_at", "updated_at"], "classes": ["collapse"]}),
    ]

    @admin.display(description="")
    def thumb(self, obj):
        if not obj.cover:
            return "—"
        return format_html(
            '<img src="{}" style="height:34px;border-radius:3px" alt="">', obj.cover.url
        )

    @admin.display(description="просмотр")
    def preview(self, obj):
        if not obj.cover:
            return "Обложка не загружена"
        return format_html(
            '<img src="{}" style="max-width:340px;border-radius:6px" alt="{}">',
            obj.cover.url, obj.cover_alt or obj.title,
        )

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)

    @admin.action(description="Опубликовать")
    def publish(self, request, queryset):
        count = 0
        for post in queryset:
            post.is_published = True
            if post.published_at is None:
                post.published_at = timezone.now()
            post.save()
            count += 1
        self.message_user(request, f"Опубликовано: {count}")

    @admin.action(description="Снять с публикации")
    def unpublish(self, request, queryset):
        updated = queryset.update(is_published=False)
        self.message_user(request, f"Снято с публикации: {updated}")
