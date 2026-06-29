from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from .forms import LoginForm, ProfileUpdateForm, RegisterForm, UserUpdateForm


def register_view(request):
    """Đăng ký tài khoản mới."""
    if request.user.is_authenticated:
        return redirect('tasks:dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Đăng ký thành công! Chào mừng bạn đến với hệ thống.')
            return redirect('tasks:dashboard')
        messages.error(request, 'Vui lòng kiểm tra lại thông tin đăng ký.')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


class CustomLoginView(LoginView):
    """Đăng nhập với giao diện tùy chỉnh."""

    template_name = 'accounts/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks:dashboard')

    def form_valid(self, form):
        user = form.get_user()
        messages.success(self.request, f'Xin chào {user.get_full_name() or user.username}!')
        return super().form_valid(form)


def logout_view(request):
    """Đăng xuất."""
    logout(request)
    messages.info(request, 'Bạn đã đăng xuất.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    """Xem và cập nhật hồ sơ cá nhân."""
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Cập nhật hồ sơ thành công.')
            return redirect('accounts:profile')
        messages.error(request, 'Vui lòng kiểm tra lại thông tin.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(
        request,
        'accounts/profile.html',
        {'user_form': user_form, 'profile_form': profile_form},
    )


@login_required
def change_password_view(request):
    """Đổi mật khẩu (giữ nguyên phiên đăng nhập sau khi đổi)."""
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # không bị đăng xuất
            messages.success(request, 'Đổi mật khẩu thành công.')
            return redirect('accounts:profile')
        messages.error(request, 'Vui lòng kiểm tra lại thông tin.')
    else:
        form = PasswordChangeForm(user=request.user)

    # Gắn class Bootstrap cho các ô nhập
    for field in form.fields.values():
        field.widget.attrs['class'] = 'form-control'

    return render(request, 'accounts/change_password.html', {'form': form})
