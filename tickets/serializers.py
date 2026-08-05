import re
from datetime import date

from rest_framework import serializers

from accounts.serializers import UserSerializer
from tickets.models import Reply, Request

_DIGITS = re.compile(r"\D")


class ReplySerializer(serializers.ModelSerializer):
    member = UserSerializer(read_only=True)

    class Meta:
        model = Reply
        fields = ["id", "member", "message", "status", "decision_comment", "created_at"]


class RequestCreateSerializer(serializers.ModelSerializer):
    """Приходит с публичной формы, без авторизации."""

    class Meta:
        model = Request
        fields = [
            "client_name", "client_phone", "client_contact_extra",
            "service_type", "description", "event_date", "location",
        ]
        extra_kwargs = {
            "client_name": {"min_length": 2},
            "description": {"min_length": 10},
        }

    def validate_client_phone(self, value: str) -> str:
        digits = _DIGITS.sub("", value)
        if len(digits) == 11 and digits.startswith("8"):
            digits = "7" + digits[1:]
        if len(digits) != 11 or not digits.startswith("7"):
            raise serializers.ValidationError("Введите телефон в формате +7 999 123-45-67")
        return f"+{digits}"

    def validate_event_date(self, value):
        if value and value < date.today():
            raise serializers.ValidationError("Дата съёмки не может быть в прошлом")
        return value


class RequestListSerializer(serializers.ModelSerializer):
    """Карточка в списке: всё, что нужно видеть без открытия."""

    responses_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Request
        fields = [
            "id", "public_number", "client_name", "service_type",
            "status", "event_date", "created_at", "responses_count",
        ]


class RequestDetailSerializer(serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)
    responses = serializers.SerializerMethodField()
    my_response = serializers.SerializerMethodField()
    client_phone = serializers.SerializerMethodField()
    client_contact_extra = serializers.SerializerMethodField()

    class Meta:
        model = Request
        fields = [
            "id", "public_number", "client_name", "client_phone",
            "client_contact_extra", "service_type", "description",
            "event_date", "location", "status", "reject_reason",
            "created_at", "assignee", "responses", "my_response",
        ]

    def _viewer(self):
        return self.context["request"].user

    def _is_staff(self) -> bool:
        user = self._viewer()
        return user.is_authenticated and user.is_content_staff

    def get_responses(self, obj):
        # Персонал видит все отклики. Участник — только свой: видя чужие
        # предложения, люди начинают сравнивать себя друг с другом,
        # и это ссорит команду.
        if not self._is_staff():
            return []
        return ReplySerializer(obj.replies.all(), many=True).data

    def get_my_response(self, obj):
        if self._is_staff():
            return None
        mine = next((r for r in obj.replies.all() if r.member_id == self._viewer().id), None)
        return ReplySerializer(mine).data if mine else None

    def get_client_phone(self, obj) -> str:
        # Телефон открывается только персоналу и назначенному исполнителю
        if self._is_staff() or obj.assignee_id == self._viewer().id:
            return obj.client_phone
        return "скрыт до назначения"

    def get_client_contact_extra(self, obj) -> str | None:
        if self._is_staff() or obj.assignee_id == self._viewer().id:
            return obj.client_contact_extra or None
        return None


class ReplyCreateSerializer(serializers.Serializer):
    message = serializers.CharField(min_length=5, max_length=2000)


class ReplyDecisionSerializer(serializers.Serializer):
    accept = serializers.BooleanField()
    comment = serializers.CharField(
        max_length=500, required=False, allow_blank=True, allow_null=True
    )


class StatusUpdateSerializer(serializers.Serializer):
    status = serializers.CharField()
    reject_reason = serializers.CharField(
        max_length=500, required=False, allow_blank=True, allow_null=True
    )
