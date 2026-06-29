from django.urls import path

from . import views

app_name = 'tasks'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),

    # Công việc
    path('cong-viec/', views.task_list, name='task_list'),
    path('cong-viec/them/', views.task_create, name='task_create'),
    path('cong-viec/<int:pk>/', views.task_detail, name='task_detail'),
    path('cong-viec/<int:pk>/sua/', views.task_update, name='task_update'),
    path('cong-viec/<int:pk>/xoa/', views.task_delete, name='task_delete'),
    path('cong-viec/<int:pk>/doi-trang-thai/', views.task_toggle, name='task_toggle'),
    path('cong-viec/<int:pk>/danh-dau-sao/', views.task_star, name='task_star'),
    path('cong-viec/<int:pk>/nhac-nho/', views.task_remind, name='task_remind'),
    path('cong-viec/<int:pk>/dat-trang-thai/', views.task_set_status, name='task_set_status'),

    # Công việc con
    path('cong-viec/<int:pk>/viec-con/them/', views.subtask_add, name='subtask_add'),
    path('viec-con/<int:pk>/doi/', views.subtask_toggle, name='subtask_toggle'),
    path('viec-con/<int:pk>/xoa/', views.subtask_delete, name='subtask_delete'),

    # Bình luận
    path('cong-viec/<int:pk>/binh-luan/', views.comment_add, name='comment_add'),
    path('binh-luan/<int:pk>/xoa/', views.comment_delete, name='comment_delete'),

    # Tệp đính kèm
    path('cong-viec/<int:pk>/dinh-kem/', views.attachment_add, name='attachment_add'),
    path('dinh-kem/<int:pk>/xoa/', views.attachment_delete, name='attachment_delete'),

    # Chế độ xem
    path('bang-kanban/', views.kanban, name='kanban'),
    path('lich/', views.calendar_view, name='calendar'),

    # Thùng rác
    path('thung-rac/', views.trash, name='trash'),
    path('thung-rac/<int:pk>/khoi-phuc/', views.task_restore, name='task_restore'),
    path('thung-rac/<int:pk>/xoa-vinh-vien/', views.task_purge, name='task_purge'),
    path('thung-rac/don-sach/', views.trash_empty, name='trash_empty'),

    # Xuất / In
    path('xuat/csv/', views.export_csv, name='export_csv'),
    path('xuat/excel/', views.export_excel, name='export_excel'),
    path('in/', views.print_view, name='print'),

    # Danh mục
    path('danh-muc/', views.category_list, name='category_list'),
    path('danh-muc/<int:pk>/sua/', views.category_update, name='category_update'),
    path('danh-muc/<int:pk>/xoa/', views.category_delete, name='category_delete'),

    # Nhãn
    path('nhan/', views.tag_list, name='tag_list'),
    path('nhan/<int:pk>/xoa/', views.tag_delete, name='tag_delete'),

    # Quản trị
    path('quan-tri/', views.admin_dashboard, name='admin_dashboard'),
    path('quan-tri/nguoi-dung/', views.admin_users, name='admin_users'),
    path('quan-tri/nguoi-dung/<int:pk>/doi-trang-thai/', views.admin_toggle_user, name='admin_toggle_user'),
    path('quan-tri/nguoi-dung/<int:pk>/doi-quyen/', views.admin_toggle_staff, name='admin_toggle_staff'),
    path('quan-tri/nguoi-dung/<int:pk>/xoa/', views.admin_delete_user, name='admin_delete_user'),
    path('quan-tri/cong-viec/', views.admin_tasks, name='admin_tasks'),
    path('quan-tri/cong-viec/<int:pk>/xoa/', views.admin_task_delete, name='admin_task_delete'),
]
