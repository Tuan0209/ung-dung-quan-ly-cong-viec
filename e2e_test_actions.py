"""Kiểm thử chức năng (functional): toggle, xóa công việc, xóa danh mục, khóa người dùng."""
import sys

from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:8000'
results = []


def check(name, condition):
    status = 'PASS' if condition else 'FAIL'
    results.append((status, name))
    print(f'[{status}] {name}')


def login(page, u, p):
    page.goto(f'{BASE}/tai-khoan/dang-nhap/')
    page.fill('input[name="username"]', u)
    page.fill('input[name="password"]', p)
    page.click('button[type="submit"]')
    page.wait_for_load_state('networkidle')


def run():
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        page = browser.new_page(viewport={'width': 1440, 'height': 900})
        login(page, 'trungha', 'user123')

        # --- Chuẩn bị: tạo 1 công việc để thao tác ---
        page.goto(f'{BASE}/cong-viec/them/')
        page.fill('input[name="title"]', 'CV thao tác chức năng')
        page.get_by_role('button', name='Lưu').click()
        page.wait_for_load_state('networkidle')
        check('Tạo công việc để test', 'CV thao tác chức năng' in page.content())

        # --- Đổi trạng thái nhanh (toggle) bằng checkbox ---
        page.goto(f'{BASE}/cong-viec/?q=thao')
        page.wait_for_load_state('networkidle')
        with page.expect_navigation():
            page.locator('.task-check').first.check()
        page.wait_for_load_state('networkidle')
        # Tải lại danh sách, kiểm tra checkbox đã được tích (trạng thái Hoàn thành)
        page.goto(f'{BASE}/cong-viec/?q=thao')
        page.wait_for_load_state('networkidle')
        check('Đổi trạng thái nhanh -> Hoàn thành',
              page.locator('.task-check').first.is_checked())

        # --- Xóa công việc (submit form trực tiếp qua JS) ---
        page.goto(f'{BASE}/cong-viec/?q=thao')
        page.wait_for_load_state('networkidle')
        action = page.locator('form[action*="/xoa/"]').first.get_attribute('action')
        with page.expect_navigation():
            page.evaluate("(a) => document.querySelector(`form[action='${a}']`).submit()", action)
        page.wait_for_load_state('networkidle')
        page.goto(f'{BASE}/cong-viec/?q=thao')
        page.wait_for_load_state('networkidle')
        check('Xóa công việc thành công', 'CV thao tác chức năng' not in page.content())

        # --- Tạo & xóa danh mục ---
        page.goto(f'{BASE}/danh-muc/')
        page.fill('input[name="name"]', 'Danh mục tạm để xóa')
        page.get_by_role('button', name='Thêm danh mục').click()
        page.wait_for_load_state('networkidle')
        check('Tạo danh mục mới', 'Danh mục tạm để xóa' in page.content())

        # Xóa danh mục vừa tạo (submit form trực tiếp qua JS)
        card = page.locator('.card-custom', has_text='Danh mục tạm để xóa')
        cat_action = card.locator('form[action*="/xoa/"]').get_attribute('action')
        with page.expect_navigation():
            page.evaluate("(a) => document.querySelector(`form[action='${a}']`).submit()", cat_action)
        page.wait_for_load_state('networkidle')
        check('Xóa danh mục thành công', 'Danh mục tạm để xóa' not in page.content())

        # --- Admin: khóa & mở khóa người dùng (form trong dropdown -> submit qua JS) ---
        admin = browser.new_page(viewport={'width': 1440, 'height': 900})
        login(admin, 'admin', 'admin123')
        admin.goto(f'{BASE}/quan-tri/nguoi-dung/')
        admin.wait_for_load_state('networkidle')
        # Khóa user 'lan'
        action = admin.locator('tr', has_text='@lan').locator('form[action*="/doi-trang-thai/"]').first.get_attribute('action')
        with admin.expect_navigation():
            admin.evaluate("(a)=>document.querySelector(`form[action='${a}']`).submit()", action)
        admin.wait_for_load_state('networkidle')
        locked = admin.locator('tr', has_text='@lan').locator('text=Đã khóa').count() > 0
        check('Khóa người dùng (lan) thành công', locked)
        # Mở khóa lại
        action2 = admin.locator('tr', has_text='@lan').locator('form[action*="/doi-trang-thai/"]').first.get_attribute('action')
        with admin.expect_navigation():
            admin.evaluate("(a)=>document.querySelector(`form[action='${a}']`).submit()", action2)
        admin.wait_for_load_state('networkidle')
        unlocked = admin.locator('tr', has_text='@lan').locator('text=Hoạt động').count() > 0
        check('Mở khóa người dùng (lan) thành công', unlocked)

        # --- Phân quyền: user thường không vào được trang quản trị ---
        page.goto(f'{BASE}/quan-tri/nguoi-dung/')
        page.wait_for_load_state('networkidle')
        check('User thường KHÔNG truy cập được quản lý người dùng',
              'Quản lý người dùng' not in page.content() or 'Đăng nhập' in page.content())

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
