from django.db import models

from accounts.models import ServiceType


class RequestStatus(models.TextChoices):
    NEW = "new", "Новая"
    IN_PROGRESS = "in_progress", "В работе"
    DONE = "done", "Выполнена"
    REJECTED = "rejected", "Отклонена"


class ReplyStatus(models.TextChoices):
    PENDING = "pending", "Ждёт решения"
    ACCEPTED = "accepted", "Принят"
    DECLINED = "declined", "Отклонён"


class Request(models.Model):
    """Заявка от внешнего клиента.

    Клиент аккаунта не имеет, поэтому связи с автором нет — вместо неё
    контактные данные. Публичный номер отдаётся клиенту на экране успеха,
    по нему он ссылается при звонке.
    """

    public_number = models.PositiveIntegerField("номер", unique=True, db_index=True)

    client_name = models.CharField("имя клиента", max_length=160)
    client_phone = models.CharField("телефон", max_length=32)
    client_contact_extra = models.CharField("другая связь", max_length=160, blank=True)

    service_type = models.CharField("вид услуги", max_length=16, choices=ServiceType.choices)
    description = models.TextField("задача")
    event_date = models.DateField("дата съёмки", blank=True, null=True)
    location = models.CharField("место", max_length=255, blank=True)

    status = models.CharField(
        "статус", max_length=16, choices=RequestStatus.choices,
        default=RequestStatus.NEW, db_index=True,
    )
    assignee = models.ForeignKey(
        "accounts.User", verbose_name="исполнитель", on_delete=models.SET_NULL,
        blank=True, null=True, related_name="assigned_requests",
    )
    reject_reason = models.CharField("причина отклонения", max_length=500, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "заявка"
        verbose_name_plural = "заявки"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"№{self.public_number} — {self.client_name}"

    def save(self, *args, **kwargs):
        if not self.public_number:
            # Сквозная нумерация с 1. Не id: у него бывают дыры от
            # удалённых записей, а клиенту нужен понятный номер.
            last = Request.objects.aggregate(models.Max("public_number"))["public_number__max"]
            self.public_number = (last or 0) + 1
        super().save(*args, **kwargs)

    @property
    def open_for_replies(self) -> bool:
        return self.status in (RequestStatus.NEW, RequestStatus.IN_PROGRESS)


class Reply(models.Model):
    """Отклик участника на заявку.

    Ответ на отклик — не отдельная сущность, а поля status и
    decision_comment. Отдельная таблица понадобилась бы только для
    переписки из нескольких сообщений; здесь решение принимается один раз.
    """

    request = models.ForeignKey(
        Request, verbose_name="заявка", on_delete=models.CASCADE, related_name="replies"
    )
    member = models.ForeignKey(
        "accounts.User", verbose_name="участник", on_delete=models.CASCADE,
        related_name="replies",
    )
    message = models.TextField("сообщение")
    status = models.CharField(
        "статус", max_length=16, choices=ReplyStatus.choices, default=ReplyStatus.PENDING
    )
    decision_comment = models.CharField("комментарий к решению", max_length=500, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "отклик"
        verbose_name_plural = "отклики"
        ordering = ["created_at"]
        constraints = [
            # Один участник — один отклик на заявку. Проверка в коде не
            # спасает от двух одновременных запросов, а ограничение в базе спасает.
            models.UniqueConstraint(
                fields=["request", "member"], name="uq_reply_request_member"
            )
        ]

    def __str__(self) -> str:
        return f"Отклик #{self.pk}"
