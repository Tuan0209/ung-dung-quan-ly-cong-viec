from django import forms
from django.contrib.auth.models import User
from django.utils import timezone

from .models import Category, Comment, SubTask, Tag, Task


class TaskForm(forms.ModelForm):
    """Biểu mẫu tạo/sửa công việc."""

    class Meta:
        model = Task
        fields = [
            'title', 'description', 'category', 'tags', 'assigned_to',
            'priority', 'status', 'repeat', 'is_starred', 'due_date',
        ]
        widgets = {
            'title': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Nhập tiêu đề công việc'}
            ),
            'description': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 4,
                       'placeholder': 'Mô tả chi tiết (không bắt buộc)'}
            ),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-select', 'size': 4}),
            'assigned_to': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'repeat': forms.Select(attrs={'class': 'form-select'}),
            'is_starred': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'due_date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'
            ),
        }
        labels = {'is_starred': 'Đánh dấu quan trọng'}

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            self.fields['category'].queryset = Category.objects.filter(owner=user)
            self.fields['tags'].queryset = Tag.objects.filter(owner=user)
            # Có thể giao việc cho chính mình hoặc người dùng khác
            self.fields['assigned_to'].queryset = User.objects.filter(is_active=True).order_by('username')
        self.fields['category'].empty_label = '— Không có danh mục —'
        self.fields['assigned_to'].empty_label = '— Giao cho chính tôi —'
        self.fields['due_date'].input_formats = ['%Y-%m-%d']

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if len(title) < 3:
            raise forms.ValidationError('Tiêu đề phải có ít nhất 3 ký tự.')
        return title

    def clean_due_date(self):
        due_date = self.cleaned_data.get('due_date')
        if due_date and not self.instance.pk and due_date < timezone.localdate():
            raise forms.ValidationError('Hạn hoàn thành không được ở trong quá khứ.')
        return due_date


class CategoryForm(forms.ModelForm):
    """Biểu mẫu tạo/sửa danh mục."""

    class Meta:
        model = Category
        fields = ['name', 'color', 'description']
        widgets = {
            'name': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Tên danh mục'}
            ),
            'color': forms.TextInput(
                attrs={'class': 'form-control form-control-color', 'type': 'color'}
            ),
            'description': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Mô tả ngắn (không bắt buộc)'}
            ),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 2:
            raise forms.ValidationError('Tên danh mục phải có ít nhất 2 ký tự.')
        qs = Category.objects.filter(owner=self.user, name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Bạn đã có danh mục với tên này.')
        return name


class TagForm(forms.ModelForm):
    """Biểu mẫu tạo/sửa nhãn."""

    class Meta:
        model = Tag
        fields = ['name', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Tên nhãn'}),
            'color': forms.TextInput(attrs={'class': 'form-control form-control-color', 'type': 'color'}),
        }

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if len(name) < 1:
            raise forms.ValidationError('Tên nhãn không được để trống.')
        qs = Tag.objects.filter(owner=self.user, name__iexact=name)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Bạn đã có nhãn với tên này.')
        return name


class SubTaskForm(forms.ModelForm):
    """Biểu mẫu thêm công việc con."""

    class Meta:
        model = SubTask
        fields = ['title']
        widgets = {
            'title': forms.TextInput(
                attrs={'class': 'form-control', 'placeholder': 'Thêm một mục việc con...'}
            ),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise forms.ValidationError('Nội dung không được để trống.')
        return title


class CommentForm(forms.ModelForm):
    """Biểu mẫu thêm bình luận."""

    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 2,
                       'placeholder': 'Viết bình luận...'}
            ),
        }

    def clean_content(self):
        content = self.cleaned_data.get('content', '').strip()
        if not content:
            raise forms.ValidationError('Bình luận không được để trống.')
        return content


class AttachmentForm(forms.Form):
    """Biểu mẫu tải tệp đính kèm."""

    file = forms.FileField(
        label='Chọn tệp', widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
