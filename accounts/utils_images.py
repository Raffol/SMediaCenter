"""Обработка загруженных изображений.

Формат определяется по содержимому через Pillow, а не по расширению или
заголовку Content-Type: и то, и другое подделывается.
"""

import secrets
from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, UnidentifiedImageError
from rest_framework.exceptions import ValidationError

MAX_DIMENSION = 2400   # большие фото уменьшаем, иначе лендинг грузится минуту
THUMB_SIZE = (600, 400)
AVATAR_SIZE = 400


def _open_checked(upload) -> Image.Image:
    raw = upload.read()

    if len(raw) > settings.MAX_UPLOAD_BYTES:
        limit = settings.MAX_UPLOAD_BYTES // (1024 * 1024)
        raise ValidationError(f"Файл больше {limit} МБ. Уменьшите размер и попробуйте снова.")

    try:
        probe = Image.open(BytesIO(raw))
        probe.verify()                    # проверка целостности
        image = Image.open(BytesIO(raw))  # verify закрывает файл, открываем заново
    except (UnidentifiedImageError, OSError):
        raise ValidationError(
            "Не удалось прочитать изображение. Подойдут JPEG, PNG или WebP."
        ) from None

    if Image.MIME.get(image.format or "") not in settings.ALLOWED_IMAGE_TYPES:
        raise ValidationError("Подойдут только JPEG, PNG или WebP.")

    if image.mode in ("RGBA", "P", "LA"):
        image = image.convert("RGB")

    return image


def _to_webp(image: Image.Image, quality: int = 85) -> ContentFile:
    buffer = BytesIO()
    image.save(buffer, "WEBP", quality=quality, method=6)
    return ContentFile(buffer.getvalue())


def save_cover(post, upload) -> None:
    """Обложка публикации. Оригинал уменьшается, превью кладётся рядом."""
    image = _open_checked(upload)
    stem = secrets.token_hex(12)

    full = image.copy()
    full.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)

    old = post.cover.name if post.cover else None
    post.cover.save(f"{stem}.webp", _to_webp(full), save=False)
    post.save(update_fields=["cover", "updated_at"])

    # Старый файл удаляем только после успешного сохранения нового
    if old:
        post.cover.storage.delete(old)


def save_avatar(user, upload) -> None:
    """Аватар кропается в квадрат по центру — иначе в круглой рамке
    на фронте портрет обрежется как попало."""
    image = _open_checked(upload)

    side = min(image.size)
    left = (image.width - side) // 2
    top = (image.height - side) // 2
    square = image.crop((left, top, left + side, top + side))
    square = square.resize((AVATAR_SIZE, AVATAR_SIZE), Image.LANCZOS)

    old = user.avatar.name if user.avatar else None
    user.avatar.save(f"{secrets.token_hex(12)}.webp", _to_webp(square), save=False)
    user.save(update_fields=["avatar", "is_staff", "is_superuser"])

    if old:
        user.avatar.storage.delete(old)
