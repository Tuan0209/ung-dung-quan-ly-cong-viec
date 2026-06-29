from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Profile


class RegisterForm(UserCreationForm):
    """Biểu mẫu đăng ký tài khoản mới."""

    first_name = forms.CharField(
        label='Họ và tên',
        max_length=150,
        widget=forms.TextInput(attrs={'placeholder': 'Nguyễn Văn A'}),
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={'placeholder': 'email@example.com'}),
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'email', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'username': 'Tên đăng nhập',
            'password1': 'Mật khẩu',
            'password2': 'Nhập lại mật khẩu',
        }
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
            if name in placeholders:
                field.widget.attrs['placeholder'] = placeholders[name]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Email này đã được sử dụng.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        if commit:
            user.save()
        return user


class LoginForm(AuthenticationForm):
    """Biểu mẫu đăng nhập."""

    error_messages = {
        'invalid_login': 'Tên đăng nhập hoặc mật khẩu không đúng.',
        'inactive': 'Tài khoản này đã bị khóa. Vui lòng liên hệ quản trị viên.',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Tên đăng nhập'}
        )
        self.fields['password'].widget.attrs.update(
            {'class': 'form-control', 'placeholder': 'Mật khẩu'}
        )


class UserUpdateForm(forms.ModelForm):
    """Cập nhật thông tin cơ bản của người dùng."""

    class Meta:
        model = User
        fields = ['first_name', 'email']
        labels = {'first_name': 'Họ và tên', 'email': 'Email'}
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        qs = User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError('Email này đã được sử dụng.')
        return email


class ProfileUpdateForm(forms.ModelForm):
    """Cập nhật hồ sơ mở rộng."""

    class Meta:
        model = Profile
        fields = ['phone', 'bio', 'avatar']
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.TextInput(attrs={'class': 'form-control'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
