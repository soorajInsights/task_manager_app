from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.models import CustomUser
from .forms import CreateAdminForm, TaskForm, AssignUserForm, CreateUserForm
from tasks.models import Task

# ------------------------------
# Decorators
# ------------------------------

def staff_required(view_func):
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("admin_panel:login")
        if request.user.role not in ("ADMIN", "SUPERADMIN"):
            messages.error(request, "Permission denied.")
            return redirect("admin_panel:login")
        return view_func(request, *args, **kwargs)
    _wrapped.__name__ = view_func.__name__
    return _wrapped

def superadmin_required(view_func):
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.role != "SUPERADMIN":
            messages.error(request, "Only SuperAdmin allowed.")
            return redirect("admin_panel:dashboard")
        return view_func(request, *args, **kwargs)
    _wrapped.__name__ = view_func.__name__
    return _wrapped

# ------------------------------
# Auth Views
# ------------------------------

def login_view(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("admin_panel:dashboard")
    else:
        form = AuthenticationForm()
    return render(request, "admin_panel/login.html", {"form": form})

def logout_view(request):
    logout(request)
    return redirect("admin_panel:login")

# ------------------------------
# Dashboard
# ------------------------------

@staff_required
def dashboard(request):
    counts = {
        "total_admins": CustomUser.objects.filter(role="ADMIN").count(),
        "total_superadmins": CustomUser.objects.filter(role="SUPERADMIN").count(),
        "total_users": CustomUser.objects.filter(role="USER").count(),
        "total_tasks": Task.objects.count(),
    }
    return render(request, "admin_panel/dashboard.html", {"counts": counts})

# ------------------------------
# Admins Management
# ------------------------------

@staff_required
def admins_list(request):
    # Show only ADMIN or SUPERADMIN roles
    admins = CustomUser.objects.filter(role__in=["ADMIN", "SUPERADMIN"])
    return render(request, "admin_panel/admins_list.html", {"admins": admins})

@staff_required
@superadmin_required
def create_admin(request):
    if request.method == "POST":
        form = CreateAdminForm(request.POST)
        if form.is_valid():
            admin = form.save(commit=False)
            if admin.role not in ("ADMIN", "SUPERADMIN"):
                admin.role = "ADMIN"
            admin.save()
            messages.success(request, "Admin created successfully.")
            return redirect("admin_panel:admins_list")
    else:
        form = CreateAdminForm(initial={"role": "ADMIN"})
    return render(request, "admin_panel/create_admin.html", {"form": form})

# ------------------------------
# Tasks Management
# ------------------------------

@login_required
def tasks_list(request):
    user = request.user
    status_filter = request.GET.get("status")  # ① Capture ?status=

    # ② Get base queryset depending on user role
    if user.is_superadmin():
        tasks = Task.objects.select_related("assigned_to").all()
    elif user.is_admin():
        tasks = Task.objects.select_related("assigned_to").filter(assigned_to__manager=user)
    else:
        tasks = Task.objects.select_related("assigned_to").filter(assigned_to=user)

    # ③ Apply filter if ?status= present
    if status_filter:
        tasks = tasks.filter(status=status_filter)

    return render(request, "admin_panel/tasks_list.html", {"tasks": tasks})



@login_required
def create_task(request):
    user = request.user
    if not (user.is_superadmin() or user.is_admin()):
        return redirect("admin_panel:dashboard")

    if request.method == "POST":
        form = TaskForm(request.POST, user=user)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = user
            task.save()
            return redirect("admin_panel:tasks_list")
    else:
        form = TaskForm(user=user)

    return render(request, "admin_panel/task_form.html", {"form": form})

@login_required
def task_report(request, task_id):
    user = request.user
    task = get_object_or_404(Task, pk=task_id)

    if user.is_superadmin():
        pass
    elif user.is_admin() and task.assigned_to.manager_id != user.id:
        return redirect("dashboard")
    elif user.is_user() and task.assigned_to_id != user.id:
        return redirect("dashboard")

    return render(request, "admin_panel/task_report.html", {"task": task})


# ------------------------------
# Users Management
# ------------------------------

@login_required
def assign_user_to_admin(request, user_id):
    if not request.user.is_superadmin():
        return redirect("admin_panel:dashboard")

    user = get_object_or_404(CustomUser, pk=user_id, role="USER")

    if request.method == "POST":
        form = AssignUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect("admin_panel:list_users")
    else:
        form = AssignUserForm(instance=user)

    return render(request, "admin_panel/assign_user.html", {"form": form, "user": user})

@login_required
def list_users(request):
    if request.user.is_superadmin():
        users = CustomUser.objects.filter(role="USER")
    elif request.user.is_admin():
        users = CustomUser.objects.filter(role="USER", manager=request.user)
    else:
        users = CustomUser.objects.none()

    return render(request, "admin_panel/users_list.html", {"users": users})

@login_required
def create_user(request):
    if not request.user.is_superadmin():
        return redirect("dashboard")

    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "User created successfully.")
            return redirect("admin_panel:list_users")
    else:
        form = CreateUserForm()

    return render(request, "admin_panel/create_user.html", {"form": form})

