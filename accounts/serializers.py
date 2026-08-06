import re

from rest_framework import serializers

from accounts.models import Tag, User

_HEX = re.compile(r"^#[0-9a-fA-F]{6}$")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "slug", "service_type", "color", "description"]
        read_only_fields = ["slug"]


class TagWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = [
            "id", "name", "service_type", "color", "description",
            "is_public", "sort_order",
        ]

    def validate_color(self, value: str) -> str:
        if not _HEX.match(value):
            raise serializers.ValidationError("Цвет указывается в виде #RRGGBB, например #E11D2E")
        return value.upper()


class UserSerializer(serializers.ModelSerializer):
    """Публичный профиль. Пароля здесь нет и быть не должно."""

    login = serializers.CharField(source="username", read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    avatar_path = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "login", "full_name", "role", "bio", "avatar_path", "tags"]

    def get_avatar_path(self, obj) -> str | None:
        return obj.avatar.url if obj.avatar else None


class MeSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ["email", "phone", "must_change_password"]


class MemberCardSerializer(serializers.ModelSerializer):
    tags = serializers.SerializerMethodField()
    avatar_path = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "full_name", "bio", "avatar_path", "tags"]

    def get_tags(self, obj):
        # Скрытые пометки наружу не отдаём
        source = obj.tags.all() if self.context.get("show_hidden") else obj.public_tags
        return TagSerializer(source, many=True).data

    def get_avatar_path(self, obj) -> str | None:
        return obj.avatar.url if obj.avatar else None


class LoginSerializer(serializers.Serializer):
    login = serializers.CharField(max_length=64)
    password = serializers.CharField(max_length=128, write_only=True)
    remember = serializers.BooleanField(default=False)


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(max_length=128, write_only=True)
    new_password = serializers.CharField(min_length=8, max_length=128, write_only=True)


class ProfileUpdateSerializer(serializers.ModelSerializer):
    """Что участник может править у себя сам.

    Роли и пометок здесь нет намеренно: иначе любой выдаст себе пометку
    и доступ к чужим заявкам.
    """

    class Meta:
        model = User
        fields = ["full_name", "email", "phone", "bio"]


class TagAssignSerializer(serializers.Serializer):
    tag_ids = serializers.ListField(child=serializers.IntegerField(), allow_empty=True)
