from django.db.models import Q
from django.utils import timezone

from .models import Task


def task_counters(request):
    """Cung cấp số liệu công việc cho thanh điều hướng (mọi trang)."""
    if not request.user.is_authenticated:
        return {}
    today = timezone.localdate()
    tasks = Task.objects.filter(
        Q(owner=request.user) | Q(assigned_to=request.user), is_deleted=False
    ).distinct()
    return {
        'nav_total_tasks': tasks.count(),
        'nav_overdue_tasks': tasks.filter(
            due_date__lt=today, status__in=[Task.Status.TODO, Task.Status.DOING]
        ).count(),
        'nav_trash_count': Task.objects.filter(owner=request.user, is_deleted=True).count(),
    }
