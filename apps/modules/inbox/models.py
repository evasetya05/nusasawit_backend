from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import Employee

User = get_user_model()


def _callable_attr(obj, name, default=False):
    """Helper to safely evaluate callable boolean attributes."""
    attr = getattr(obj, name, default)
    return attr() if callable(attr) else attr


class ChatThread(models.Model):
    """Thread that connects one admin/owner with a supervisor."""

    admin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="inbox_threads",
        limit_choices_to={"is_staff": True},
        help_text="Admin/owner participant",
    )
    supervisor = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        related_name="inbox_threads",
        help_text="Supervisor (employee with subordinates)",
    )
    subject = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["admin", "supervisor"],
                name="unique_admin_supervisor_thread",
            )
        ]

    def __str__(self):
        return f"Thread {self.pk} - {self.supervisor.name if self.supervisor else 'N/A'}"

    def clean(self):
        if self.supervisor and not self.supervisor.subordinates.exists():
            raise ValidationError("Supervisor must have at least one subordinate.")

    @property
    def supervisor_display(self):
        return self.supervisor.name if self.supervisor else "-"


class ChatMessage(models.Model):
    """Individual chat messages inside a thread."""

    thread = models.ForeignKey(
        ChatThread,
        on_delete=models.CASCADE,
        related_name="messages",
    )
    sender_admin = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="sent_admin_messages",
        limit_choices_to={"is_staff": True},
    )
    sender_supervisor = models.ForeignKey(
        Employee,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="sent_supervisor_messages",
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message {self.pk} in thread {self.thread_id}"

    def clean(self):
        if bool(self.sender_admin) == bool(self.sender_supervisor):
            raise ValidationError("Message must have exactly one sender (admin or supervisor).")

    @property
    def sender_label(self):
        if self.sender_admin:
            return self.sender_admin.get_full_name() or self.sender_admin.get_username()
        if self.sender_supervisor:
            return self.sender_supervisor.name
        return "System"

