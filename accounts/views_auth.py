import time
from collections import defaultdict

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import ensure_csrf_cookie
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from accounts.serializers import ChangePasswordSerializer, LoginSerializer, MeSerializer

# Один текст на все неудачи входа. Разные сообщения подсказали бы,
# какой логин существует, — это готовый список для перебора.
INVALID_CREDENTIALS = "Неверный логин или пароль"


# ---------------------------------------------------- ограничение попыток
#
# Счётчики в памяти процесса. Этого достаточно для одного воркера и
# пятнадцати пользователей. При нескольких воркерах счётчики разъедутся —
# тогда переносите в кеш Django (settings.CACHES) с тем же интерфейсом.

_attempts: dict[str, list[float]] = defaultdict(list)


def _hit(key: str, window: int) -> int:
    now = time.monotonic()
    bucket = [t for t in _attempts[key] if t > now - window]
    bucket.append(now)
    _attempts[key] = bucket
    return len(bucket)


def _count(key: str, window: int) -> int:
    now = time.monotonic()
    return len([t for t in _attempts[key] if t > now - window])


def client_ip(request) -> str:
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "unknown")


def _is_locked(ip: str, login_name: str) -> bool:
    window = settings.LOGIN_LOCKOUT_SECONDS
    limit = settings.LOGIN_MAX_ATTEMPTS
    return any(
        _count(k, window) >= limit
        for k in (f"ip:{ip}", f"user:{login_name.lower()}")
    )


# ------------------------------------------------------------------ вьюхи


@api_view(["GET"])
@permission_classes([AllowAny])
@ensure_csrf_cookie
def csrf(request):
    """Ставит cookie csrftoken.

    SPA вызывает это один раз при загрузке: без токена Django отклонит
    любой POST с ошибкой 403. axios подхватит cookie автоматически, если
    в нём заданы xsrfCookieName и xsrfHeaderName.
    """
    return Response({"detail": "ok"})


@api_view(["POST"])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    ip = client_ip(request)
    login_name = data["login"].strip()

    if _is_locked(ip, login_name):
        return Response(
            {"detail": "Слишком много попыток входа. Подождите пять минут."},
            status=status.HTTP_429_TOO_MANY_REQUESTS,
        )

    # authenticate сам выравнивает время ответа при отсутствующем
    # пользователе — прогоняет хеширование против заглушки
    user = authenticate(request, username=login_name, password=data["password"])

    if user is None or not user.is_active:
        _hit(f"ip:{ip}", settings.LOGIN_LOCKOUT_SECONDS)
        _hit(f"user:{login_name.lower()}", settings.LOGIN_LOCKOUT_SECONDS)
        return Response(
            {"detail": INVALID_CREDENTIALS}, status=status.HTTP_401_UNAUTHORIZED
        )

    _attempts.pop(f"ip:{ip}", None)
    _attempts.pop(f"user:{login_name.lower()}", None)

    login(request, user)

    if data["remember"]:
        request.session.set_expiry(60 * 60 * 24 * 30)
    else:
        request.session.set_expiry(settings.SESSION_COOKIE_AGE)

    return Response(MeSerializer(user).data)


@api_view(["POST"])
@permission_classes([AllowAny])
def logout_view(request):
    logout(request)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    # Намеренно без PasswordChanged: фронту нужно прочитать
    # must_change_password, чтобы отправить человека на смену пароля
    return Response(MeSerializer(request.user).data)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def change_password(request):
    serializer = ChangePasswordSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    data = serializer.validated_data

    user = request.user

    if not user.check_password(data["current_password"]):
        return Response(
            {"detail": "Текущий пароль указан неверно"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if data["new_password"] == data["current_password"]:
        return Response(
            {"detail": "Новый пароль совпадает с текущим"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError

    try:
        validate_password(data["new_password"], user)
    except ValidationError as exc:
        return Response({"detail": " ".join(exc.messages)}, status=status.HTTP_400_BAD_REQUEST)

    user.set_password(data["new_password"])
    user.must_change_password = False
    user.save(update_fields=["password", "must_change_password", "is_staff", "is_superuser"])

    # Смена пароля инвалидирует сессию — переустанавливаем, чтобы
    # человека не выкинуло сразу после успешной операции
    from django.contrib.auth import update_session_auth_hash

    update_session_auth_hash(request, user)

    return Response(status=status.HTTP_204_NO_CONTENT)
