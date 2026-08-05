import time
from collections import defaultdict

from django.conf import settings
from django.db import IntegrityError, transaction
from django.db.models import Count, Max
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from accounts.models import User
from accounts.permissions import IsStaffRole, PasswordChanged
from tickets.models import Reply, ReplyStatus, Request, RequestStatus
from tickets.serializers import (
    ReplyCreateSerializer,
    ReplyDecisionSerializer,
    ReplySerializer,
    RequestCreateSerializer,
    RequestDetailSerializer,
    RequestListSerializer,
    StatusUpdateSerializer,
)

# --- защита публичной формы от спама -------------------------------------
_form_hits: dict[str, list[float]] = defaultdict(list)


def _form_allowed(ip: str) -> bool:
    now = time.monotonic()
    bucket = [t for t in _form_hits[ip] if t > now - 3600]
    bucket.append(now)
    _form_hits[ip] = bucket
    return len(bucket) <= settings.PUBLIC_FORM_MAX_PER_HOUR


def _detail_response(request_obj, http_request):
    serializer = RequestDetailSerializer(request_obj, context={"request": http_request})
    return Response(serializer.data)


# ---------------------------------------------------------------- публичное


@api_view(["GET", "POST"])
@permission_classes([AllowAny])
def request_root(request):
    """Один путь, два разных доступа.

    GET — список для авторизованных. POST — публичная форма с лендинга.
    Разделять их на разные URL незачем: это один ресурс.
    """
    if request.method == "POST":
        return create_request(request)

    if not (request.user.is_authenticated and not request.user.must_change_password):
        return Response(
            {"detail": "Требуется вход"}, status=status.HTTP_401_UNAUTHORIZED
        )
    return request_list(request)


