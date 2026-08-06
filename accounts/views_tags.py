from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from accounts.models import Tag, User
from accounts.permissions import IsStaffRole, PasswordChanged
from accounts.serializers import (
    TagAssignSerializer,
    TagSerializer,
    TagWriteSerializer,
    UserSerializer,
)


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def tag_list(request):
    if request.method == "GET":
        # Публичный список — нужен фильтру на странице «Команда»
        tags = Tag.objects.filter(is_public=True)
        return Response(TagSerializer(tags, many=True).data)

    # POST требует прав персонала — проверяем вручную, потому что
    # у метода GET права другие
    if not (request.user.is_authenticated and request.user.is_content_staff):
        return Response({"detail": "Недостаточно прав"}, status=status.HTTP_403_FORBIDDEN)

    serializer = TagWriteSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
@permission_classes([IsStaffRole])
def tag_list_manage(request):
    """Со скрытыми пометками."""
    return Response(TagSerializer(Tag.objects.all(), many=True).data)


@api_view(["PATCH", "DELETE"])
@permission_classes([IsStaffRole])
def tag_detail(request, tag_id: int):
    tag = get_object_or_404(Tag, pk=tag_id)

    if request.method == "PATCH":
        serializer = TagWriteSerializer(tag, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        if "name" in serializer.validated_data:
            from accounts.models import make_slug

            tag.slug = make_slug(serializer.validated_data["name"], 64)
        serializer.save(slug=tag.slug)
        return Response(serializer.data)

    # Удаление присвоенной пометки — почти всегда ошибка.
    # Без force сначала сообщаем, у скольких человек она стоит.
    used_by = tag.users.count()
    if used_by and request.query_params.get("force") != "true":
        return Response(
            {
                "detail": f"Пометка стоит у {used_by} участников. "
                          f"Повторите с force=true, чтобы удалить её у всех."
            },
            status=status.HTTP_409_CONFLICT,
        )

    tag.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["PUT"])
@permission_classes([IsStaffRole])
def assign_tags(request, user_id: int):
    """Полная замена набора пометок у участника.

    Именно замена, а не добавление: контент-менеджер видит перед собой
    итоговый список галочек и ожидает, что сохранится именно он.
    """
    target = get_object_or_404(User, pk=user_id)

    serializer = TagAssignSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    ids = serializer.validated_data["tag_ids"]

    known = set(Tag.objects.filter(id__in=ids).values_list("id", flat=True))
    unknown = set(ids) - known
    if unknown:
        return Response(
            {"detail": f"Неизвестные пометки: {sorted(unknown)}"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    target.tags.set(known)
    return Response(UserSerializer(target).data)


@api_view(["GET"])
@permission_classes([IsAuthenticated, PasswordChanged])
def my_service_types(request):
    """Что участник может брать по своим пометкам. Фронт показывает это
    в пустом состоянии, если подходящих заявок нет."""
    return Response(sorted(request.user.service_types))
