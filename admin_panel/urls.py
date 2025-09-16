from django.urls import path
from . import views

app_name = "admin_panel"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("admins/", views.admins_list, name="admins_list"),
    path("admins/create/", views.create_admin, name="create_admin"),
    path("tasks/", views.tasks_list, name="tasks_list"),
    path("tasks/create/", views.create_task, name="create_task"),
    path("tasks/<int:task_id>/report/", views.task_report, name="task_report"),
    path("users/", views.list_users, name="list_users"),
    path("users/create/", views.create_user, name="create_user"),
    path("users/<int:user_id>/assign/", views.assign_user_to_admin, name="assign_user_to_admin"),

]
