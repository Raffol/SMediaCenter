from rest_framework.permissions import BasePermission

from accounts.models import ROLE_LEVEL, Role


class IsStaffRole(BasePermission):
    """Контент-менеджер или админ."""

    message = "Недостаточно прав"

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and ROLE_LEVEL.get(user.role, 0) >= ROLE_LEVEL[Role.CONTENT_MANAGER]
        )


class IsAdminRole(BasePermission):
    message = "Действие доступно только администратору"

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and user.role == Role.ADMIN)


class PasswordChanged(BasePermission):
    """Пользователь сменил временный пароль.

    Все рабочие эндпоинты используют это право: иначе человек с временным
    паролем сможет работать в обход экрана смены.
    """

    message = "Смените временный пароль, чтобы продолжить"

    def has_permission(self, request, view) -> bool:
        user = request.user
        return bool(user and user.is_authenticated and not user.must_change_password)
