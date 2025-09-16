from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.db.models import Q

from .models import Task
from .serializers import TaskSerializer
from .permissions import TaskPermission

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all().select_related("assigned_to", "created_by")
    serializer_class = TaskSerializer
    permission_classes = [TaskPermission]

    def get_queryset(self):
        """
        Filter tasks based on role:
        - SuperAdmin sees all.
        - Admin sees tasks of their assigned users.
        - User sees only their own tasks.
        """
        user = self.request.user

        if user.is_superadmin():
            return Task.objects.all()

        if user.is_admin():
            return Task.objects.filter(
                Q(assigned_to__manager=user) | Q(created_by=user)
            )

        # normal user
        return Task.objects.filter(assigned_to=user)

    def perform_create(self, serializer):
        """
        Set created_by automatically when Admin or SuperAdmin creates tasks.
        """
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=["get"])
    def report(self, request, pk=None):
        """
        GET /api/v1/tasks/<id>/report/
        - Admin and SuperAdmin can view report of completed tasks.
        """
        task = self.get_object()

        # Check permissions:
        if request.user.is_user():
            return Response({"detail": "Not allowed."}, status=status.HTTP_403_FORBIDDEN)

        if task.status != Task.Status.COMPLETED:
            return Response({"detail": "Report only available for completed tasks."}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "completion_report": task.completion_report,
            "worked_hours": task.worked_hours,
            "assigned_to": task.assigned_to.username,
            "title": task.title,
        }
        return Response(data)
