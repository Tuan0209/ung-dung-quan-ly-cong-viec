"""Tạo dữ liệu mẫu phong phú cho toàn bộ Ứng dụng quản lý công việc."""
import datetime
import random

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.utils import timezone

from tasks.models import Category, Comment, SubTask, Tag, Task

random.seed(2026)  # cố định để dữ liệu sinh ra ổn định, dễ demo


class Command(BaseCommand):
    help = 'Tạo dữ liệu mẫu phong phú (người dùng, danh mục, công việc)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--fresh', action='store_true',
            help='Xóa toàn bộ công việc & danh mục cũ trước khi tạo mới',
        )

    def handle(self, *args, **options):
        self.stdout.write('Đang tạo dữ liệu mẫu cho toàn hệ thống...')

        if options['fresh']:
            Task.objects.all().delete()
            Category.objects.all().delete()
            Tag.objects.all().delete()
            self.stdout.write('  - Đã xóa dữ liệu công việc, danh mục & nhãn cũ.')

        # ----- Tài khoản quản trị -----
        admin, _ = User.objects.get_or_create(
            username='admin',
            defaults={'email': 'admin@congviec.vn', 'first_name': 'Quản Trị Viên'},
        )
        admin.first_name = 'Quản Trị Viên'
        admin.email = 'admin@congviec.vn'
        admin.is_staff = True
        admin.is_superuser = True
        admin.set_password('admin123')
        admin.save()

        # ----- Người dùng thường -----
        users_info = [
            ('trungha', 'Nguyễn Trung Hà', 'trungha@congviec.vn'),
            ('lan', 'Trần Thị Lan', 'lan@congviec.vn'),
            ('minh', 'Lê Văn Minh', 'minh@congviec.vn'),
            ('hoa', 'Phạm Thị Hoa', 'hoa@congviec.vn'),
            ('nam', 'Đỗ Hoàng Nam', 'nam@congviec.vn'),
            ('thao', 'Vũ Phương Thảo', 'thao@congviec.vn'),
        ]
        users = []
        for username, fullname, email in users_info:
            u, _ = User.objects.get_or_create(username=username, defaults={'email': email})
            u.first_name = fullname
            u.email = email
            u.is_active = True
            u.set_password('user123')
            u.save()
            u.profile.phone = '09' + ''.join(random.choice('0123456789') for _ in range(8))
            u.profile.bio = f'Tôi là {fullname}, đang sử dụng ứng dụng để quản lý công việc.'
            u.profile.save()
            users.append(u)

        # ----- Mẫu danh mục (tên, màu, mô tả) -----
        category_templates = [
            ('Công việc', '#4f46e5', 'Nhiệm vụ tại cơ quan/công ty'),
            ('Học tập', '#0ea5e9', 'Bài tập, đồ án, ôn thi'),
            ('Cá nhân', '#22c55e', 'Việc riêng hằng ngày'),
            ('Dự án', '#a855f7', 'Công việc theo dự án'),
            ('Sức khỏe', '#14b8a6', 'Thể thao, khám sức khỏe'),
            ('Khẩn cấp', '#dc2626', 'Việc cần xử lý gấp'),
            ('Mua sắm', '#f59e0b', 'Danh sách cần mua'),
        ]

        # ----- Kho tiêu đề công việc theo danh mục -----
        task_pool = {
            'Công việc': [
                'Hoàn thiện báo cáo tuần', 'Gửi email cho khách hàng',
                'Chuẩn bị tài liệu cuộc họp', 'Cập nhật bảng tiến độ dự án',
                'Phản hồi yêu cầu từ phòng ban', 'Lập kế hoạch công việc tháng',
                'Tổng hợp số liệu kinh doanh', 'Họp giao ban đầu tuần',
            ],
            'Học tập': [
                'Làm bài tập môn Lập trình web', 'Ôn tập kiểm tra giữa kỳ',
                'Đọc tài liệu Django ORM', 'Viết báo cáo đồ án học phần',
                'Hoàn thành chương 3 của luận văn', 'Luyện tập thuật toán',
                'Xem video bài giảng tuần này', 'Nộp bài tập lớn môn CSDL',
            ],
            'Cá nhân': [
                'Dọn dẹp phòng làm việc', 'Gọi điện hỏi thăm gia đình',
                'Thanh toán hóa đơn điện nước', 'Cập nhật sơ yếu lý lịch',
                'Sắp xếp lịch tuần tới', 'Đọc xong cuốn sách đang dở',
            ],
            'Dự án': [
                'Thiết kế giao diện trang chủ', 'Viết tài liệu API',
                'Sửa lỗi đăng nhập của ứng dụng', 'Triển khai tính năng thông báo',
                'Kiểm thử chức năng thanh toán', 'Tối ưu tốc độ tải trang',
                'Họp nhóm tổng kết sprint',
            ],
            'Sức khỏe': [
                'Tập thể dục buổi sáng', 'Đi khám sức khỏe định kỳ',
                'Uống đủ 2 lít nước mỗi ngày', 'Đi ngủ trước 23 giờ',
                'Chạy bộ 30 phút', 'Đặt lịch khám nha khoa',
            ],
            'Khẩn cấp': [
                'Xử lý sự cố máy chủ', 'Phản hồi gấp tin nhắn khách hàng',
                'Nộp hồ sơ trước hạn chót', 'Sửa lỗi nghiêm trọng trên hệ thống',
            ],
            'Mua sắm': [
                'Mua đồ dùng học tập', 'Mua quà sinh nhật',
                'Đi siêu thị cuối tuần', 'Mua linh kiện máy tính',
            ],
        }

        priorities = [Task.Priority.LOW, Task.Priority.MEDIUM, Task.Priority.HIGH]
        statuses = [Task.Status.TODO, Task.Status.DOING, Task.Status.DONE]
        today = timezone.localdate()

        # Mẫu nhãn dùng chung
        tag_templates = [
            ('Gấp', '#dc2626'), ('Quan trọng', '#d97706'), ('Chờ duyệt', '#0ea5e9'),
            ('Đang chờ', '#64748b'), ('Ý tưởng', '#a855f7'), ('Theo dõi', '#14b8a6'),
        ]
        subtask_samples = [
            'Lên ý tưởng', 'Chuẩn bị tài liệu', 'Thực hiện chính',
            'Rà soát lại', 'Báo cáo kết quả', 'Kiểm tra lần cuối',
        ]
        comment_samples = [
            'Mình sẽ bắt đầu việc này hôm nay.', 'Cần thêm thông tin từ phòng ban khác.',
            'Đã hoàn thành phần đầu, đang làm tiếp.', 'Nhớ kiểm tra kỹ trước khi nộp.',
            'Việc này nên ưu tiên cao hơn.',
        ]

        total_tasks = 0
        for idx, user in enumerate(users):
            # Người dùng chính (trungha) có nhiều danh mục & công việc hơn
            num_cats = 6 if idx == 0 else random.randint(3, 5)
            chosen = category_templates[:num_cats]
            cats = []
            for name, color, desc in chosen:
                c, _ = Category.objects.get_or_create(
                    owner=user, name=name, defaults={'color': color, 'description': desc}
                )
                c.color = color
                c.description = desc
                c.save()
                cats.append((name, c))

            # Tạo nhãn cho người dùng
            num_tags = 5 if idx == 0 else random.randint(2, 4)
            user_tags = []
            for tname, tcolor in tag_templates[:num_tags]:
                tag, _ = Tag.objects.get_or_create(
                    owner=user, name=tname, defaults={'color': tcolor}
                )
                tag.color = tcolor
                tag.save()
                user_tags.append(tag)

            num_tasks = random.randint(18, 24) if idx == 0 else random.randint(8, 14)
            used_titles = set()
            for _ in range(num_tasks):
                cat_name, cat = random.choice(cats)
                pool = task_pool[cat_name]
                title = random.choice(pool)
                # tránh trùng tiêu đề trong cùng người dùng
                guard = 0
                while title in used_titles and guard < 5:
                    title = random.choice(pool)
                    guard += 1
                used_titles.add(title)

                status = random.choices(statuses, weights=[4, 3, 3])[0]
                priority = random.choices(priorities, weights=[3, 4, 3])[0]

                # ngày hạn: phân bố quá khứ / hôm nay / tương lai, một số không đặt
                roll = random.random()
                if roll < 0.15:
                    due = None
                elif roll < 0.35:
                    due = today - datetime.timedelta(days=random.randint(1, 8))  # quá hạn
                elif roll < 0.45:
                    due = today
                else:
                    due = today + datetime.timedelta(days=random.randint(1, 21))

                # 20% công việc giao cho người dùng khác (cộng tác)
                assigned = None
                if random.random() < 0.2 and len(users) > 1:
                    assigned = random.choice([u for u in users if u != user])

                t = Task(
                    owner=user,
                    title=title,
                    description=f'{title} — ghi chú chi tiết cho công việc này.',
                    category=cat,
                    priority=priority,
                    status=status,
                    due_date=due,
                    assigned_to=assigned,
                    is_starred=random.random() < 0.2,
                    repeat=random.choice([Task.Repeat.NONE, Task.Repeat.NONE,
                                          Task.Repeat.DAILY, Task.Repeat.WEEKLY]),
                )
                t.save()
                if status == Task.Status.DONE:
                    t.completed_at = timezone.now() - datetime.timedelta(
                        days=random.randint(0, 6), hours=random.randint(0, 23)
                    )
                    t.save(update_fields=['completed_at'])

                # Gắn 0-2 nhãn
                if user_tags and random.random() < 0.6:
                    t.tags.set(random.sample(user_tags, random.randint(1, min(2, len(user_tags)))))

                # 40% công việc có checklist (2-4 mục)
                if random.random() < 0.4:
                    for st in random.sample(subtask_samples, random.randint(2, 4)):
                        SubTask.objects.create(
                            task=t, title=st, is_done=random.random() < 0.5
                        )

                # 30% công việc có bình luận
                if random.random() < 0.3:
                    for _ in range(random.randint(1, 2)):
                        Comment.objects.create(
                            task=t, user=random.choice(users),
                            content=random.choice(comment_samples),
                        )
                total_tasks += 1

            # Mỗi người dùng có 1-2 công việc trong thùng rác
            for _ in range(random.randint(1, 2)):
                cat_name, cat = random.choice(cats)
                dt = Task(
                    owner=user, title=f'[Đã xóa] {random.choice(task_pool[cat_name])}',
                    category=cat, priority=Task.Priority.LOW, status=Task.Status.TODO,
                    is_deleted=True, deleted_at=timezone.now() - datetime.timedelta(days=random.randint(1, 5)),
                )
                dt.save()

        self.stdout.write(self.style.SUCCESS(
            f'Hoàn tất! {User.objects.count()} người dùng, '
            f'{Category.objects.count()} danh mục, {Tag.objects.count()} nhãn, '
            f'{Task.objects.count()} công việc, {SubTask.objects.count()} việc con, '
            f'{Comment.objects.count()} bình luận.'
        ))
        self.stdout.write('  - Quản trị: admin / admin123')
        self.stdout.write('  - Người dùng: trungha, lan, minh, hoa, nam, thao / user123')
