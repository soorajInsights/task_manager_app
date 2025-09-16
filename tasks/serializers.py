from rest_framework import serializers
from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = [
            "id",
            "title",
            "description",
            "assigned_to",
            "due_date",
            "status",
            "completion_report",
            "worked_hours",
            "created_by",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_by", "created_at", "updated_at"]

    def validate(self, data):
        """
        Enforce: when status=COMPLETED, completion_report and worked_hours are required.
        """
        status = data.get("status") or getattr(self.instance, "status", None)
        report = data.get("completion_report") or getattr(self.instance, "completion_report", None)
        hours = data.get("worked_hours") or getattr(self.instance, "worked_hours", None)

        if status == Task.Status.COMPLETED:
            if not report or hours is None:
                raise serializers.ValidationError(
                    "When a task is completed, completion_report and worked_hours are required."
                )
        return data
