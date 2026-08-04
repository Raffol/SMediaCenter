from rest_framework import serializers

from accounts.serializers import UserSerializer
from posts.models import Post


class PostListSerializer(serializers.ModelSerializer):
    cover_thumb_path = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = [
            "id", "slug", "title", "excerpt", "category",
            "cover_thumb_path", "cover_alt", "published_at",
        ]

    def get_cover_thumb_path(self, obj) -> str | None:
        # Отдаём готовый URL: фронт подставляет его в src напрямую
        return obj.cover.url if obj.cover else None


class PostDetailSerializer(PostListSerializer):
    author = UserSerializer(read_only=True)
    cover_path = serializers.SerializerMethodField()

    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + [
            "body", "cover_path", "is_published", "author",
        ]

    def get_cover_path(self, obj) -> str | None:
        return obj.cover.url if obj.cover else None


class PostWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            "id", "title", "body", "excerpt", "category",
            "cover_alt", "is_published",
        ]
        extra_kwargs = {
            "title": {"min_length": 3},
            "body": {"min_length": 10},
        }
