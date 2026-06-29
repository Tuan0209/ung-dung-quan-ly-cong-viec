from django.contrib import admin

from .models import Attachment, Category, Comment, SubTask, Tag, Task


class SubTaskInline(admin.TabularInline):
    model = SubTask
    extra = 0


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'color', 'task_count', 'created_at']
    list_filter = ['owner']
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'color']
    list_filter = ['owner']
    search_fields = ['name']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'assigned_to', 'category', 'priority',
                    'status', 'is_starred', 'is_deleted', 'due_date', 'created_at']
    list_filter = ['status', 'priority', 'is_starred', 'is_deleted', 'category']
    search_fields = ['title', 'description']
    date_hierarchy = 'created_at'
    inlines = [SubTaskInline, CommentInline]


@admin.register(SubTask)
class SubTaskAdmin(admin.ModelAdmin):
    list_display = ['title', 'task', 'is_done']
    list_filter = ['is_done']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['user', 'task', 'created_at']


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin):
    list_display = ['original_name', 'task', 'uploaded_by', 'uploaded_at']