def create_request(request):
    """Публичная форма с лендинга. Авторизация не требуется."""
    from accounts.views_auth import client_ip

    if not _form_allowed(client_ip(request)):
        return Response(
            {
                "detail": "Слишком много заявок с одного адреса. "
                          "Попробуйте через час или позвоните нам."
            },
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    serializer = RequestCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    obj = serializer.save()

    return Response(
        {
            "public_number": obj.public_number,
            "message": (
                f"Заявка №{obj.public_number} принята. "
                "Мы позвоним по указанному номеру в течение рабочего дня."
            ),
        },
        status=status.HTTP_201_CREATED,
    )


# ------------------------------------------------------------- авторизованное


def request_list(request):
    """Список заявок. Доступен всем авторизованным — участник должен
    видеть, на что можно откликнуться."""
    qs = Request.objects.annotate(responses_count=Count("replies"))

    params = request.query_params

    if params.get("status"):
        qs = qs.filter(status=params["status"])
    if params.get("service_type"):
        qs = qs.filter(service_type=params["service_type"])
    if params.get("mine") == "true":
        qs = qs.filter(assignee=request.user)

    if params.get("relevant") == "true":
        allowed = request.user.service_types
        # Пустое множество значит «у участника нет пометок с видом услуги».
        # Возвращаем ничего, а не всё: иначе фильтр «подходящие мне» молча
        # превращается в «все» и теряет смысл.
        if not allowed:
            return Response({"total": 0, "items": []})
        qs = qs.filter(service_type__in=allowed)

    total = qs.count()

    try:
        limit = min(int(params.get("limit", 20)), 100)
        offset = max(int(params.get("offset", 0)), 0)
    except ValueError:
        limit, offset = 20, 0

    items = qs[offset : offset + limit]
    return Response(
        {"total": total, "items": RequestListSerializer(items, many=True).data}
    )


@api_view(["GET"])
@permission_classes([IsAuthenticated, PasswordChanged])
def request_detail(request, request_id: int):
    obj = get_object_or_404(
        Request.objects.prefetch_related("replies__member__tags"), pk=request_id
    )
    return _detail_response(obj, request)


@api_view(["PATCH"])
@permission_classes([IsStaffRole, PasswordChanged])
def update_status(request, request_id: int):
    obj = get_object_or_404(Request, pk=request_id)

    serializer = StatusUpdateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    new_status = serializer.validated_data["status"]
    reason = serializer.validated_data.get("reject_reason") or ""

    if new_status not in RequestStatus.values:
        return Response({"detail": "Неизвестный статус"}, status=status.HTTP_400_BAD_REQUEST)

    if new_status == RequestStatus.REJECTED and not reason.strip():
        return Response(
            {"detail": "Укажите причину отклонения"}, status=status.HTTP_400_BAD_REQUEST
        )

    obj.status = new_status
    if new_status == RequestStatus.REJECTED:
        obj.reject_reason = reason
    obj.save(update_fields=["status", "reject_reason", "updated_at"])

    return _detail_response(obj, request)


@api_view(["PUT"])
@permission_classes([IsStaffRole, PasswordChanged])
def assign_member(request, request_id: int, member_id: int):
    """Назначение исполнителя вручную — когда на заявку никто не откликнулся.

    Без force не даём поставить человека, у которого нет пометки под этот
    вид услуги: назначить дизайнера на видеосъёмку почти всегда опечатка.
    """
    obj = get_object_or_404(Request, pk=request_id)
    member = get_object_or_404(User, pk=member_id, is_active=True)

    force = request.query_params.get("force") == "true"
    if not force and obj.service_type not in member.service_types:
        return Response(
            {
                "detail": f"У {member.full_name} нет пометки под этот вид услуги. "
                          f"Повторите с force=true, если назначаете сознательно."
            },
            status=status.HTTP_409_CONFLICT,
        )

    obj.assignee = member
    if obj.status == RequestStatus.NEW:
        obj.status = RequestStatus.IN_PROGRESS
    obj.save(update_fields=["assignee", "status", "updated_at"])

    return _detail_response(obj, request)


# ------------------------------------------------------------------ отклики


@api_view(["POST"])
@permission_classes([IsAuthenticated, PasswordChanged])
def create_reply(request, request_id: int):
    obj = get_object_or_404(Request, pk=request_id)

    if not obj.open_for_replies:
        return Response(
            {"detail": "Заявка закрыта для откликов"}, status=status.HTTP_409_CONFLICT
        )

    serializer = ReplyCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    try:
        reply = Reply.objects.create(
            request=obj, member=request.user, message=serializer.validated_data["message"]
        )
    except IntegrityError:
        # Дубли отсекает ограничение в базе: проверка в коде не спасает
        # от двух одновременных запросов
        return Response(
            {"detail": "Вы уже откликнулись на эту заявку"},
            status=status.HTTP_409_CONFLICT,
        )

    return Response(ReplySerializer(reply).data, status=status.HTTP_201_CREATED)


@api_view(["PATCH"])
@permission_classes([IsStaffRole, PasswordChanged])
def decide_reply(request, reply_id: int):
    """Принять или отклонить отклик. Решает контент-менеджер, а не
    первый успевший участник."""
    reply = get_object_or_404(Reply.objects.select_related("request"), pk=reply_id)

    serializer = ReplyDecisionSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    accept = serializer.validated_data["accept"]
    comment = serializer.validated_data.get("comment") or ""

    # Одна транзакция: иначе можно получить заявку с двумя принятыми откликами
    with transaction.atomic():
        reply.status = ReplyStatus.ACCEPTED if accept else ReplyStatus.DECLINED
        reply.decision_comment = comment
        reply.save(update_fields=["status", "decision_comment", "updated_at"])

        if accept:
            ticket = reply.request
            ticket.status = RequestStatus.IN_PROGRESS
            ticket.assignee_id = reply.member_id
            ticket.save(update_fields=["status", "assignee", "updated_at"])

            ticket.replies.filter(status=ReplyStatus.PENDING).exclude(pk=reply.pk).update(
                status=ReplyStatus.DECLINED,
                decision_comment="Выбран другой исполнитель",
            )

    reply.refresh_from_db()
    return Response(ReplySerializer(reply).data)
