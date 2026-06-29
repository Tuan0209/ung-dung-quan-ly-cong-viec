from django.conf import settings
from django.db import models
from django.utils import timezone


class Tag(models.Model):
    """Nhãn để gắn cho công việc (nhiều nhãn cho 1 công việc)."""

    name = models.CharField('Tên nhãn', max_length=50)
    color = models.CharField('Màu sắc', max_length=7, default='#64748b')
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tags',
        verbose_name='Chủ sở hữu',
    )

    class Meta:
        verbose_name = 'Nhãn'
        verbose_name_plural = 'Nhãn'
        ordering = ['name']
        unique_together = ['owner', 'name']

    def __str__(self):
        return self.name


class Category(models.Model):
    """Danh mục/Dự án để nhóm các công việc."""

    name = models.CharField('Tên danh mục', max_length=100)
    color = models.CharField('Màu sắc', max_length=7, default='#2563eb')
    description = models.CharField('Mô tả', max_length=255, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='categories',
        verbose_name='Chủ sở hữu',
    )
    created_at = models.DateTimeField('Ngày tạo', auto_now_add=True)

    class Meta:
        verbose_name = 'Danh mục'
        verbose_name_plural = 'Danh mục'
        ordering = ['name']
        unique_together = ['owner', 'name']

    def __str__(self):
        return self.name

    @property
    def task_count(self):
        return self.tasks.filter(is_deleted=False).count()

    @property
    def done_count(self):
        return self.tasks.filter(is_deleted=False, status=Task.Status.DONE).count()


class Task(models.Model):
    """Công việc cần thực hiện."""

    class Priority(models.TextChoices):
        LOW = 'low', 'Thấp'
        MEDIUM = 'medium', 'Trung bình'
        HIGH = 'high', 'Cao'

    class Status(models.TextChoices):
        TODO = 'todo', 'Cần làm'
        DOING = 'doing', 'Đang làm'
        DONE = 'done', 'Hoàn thành'

    class Repeat(models.TextChoices):
        NONE = 'none', 'Không lặp'
        DAILY = 'daily', 'Hằng ngày'
        WEEKLY = 'weekly', 'Hằng tuần'
        MONTHLY = 'monthly', 'Hằng tháng'

    title = models.CharField('Tiêu đề', max_length=200)
    description = models.TextField('Mô tả', blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name='Danh mục',
    )
    tags = models.ManyToManyField(
        Tag, blank=True, related_name='tasks', verbose_name='Nhãn'
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='tasks',
        verbose_name='Người tạo',
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_tasks',
        verbose_name='Người được giao',
    )
    priority = models.CharField(
        'Độ ưu tiên', max_length=10, choices=Priority.choices, default=Priority.MEDIUM
    )
    status = models.CharField(
        'Trạng thái', max_length=10, choices=Status.choices, default=Status.TODO
    )
    repeat = models.CharField(
        'Lặp lại', max_length=10, choices=Repeat.choices, default=Repeat.NONE
    )
    is_starred = models.BooleanField('Quan trọng', default=False)
    due_date = models.DateField('Hạn hoàn thành', null=True, blank=True)
    completed_at = models.DateTimeField('Thời điểm hoàn thành', null=True, blank=True)
    is_deleted = models.BooleanField('Đã xóa (thùng rác)', default=False)
    deleted_at = models.DateTimeField('Thời điểm xóa', null=True, blank=True)
    created_at = models.DateTimeField('Ngày tạo', auto_now_add=True)
    updated_at = models.DateTimeField('Cập nhật lần cuối', auto_now=True)

    class Meta:
        verbose_name = 'Công việc'
        verbose_name_plural = 'Công việc'
        ordering = ['-is_starred', '-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.status == self.Status.DONE and self.completed_at is None:
            self.completed_at = timezone.now()
        elif self.status != self.Status.DONE:
            self.completed_at = None
        super().save(*args, **kwargs)

    def soft_delete(self):
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])

    def restore(self):
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=['is_deleted', 'deleted_at'])

    @property
    def is_overdue(self):
        if self.due_date and self.status != self.Status.DONE:
            return self.due_date < timezone.localdate()
        return False

    @property
    def progress(self):
        """% hoàn thành dựa trên công việc con; nếu không có thì theo trạng thái."""
        subs = self.subtasks.all()
        total = len(subs)
        if total:
            done = sum(1 for s in subs if s.is_done)
            return round(done / total * 100)
        return 100 if self.status == self.Status.DONE else 0

    @property
    def priority_badge(self):
        return {
            self.Priority.LOW: 'secondary',
            self.Priority.MEDIUM: 'warning',
            self.Priority.HIGH: 'danger',
        }.get(self.priority, 'secondary')

    @property
    def status_badge(self):
        return {
            self.Status.TODO: 'secondary',
            self.Status.DOING: 'info',
            self.Status.DONE: 'success',
        }.get(self.status, 'secondary')


class SubTask(models.Model):
    """Công việc con (mục trong checklist)."""

    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name='subtasks', verbose_name='Công việc'
    )
    title = models.CharField('Nội dung', max_length=200)
    is_done = models.BooleanField('Đã xong', default=False)
    created_at = models.DateTimeField('Ngày tạo', auto_now_add=True)

    class Meta:
        verbose_name = 'Công việc con'
        verbose_name_plural = 'Công việc con'
        ordering = ['created_at']

    def __str__(self):
        return self.title


class Comment(models.Model):
    """Bình luận/trao đổi trong công việc."""

    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name='comments', verbose_name='Công việc'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Người viết'
    )
    content = models.TextField('Nội dung')
    created_at = models.DateTimeField('Thời điểm', auto_now_add=True)

    class Meta:
        verbose_name = 'Bình luận'
        verbose_name_plural = 'Bình luận'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.user} - {self.content[:30]}'


class Attachment(models.Model):
    """Tệp đính kèm cho công việc."""

    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name='attachments', verbose_name='Công việc'
    )
    file = models.FileField('Tệp', upload_to='attachments/%Y/%m/')
    original_name = models.CharField('Tên tệp', max_length=255, blank=True)
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, verbose_name='Người tải lên'
    )
    uploaded_at = models.DateTimeField('Thời điểm tải lên', auto_now_add=True)

    class Meta:
        verbose_name = 'Tệp đính kèm'
        verbose_name_plural = 'Tệp đính kèm'
        ordering = ['-uploaded_at']

    def __str__(self):
        return self.original_name or self.file.name
