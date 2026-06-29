"""Cấu hình URL gốc cho dự án Ứng dụng quản lý công việc."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tai-khoan/', include('accounts.urls')),
    path('', include('tasks.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Tùy chỉnh tiêu đề trang quản trị Django
admin.site.site_header = 'Quản trị Ứng dụng quản lý công việc'
admin.site.site_title = 'Quản trị công việc'
admin.site.index_title = 'Bảng điều khiển quản trị'
