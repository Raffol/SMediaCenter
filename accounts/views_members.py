from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from accounts.permissions import IsStaffRole, PasswordChanged
from accounts.serializers import MeSerializer, MemberCardSerializer, ProfileUpdateSerializer
from accounts.utils_images import save_avatar
from posts.models import PostCategory
from posts.serializers import PostListSerializer
from tickets.models import RequestStatus


@api_view(["GET"])
@permission_classes([AllowAny])
def member_list(request):
    """Секция «Штатники»."""
    members = User.objects.filter(is_active=True, is_public=True).prefetch_related("tags")

    tag_slug = request.query_params.get("tag")
    data = []
    for member in members:
        visible = member.public_tags
        if tag_slug and not any(t.slug == tag_slug for t in visible):
            continue
        data.append(MemberCardSerializer(member).data)

    return Response(data)


@api_view(["GET"])
@permission_classes([AllowAny])
def member_detail(request, user_id: int):
    member = get_object_or_404(
        User.objects.prefetch_related("tags"),
        pk=user_id, is_active=True, is_public=True,
    )

    works = member.posts.filter(is_published=True, category=PostCategory.WORK)[:12]
    completed = member.assigned_requests.filter(status=RequestStatus.DONE).count()

    data = MemberCardSerializer(member).data
    data["works"] = PostListSerializer(works, many=True, context={"request": request}).data
    data["completed_count"] = completed
    return Response(data)


@api_view(["PATCH"])
@permission_classes([IsAuthenticated, PasswordChanged])
def update_my_profile(request):
    serializer = ProfileUpdateSerializer(request.user, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(MeSerializer(request.user).data)


@api_view(["PUT"])
@permission_classes([IsAuthenticated, PasswordChanged])
@parser_classes([MultiPartParser])
def upload_my_avatar(request):
    upload = request.data.get("file")
    if upload is None:
        return Response({"detail": "Файл не передан"}, status=400)

    save_avatar(request.user, upload)
    return Response(MeSerializer(request.user).data)


@api_view(["GET"])
@permission_classes([IsStaffRole])
def member_list_manage(request):
    """Со скрытыми участниками и скрытыми пометками — для назначения
    исполнителей и управления командой."""
    members = User.objects.filter(is_active=True).prefetch_related("tags")
    return Response(
        MemberCardSerializer(
            members, many=True, context={"show_hidden": True}
        ).data
    )
