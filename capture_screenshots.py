"""Chụp bộ ảnh giao diện sạch để gửi khách (chỉ xem, không tạo dữ liệu rác)."""
import os

from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:8000'
SHOT = os.path.join(os.path.dirname(__file__), 'screenshots')
os.makedirs(SHOT, exist_ok=True)
shots = []


def snap(page, name):
    path = f'{SHOT}/{name}.png'
    page.screenshot(path=path, full_page=True)
    shots.append(name)
    print('  +', name)


def login(page, u, p):
    page.goto(f'{BASE}/tai-khoan/dang-nhap/')
    page.fill('input[name="username"]', u)
    page.fill('input[name="password"]', p)
    page.click('button[type="submit"]')
    page.wait_for_load_state('networkidle')


def run():
    with sync_playwright() as pw:
        b = pw.chromium.launch()

        # ===== Trang công khai (chưa đăng nhập) =====
        pub = b.new_page(viewport={'width': 1440, 'height': 900})
        pub.goto(f'{BASE}/tai-khoan/dang-nhap/'); pub.wait_for_load_state('networkidle')
        snap(pub, '01_dang_nhap')
        pub.goto(f'{BASE}/tai-khoan/dang-ky/'); pub.wait_for_load_state('networkidle')
        snap(pub, '02_dang_ky')
        pub.close()

        # ===== Người dùng (trungha) =====
        page = b.new_page(viewport={'width': 1440, 'height': 900})
        login(page, 'trungha', 'user123')
        snap(page, '03_tong_quan')

        page.goto(f'{BASE}/cong-viec/'); page.wait_for_load_state('networkidle')
        snap(page, '04_danh_sach_cong_viec')

        # Chi tiết: chọn công việc có nhiều dữ liệu nhất (việc con + bình luận)
        cid = page.evaluate("""async () => {
            const r = await fetch('/cong-viec/'); return null;
        }""")
        # mở công việc đầu tiên trong danh sách
        page.locator('a.task-title').first.click(); page.wait_for_load_state('networkidle')
        snap(page, '05_chi_tiet_cong_viec')

        page.goto(f'{BASE}/cong-viec/them/'); page.wait_for_load_state('networkidle')
        snap(page, '06_them_cong_viec')

        page.goto(f'{BASE}/bang-kanban/'); page.wait_for_load_state('networkidle')
        snap(page, '07_bang_kanban')

        page.goto(f'{BASE}/lich/'); page.wait_for_load_state('networkidle')
        snap(page, '08_lich_cong_viec')

        page.goto(f'{BASE}/danh-muc/'); page.wait_for_load_state('networkidle')
        snap(page, '09_danh_muc')

        page.goto(f'{BASE}/nhan/'); page.wait_for_load_state('networkidle')
        snap(page, '10_nhan')

        page.goto(f'{BASE}/thung-rac/'); page.wait_for_load_state('networkidle')
        snap(page, '11_thung_rac')

        page.goto(f'{BASE}/tai-khoan/ho-so/'); page.wait_for_load_state('networkidle')
        snap(page, '12_ho_so')

        page.goto(f'{BASE}/tai-khoan/doi-mat-khau/'); page.wait_for_load_state('networkidle')
        snap(page, '13_doi_mat_khau')
        page.close()

        # ===== Giao diện mobile =====
        m = b.new_page(viewport={'width': 390, 'height': 844})
        login(m, 'trungha', 'user123')
        snap(m, '14_mobile_tong_quan')
        m.goto(f'{BASE}/cong-viec/'); m.wait_for_load_state('networkidle')
        snap(m, '15_mobile_danh_sach')
        m.close()

        # ===== Quản trị viên (admin) =====
        adm = b.new_page(viewport={'width': 1440, 'height': 900})
        login(adm, 'admin', 'admin123')
        adm.goto(f'{BASE}/quan-tri/'); adm.wait_for_load_state('networkidle')
        snap(adm, '16_admin_bang_quan_tri')
        adm.goto(f'{BASE}/quan-tri/nguoi-dung/'); adm.wait_for_load_state('networkidle')
        snap(adm, '17_admin_quan_ly_nguoi_dung')
        adm.goto(f'{BASE}/quan-tri/cong-viec/'); adm.wait_for_load_state('networkidle')
        snap(adm, '18_admin_quan_ly_cong_viec')
        adm.close()

        b.close()


if __name__ == '__main__':
    print('Đang chụp ảnh giao diện...')
    run()
    print(f'\nHoàn tất! Đã chụp {len(shots)} ảnh vào thư mục screenshots/')
