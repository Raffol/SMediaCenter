from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, parser_classes, permission_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from accounts.permissions import IsStaffRole, PasswordChanged
from accounts.utils_images import save_cover
from posts.models import Post
from posts.serializers import PostDetailSerializer, PostListSerializer, PostWriteSerializer


def _page(request, qs):
    total = qs.count()
    try:
        limit = min(int(request.query_params.get("limit", 12)), 50)
        offset = max(int(request.query_params.get("offset", 0)), 0)
    except ValueError:
        limit, offset = 12, 0

    items = qs[offset : offset + limit]
    return Response(
        {
            "total": total,
            "items": PostListSerializer(items, many=True, context={"request": request}).data,
        }
    )


# ---------------------------------------------------------------- публичное


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def post_root(request):
    if request.method == "POST":
        if not (request.user.is_authenticated and request.user.is_content_staff):
            return Response({"detail": "Недостаточно прав"}, status=status.HTTP_403_FORBIDDEN)
        if request.user.must_change_password:
            return Response(
                {"detail": "Смените временный пароль, чтобы продолжить"},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = PostWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        post = serializer.save(author=request.user)
        return Response(
            PostDetailSerializer(post, context={"request": request}).data,
            status=status.HTTP_201_CREATED,
        )

    qs = Post.objects.filter(is_published=True)
    if request.query_params.get("category"):
        qs = qs.filter(category=request.query_params["category"])
    return _page(request, qs)


@api_view(["GET"])
@permission_classes([AllowAny])
def post_detail_public(request, slug: str):
    post = get_object_or_404(Post, slug=slug, is_published=True)
    return Response(PostDetailSerializer(post, context={"request": request}).data)


# ------------------------------------------------------------- для персонала


@api_view(["GET"])
@permission_classes([IsStaffRole, PasswordChanged])
def post_list_manage(request):
    """То же, что публичный список, но с черновиками."""
    qs = Post.objects.all()
    if request.query_params.get("category"):
        qs = qs.filter(category=request.query_params["category"])
    return _page(request, qs)


@api_view(["PATCH", "DELETE"])
@permission_classes([IsStaffRole, PasswordChanged])
def post_manage(request, post_id: int):
    post = get_object_or_404(Post, pk=post_id)

    if request.method == "DELETE":
        if post.cover:
            post.cover.delete(save=False)
        post.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    serializer = PostWriteSerializer(post, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(PostDetailSerializer(post, context={"request": request}).data)


@api_view(["PUT"])
@permission_classes([IsStaffRole, PasswordChanged])
@parser_classes([MultiPartParser])
def post_cover(request, post_id: int):
    post = get_object_or_404(Post, pk=post_id)

    upload = request.data.get("file")
    if upload is None:
        return Response({"detail": "Файл не передан"}, status=status.HTTP_400_BAD_REQUEST)

    save_cover(post, upload)
    return Response(PostDetailSerializer(post, context={"request": request}).data)
