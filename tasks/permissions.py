from rest_framework.permissions import BasePermission, SAFE_METHODS

class TaskPermission(BasePermission):
    """
    - SuperAdmin: can see all tasks.
    - Admin: can see tasks for their assigned users.
    - User: can only see and update their own tasks.
    """

    def has_object_permission(self, request, view, obj):
        user = request.user

        if hasattr(user, "is_superadmin") and user.is_superadmin():
            return True

        if hasattr(user, "is_admin") and user.is_admin():
            # Admin can manage tasks of users they manage or tasks they created
            return obj.assigned_to.manager_id == user.id or obj.created_by_id == user.id

        # else normal user
        return obj.assigned_to_id == user.id

    def has_permission(self, request, view):
        # Must be authenticated
        return request.user and request.user.is_authenticated
