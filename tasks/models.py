from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

class Task(models.Model):
    class Status(models.TextChoices):
        TODO = "TODO", "To Do"
        IN_PROGRESS = "IN_PROGRESS", "In Progress"
        COMPLETED = "COMPLETED", "Completed"

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="tasks",
        help_text="User who will do the task",
    )
    due_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.TODO,
        help_text="Select task status",
    )

    # Required only when status=COMPLETED:
    completion_report = models.TextField(blank=True, null=True)
    worked_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Hours worked (required when completed)",
    )

    created_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="created_tasks",
        help_text="Admin or SuperAdmin who created the task",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        """
        Enforce rules:
        - If status=COMPLETED, completion_report and worked_hours must be provided.
        """
        from django.core.exceptions import ValidationError

        if self.status == self.Status.COMPLETED:
            if not self.completion_report or self.worked_hours is None:
                raise ValidationError(
                    "When a task is completed, completion_report and worked_hours are required."
                )

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
