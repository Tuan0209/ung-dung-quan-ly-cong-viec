"""Kiểm thử bổ sung: các trang còn lại + trạng thái validation/lỗi + menu mobile."""
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


def login(page, username, password):
    page.goto(f'{BASE}/tai-khoan/dang-nhap/')
    page.fill('input[name="username"]', username)
    page.fill('input[name="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_load_state('networkidle')


def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={'width': 1440, 'height': 900})
        login(page, 'trungha', 'user123')

        # 13. Sửa công việc (mở công việc đầu tiên -> Sửa)
        page.goto(f'{BASE}/cong-viec/')
        page.wait_for_load_state('networkidle')
        page.locator('a.task-title').first.click()
        page.wait_for_load_state('networkidle')
        page.get_by_role('link', name='Sửa').first.click()
        page.wait_for_load_state('networkidle')
        check('Trang sửa công việc hiển thị', 'Sửa công việc' in page.content())
        check('Form sửa có dữ liệu sẵn (title không rỗng)',
              page.locator('input[name="title"]').input_value() != '')
        page.screenshot(path=f'{SHOT_DIR}/13_sua_cong_viec.png', full_page=True)

        # 14. Validation lỗi khi tạo công việc: tiêu đề quá ngắn
        page.goto(f'{BASE}/cong-viec/them/')
        page.wait_for_load_state('networkidle')
        page.fill('input[name="title"]', 'ab')  # < 3 ký tự
        page.get_by_role('button', name='Lưu').click()
        page.wait_for_load_state('networkidle')
        check('Hiển thị lỗi validation tiêu đề ngắn',
              'ít nhất 3 ký tự' in page.content())
        page.screenshot(path=f'{SHOT_DIR}/14_loi_validation_congviec.png', full_page=True)

        # 15. Validation lỗi: hạn ở quá khứ
        page.goto(f'{BASE}/cong-viec/them/')
        page.wait_for_load_state('networkidle')
        page.fill('input[name="title"]', 'Công việc hợp lệ')
        page.fill('input[name="due_date"]', '2020-01-01')
        page.get_by_role('button', name='Lưu').click()
        page.wait_for_load_state('networkidle')
        check('Hiển thị lỗi hạn trong quá khứ',
              'quá khứ' in page.content())
        page.screenshot(path=f'{SHOT_DIR}/15_loi_han_quakhu.png', full_page=True)

        # 16. Danh mục: validation trùng tên (Học tập đã tồn tại)
        page.goto(f'{BASE}/danh-muc/')
        page.wait_for_load_state('networkidle')
        page.fill('input[name="name"]', 'Học tập')
        page.get_by_role('button', name='Thêm danh mục').click()
        page.wait_for_load_state('networkidle')
        check('Hiển thị lỗi danh mục trùng tên',
              'đã có danh mục' in page.content())
        page.screenshot(path=f'{SHOT_DIR}/16_loi_danhmuc_trung.png', full_page=True)

        # 17. Sửa danh mục (lấy href trong dropdown ẩn rồi truy cập)
        page.goto(f'{BASE}/danh-muc/')
        page.wait_for_load_state('networkidle')
        edit_href = page.locator('.dropdown-menu a[href*="/danh-muc/"]').first.get_attribute('href')
        page.goto(f'{BASE}{edit_href}')
        page.wait_for_load_state('networkidle')
        check('Trang sửa danh mục hiển thị', 'Sửa danh mục' in page.content())
        page.screenshot(path=f'{SHOT_DIR}/17_sua_danhmuc.png', full_page=True)

        # 18. Empty state: lọc ra 0 kết quả
        page.goto(f'{BASE}/cong-viec/?q=khongtontaixyz123')
        page.wait_for_load_state('networkidle')
        check('Hiển thị trạng thái rỗng khi không có kết quả',
              'Không có công việc nào phù hợp' in page.content())
        page.screenshot(path=f'{SHOT_DIR}/18_empty_state.png', full_page=True)

        # 19. Đăng nhập sai mật khẩu -> thông báo lỗi
        ctx = browser.new_page(viewport={'width': 1440, 'height': 900})
        ctx.goto(f'{BASE}/tai-khoan/dang-nhap/')
        ctx.fill('input[name="username"]', 'trungha')
        ctx.fill('input[name="password"]', 'saibet')
        ctx.click('button[type="submit"]')
        ctx.wait_for_load_state('networkidle')
        check('Hiển thị lỗi đăng nhập sai',
              'không đúng' in ctx.content())
        ctx.screenshot(path=f'{SHOT_DIR}/19_dangnhap_sai.png', full_page=True)

        # 20. Menu mobile khi MỞ (hamburger)
        m = browser.new_page(viewport={'width': 390, 'height': 844})
        login(m, 'trungha', 'user123')
        m.goto(f'{BASE}/cong-viec/')
        m.wait_for_load_state('networkidle')
        m.click('#sidebarToggle')
        m.wait_for_timeout(500)
        check('Sidebar mở trên mobile',
              'open' in (m.locator('#sidebar').get_attribute('class') or ''))
        m.screenshot(path=f'{SHOT_DIR}/20_mobile_menu_mo.png', full_page=False)

        # 21. Danh sách công việc trên mobile (đóng menu)
        m.goto(f'{BASE}/cong-viec/')
        m.wait_for_load_state('networkidle')
        check('Danh sách công việc mobile hiển thị', 'Danh sách công việc' in m.content())
        m.screenshot(path=f'{SHOT_DIR}/21_mobile_danhsach.png', full_page=True)

        # 22. Trang quản trị trên mobile
        am = browser.new_page(viewport={'width': 390, 'height': 844})
        login(am, 'admin', 'admin123')
        am.goto(f'{BASE}/quan-tri/')
        am.wait_for_load_state('networkidle')
        check('Trang quản trị mobile hiển thị',
              'quản trị hệ thống' in am.content().lower())
        am.screenshot(path=f'{SHOT_DIR}/22_mobile_quantri.png', full_page=True)

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
