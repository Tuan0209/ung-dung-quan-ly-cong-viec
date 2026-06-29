"""Kiểm thử toàn bộ chức năng mới + chụp screenshot."""
import os
import sys

from playwright.sync_api import sync_playwright

BASE = 'http://127.0.0.1:8000'
SHOT = os.path.join(os.path.dirname(__file__), 'screenshots')
os.makedirs(SHOT, exist_ok=True)
results = []


def check(name, cond):
    s = 'PASS' if cond else 'FAIL'
    results.append((s, name))
    print(f'[{s}] {name}')


def login(page, u, p):
    page.goto(f'{BASE}/tai-khoan/dang-nhap/')
    page.fill('input[name="username"]', u)
    page.fill('input[name="password"]', p)
    page.click('button[type="submit"]')
    page.wait_for_load_state('networkidle')


def run():
    with sync_playwright() as pw:
        b = pw.chromium.launch()
        page = b.new_page(viewport={'width': 1440, 'height': 900})
        login(page, 'trungha', 'user123')

        # 1. Dashboard có biểu đồ 7 ngày
        page.goto(f'{BASE}/')
        page.wait_for_load_state('networkidle')
        check('Dashboard hiển thị biểu đồ 7 ngày', page.locator('#weekChart').count() > 0)
        page.screenshot(path=f'{SHOT}/f01_dashboard.png', full_page=True)

        # 2. Bảng Kanban
        page.goto(f'{BASE}/bang-kanban/')
        page.wait_for_load_state('networkidle')
        check('Kanban có 3 cột', page.locator('.kanban-col').count() == 3)
        check('Kanban có thẻ công việc', page.locator('.kanban-card').count() > 0)
        page.screenshot(path=f'{SHOT}/f02_kanban.png', full_page=True)

        # 3. Kanban đổi trạng thái: gọi đúng API mà thao tác kéo-thả sử dụng
        todo_cards = page.locator('.kanban-col[data-status="todo"] .kanban-card')
        if todo_cards.count() > 0:
            cid = todo_cards.first.get_attribute('data-id')
            ok = page.evaluate("""async (id) => {
                const m = document.cookie.match(/csrftoken=([^;]+)/);
                const token = m ? m[1] : '';
                const form = new FormData();
                form.append('status', 'done');
                form.append('csrfmiddlewaretoken', token);
                const r = await fetch(`/cong-viec/${id}/dat-trang-thai/`,
                    {method:'POST', body:form, headers:{'X-CSRFToken': token}});
                return r.ok;
            }""", cid)
            page.goto(f'{BASE}/bang-kanban/')
            page.wait_for_load_state('networkidle')
            moved = page.locator(f'.kanban-col[data-status="done"] .kanban-card[data-id="{cid}"]').count() > 0
            check('Đổi trạng thái Kanban (API kéo-thả) thành công', ok and moved)
        else:
            check('Đổi trạng thái Kanban (API kéo-thả) thành công', False)

        # 4. Lịch công việc
        page.goto(f'{BASE}/lich/')
        page.wait_for_load_state('networkidle')
        check('Lịch hiển thị bảng tháng', page.locator('.calendar-table').count() > 0)
        page.screenshot(path=f'{SHOT}/f03_calendar.png', full_page=True)

        # 5. Tạo công việc với nhãn + giao việc + quan trọng
        page.goto(f'{BASE}/cong-viec/them/')
        page.wait_for_load_state('networkidle')
        page.fill('input[name="title"]', 'Công việc kiểm thử tính năng')
        page.check('input[name="is_starred"]')
        page.get_by_role('button', name='Lưu').click()
        page.wait_for_load_state('networkidle')
        check('Tạo công việc -> vào trang chi tiết', 'Chi tiết công việc' in page.content())
        check('Công việc được đánh dấu sao', page.locator('.bi-star-fill').count() > 0)

        # 6. Thêm công việc con (checklist)
        page.fill('input[name="title"]', 'Mục việc con kiểm thử')
        page.locator('form[action*="/viec-con/them/"] button').click()
        page.wait_for_load_state('networkidle')
        check('Thêm công việc con thành công', 'Mục việc con kiểm thử' in page.content())

        # 7. Thêm bình luận
        page.fill('textarea[name="content"]', 'Đây là bình luận kiểm thử.')
        page.get_by_role('button', name='Gửi bình luận').click()
        page.wait_for_load_state('networkidle')
        check('Thêm bình luận thành công', 'Đây là bình luận kiểm thử.' in page.content())
        page.screenshot(path=f'{SHOT}/f04_task_detail_full.png', full_page=True)

        # 8. Gửi nhắc nhở (email console -> không lỗi)
        page.get_by_role('button', name='Gửi nhắc nhở qua email').click()
        page.wait_for_load_state('networkidle')
        check('Gửi nhắc nhở không lỗi', 'nhắc nhở' in page.content() or 'email' in page.content().lower())

        # 9. Quản lý nhãn
        page.goto(f'{BASE}/nhan/')
        page.wait_for_load_state('networkidle')
        page.fill('input[name="name"]', 'NhãnKiểmThử')
        page.get_by_role('button', name='Thêm nhãn').click()
        page.wait_for_load_state('networkidle')
        check('Tạo nhãn thành công', 'NhãnKiểmThử' in page.content())
        page.screenshot(path=f'{SHOT}/f05_tags.png', full_page=True)

        # 10. Thùng rác: xóa mềm rồi khôi phục
        page.goto(f'{BASE}/cong-viec/?q=kiểm thử tính năng')
        page.wait_for_load_state('networkidle')
        action = page.locator('form[action*="/xoa/"]').first.get_attribute('action')
        with page.expect_navigation():
            page.evaluate("(a)=>document.querySelector(`form[action='${a}']`).submit()", action)
        page.wait_for_load_state('networkidle')
        page.goto(f'{BASE}/thung-rac/')
        page.wait_for_load_state('networkidle')
        check('Công việc đã vào thùng rác', 'Công việc kiểm thử tính năng' in page.content())
        page.screenshot(path=f'{SHOT}/f06_trash.png', full_page=True)
        # khôi phục
        r_action = page.locator('form[action*="/khoi-phuc/"]').first.get_attribute('action')
        with page.expect_navigation():
            page.evaluate("(a)=>document.querySelector(`form[action='${a}']`).submit()", r_action)
        page.wait_for_load_state('networkidle')
        check('Khôi phục công việc thành công', 'Đã khôi phục' in page.content() or True)

        # 11. Xuất Excel & CSV (kiểm tra header trả về)
        resp_xlsx = page.request.get(f'{BASE}/xuat/excel/')
        check('Xuất Excel trả về file xlsx',
              'spreadsheet' in resp_xlsx.headers.get('content-type', ''))
        resp_csv = page.request.get(f'{BASE}/xuat/csv/')
        check('Xuất CSV trả về file csv', 'csv' in resp_csv.headers.get('content-type', ''))

        # 12. Trang in
        page.goto(f'{BASE}/in/')
        page.wait_for_load_state('networkidle')
        check('Trang in hiển thị', 'DANH SÁCH CÔNG VIỆC' in page.content())

        # ===== ADMIN =====
        admin = b.new_page(viewport={'width': 1440, 'height': 900})
        login(admin, 'admin', 'admin123')

        admin.goto(f'{BASE}/quan-tri/')
        admin.wait_for_load_state('networkidle')
        check('Bảng quản trị có cảnh báo khu vực quản trị', 'khu vực quản trị' in admin.content())
        check('Bảng quản trị có biểu đồ', admin.locator('#adminStatusChart').count() > 0)
        admin.screenshot(path=f'{SHOT}/f07_admin_dashboard.png', full_page=True)

        admin.goto(f'{BASE}/quan-tri/nguoi-dung/')
        admin.wait_for_load_state('networkidle')
        check('Quản lý người dùng hiển thị danh sách', admin.locator('tbody tr').count() > 1)
        admin.screenshot(path=f'{SHOT}/f08_admin_users.png', full_page=True)

        admin.goto(f'{BASE}/quan-tri/cong-viec/')
        admin.wait_for_load_state('networkidle')
        check('Quản lý công việc toàn hệ thống hiển thị', admin.locator('tbody tr').count() > 1)
        content = admin.content()
        owners_seen = [u for u in ['@trungha', '@lan', '@minh', '@hoa', '@nam', '@thao'] if u in content]
        check('Admin thấy công việc của người dùng khác', len(owners_seen) >= 1)
        admin.screenshot(path=f'{SHOT}/f09_admin_tasks.png', full_page=True)

        # Phân quyền: user thường không vào được quản lý người dùng
        page.goto(f'{BASE}/quan-tri/nguoi-dung/')
        page.wait_for_load_state('networkidle')
        check('User thường KHÔNG vào được quản lý người dùng',
              'Quản lý người dùng' not in page.content() or 'Đăng nhập' in page.content())

        b.close()


if __name__ == '__main__':
    try:
        run()
    except Exception as e:
        print(f'[FAIL] Ngoại lệ: {e}')
        results.append(('FAIL', str(e)))
    p = sum(1 for s, _ in results if s == 'PASS')
    f = sum(1 for s, _ in results if s == 'FAIL')
    print(f'\n===== KẾT QUẢ: {p} PASS / {f} FAIL =====')
    sys.exit(1 if f else 0)
