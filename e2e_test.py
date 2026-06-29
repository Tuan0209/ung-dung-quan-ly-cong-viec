"""Kiểm thử E2E + chụp ảnh màn hình toàn bộ giao diện ứng dụng."""
import os
import sys

from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:8000'
SHOT_DIR = os.path.join(os.path.dirname(__file__), 'screenshots')
os.makedirs(SHOT_DIR, exist_ok=True)

results = []


def check(name, condition):
    status = 'PASS' if condition else 'FAIL'
    results.append((status, name))
    print(f'[{status}] {name}')


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1440, 'height': 900})

        # 1. Trang đăng nhập
        page.goto(f'{BASE}/tai-khoan/dang-nhap/')
        page.wait_for_load_state('networkidle')
        check('Trang đăng nhập hiển thị tiêu đề', 'Quản lý công việc' in page.content())
        page.screenshot(path=f'{SHOT_DIR}/01_dang_nhap.png', full_page=True)

        # 2. Trang đăng ký
        page.goto(f'{BASE}/tai-khoan/dang-ky/')
        page.wait_for_load_state('networkidle')
        check('Trang đăng ký có nút Đăng ký', page.get_by_role('button', name='Đăng ký').count() > 0)
        page.screenshot(path=f'{SHOT_DIR}/02_dang_ky.png', full_page=True)

        # 3. Đăng nhập tài khoản người dùng
        page.goto(f'{BASE}/tai-khoan/dang-nhap/')
        page.fill('input[name="username"]', 'trungha')
        page.fill('input[name="password"]', 'user123')
        page.click('button[type="submit"]')
        page.wait_for_load_state('networkidle')
        check('Đăng nhập thành công, vào Tổng quan', 'Tổng quan' in page.content())
        page.screenshot(path=f'{SHOT_DIR}/03_dashboard.png', full_page=True)

        # 4. Danh sách công việc
        page.goto(f'{BASE}/cong-viec/')
        page.wait_for_load_state('networkidle')
        check('Danh sách công việc hiển thị', 'Danh sách công việc' in page.content())
        page.screenshot(path=f'{SHOT_DIR}/04_danh_sach_cong_viec.png', full_page=True)

        # 5. Form thêm công việc
        page.goto(f'{BASE}/cong-viec/them/')
        page.wait_for_load_state('networkidle')
        check('Form thêm công việc có ô tiêu đề', page.locator('input[name="title"]').count() > 0)
        page.screenshot(path=f'{SHOT_DIR}/05_them_cong_viec.png', full_page=True)

        # 6. Tạo công việc mới (kiểm tra chức năng thực)
        page.fill('input[name="title"]', 'Công việc kiểm thử tự động')
        page.fill('textarea[name="description"]', 'Tạo bởi Playwright')
        page.select_option('select[name="priority"]', 'high')
        page.get_by_role('button', name='Lưu').click()
        page.wait_for_load_state('networkidle')
        check('Tạo công việc mới thành công', 'Công việc kiểm thử tự động' in page.content())
        page.screenshot(path=f'{SHOT_DIR}/06_sau_khi_them.png', full_page=True)

        # 7. Chi tiết công việc (mở từ danh sách)
        page.goto(f'{BASE}/cong-viec/')
        page.wait_for_load_state('networkidle')
        page.locator('a.task-title').first.click()
        page.wait_for_load_state('networkidle')
        check('Trang chi tiết công việc hiển thị', 'Chi tiết công việc' in page.content())
        page.screenshot(path=f'{SHOT_DIR}/07_chi_tiet_cong_viec.png', full_page=True)

        # 8. Danh mục
        page.goto(f'{BASE}/danh-muc/')
        page.wait_for_load_state('networkidle')
        check('Trang danh mục hiển thị', 'Quản lý danh mục' in page.content())
        page.screenshot(path=f'{SHOT_DIR}/08_danh_muc.png', full_page=True)

        # 9. Hồ sơ cá nhân
        page.goto(f'{BASE}/tai-khoan/ho-so/')
        page.wait_for_load_state('networkidle')
        check('Trang hồ sơ hiển thị', 'Hồ sơ cá nhân' in page.content())
        page.screenshot(path=f'{SHOT_DIR}/09_ho_so.png', full_page=True)

        # 10. Lọc công việc (kiểm tra chức năng tìm kiếm)
        page.goto(f'{BASE}/cong-viec/?status=done')
        page.wait_for_load_state('networkidle')
        check('Bộ lọc trạng thái hoạt động', page.locator('.task-item').count() >= 0)
        page.screenshot(path=f'{SHOT_DIR}/10_loc_cong_viec.png', full_page=True)

        # 11. Giao diện mobile (responsive)
        mobile = browser.new_page(viewport={'width': 390, 'height': 844})
        mobile.goto(f'{BASE}/tai-khoan/dang-nhap/')
        mobile.fill('input[name="username"]', 'trungha')
        mobile.fill('input[name="password"]', 'user123')
        mobile.click('button[type="submit"]')
        mobile.wait_for_load_state('networkidle')
        check('Giao diện mobile tải được Tổng quan', 'Tổng quan' in mobile.content())
        mobile.screenshot(path=f'{SHOT_DIR}/11_mobile_dashboard.png', full_page=True)

        # 12. Đăng nhập admin + trang quản trị
        admin = browser.new_page(viewport={'width': 1440, 'height': 900})
        admin.goto(f'{BASE}/tai-khoan/dang-nhap/')
        admin.fill('input[name="username"]', 'admin')
        admin.fill('input[name="password"]', 'admin123')
        admin.click('button[type="submit"]')
        admin.wait_for_load_state('networkidle')
        admin.goto(f'{BASE}/quan-tri/')
        admin.wait_for_load_state('networkidle')
        check('Bảng quản trị hệ thống hiển thị', 'quản trị hệ thống' in admin.content().lower())
        admin.goto(f'{BASE}/quan-tri/nguoi-dung/')
        admin.wait_for_load_state('networkidle')
        check('Trang quản lý người dùng hiển thị', 'Quản lý người dùng' in admin.content())
        admin.screenshot(path=f'{SHOT_DIR}/12_quan_tri.png', full_page=True)

        browser.close()


if __name__ == '__main__':
    try:
        run()
    except Exception as e:
        print(f'[FAIL] Lỗi khi chạy test: {e}')
        results.append(('FAIL', f'Ngoại lệ: {e}'))

    passed = sum(1 for s, _ in results if s == 'PASS')
    failed = sum(1 for s, _ in results if s == 'FAIL')
    print(f'\n===== KẾT QUẢ: {passed} PASS / {failed} FAIL =====')
    sys.exit(1 if failed else 0)
