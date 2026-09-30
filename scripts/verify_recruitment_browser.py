"""Real browser recruitment smoke against private temporary data and processes.

Run from repository root after npm ci:
  python scripts/verify_recruitment_browser.py
Uses existing Microsoft Edge. Never starts SMTP, AI, BOSS or knowledge services.
"""
from __future__ import annotations
import json
import os
import re
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timedelta, timezone
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'docs' / 'verification' / 'recruitment'


def free_port():
    with socket.socket() as sock:
        sock.bind(('127.0.0.1', 0))
        return sock.getsockname()[1]


def ready(url, process):
    for _ in range(120):
        if process.poll() is not None:
            raise RuntimeError('Verification service exited; inspect server logs')
        try:
            with urlopen(url, timeout=1) as response:
                if response.status == 200:
                    return
        except Exception:
            time.sleep(0.25)
    raise RuntimeError('Verification service did not become ready')


def field(page, label, value):
    page.get_by_label(label, exact=True).fill(value)


def select(page, label, value):
    page.get_by_label(label, exact=True).locator('xpath=ancestor::div[contains(@class,"el-select__wrapper")][1]').click()
    page.get_by_role('option', name=value, exact=True).click()


def token(page):
    return page.evaluate("localStorage.getItem('employment-platform-access-token')")


def capture(page, path):
    # Wait for actual route entry and toast transitions before documenting
    # the rendered page; do not modify application styles for screenshots.
    page.wait_for_function("!document.querySelector('.page-fade-enter-active, .page-fade-leave-active')")
    page.locator('.el-message').last.wait_for(state='hidden', timeout=10000) if page.locator('.el-message').count() else None
    page.screenshot(path=str(path), full_page=True, animations='disabled')


def authorized(page, path, *, body=None, method='get'):
    response = getattr(page.request, method)(path, headers={'Authorization': f'Bearer {token(page)}'}, data=body)
    assert response.ok, response.text()
    return response.json()['data']


def main():
    from playwright.sync_api import sync_playwright, expect
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / 'browser-results.json').unlink(missing_ok=True)
    backend_port, frontend_port = free_port(), free_port()
    backend_url = f'http://127.0.0.1:{backend_port}'
    frontend_url = f'http://127.0.0.1:{frontend_port}'
    checks, errors = [], []
    processes = []
    with tempfile.TemporaryDirectory(prefix='dachuang-recruitment-') as temporary:
        env = os.environ.copy()
        env.update({'DATABASE_URL': f'sqlite:///{Path(temporary).as_posix()}/verification.db',
            'APP_ENV': 'testing', 'JWT_SECRET': secrets.token_hex(32), 'DEEPSEEK_API_KEY': '',
            'KNOWLEDGE_DATABASE_URL': '', 'RATE_LIMIT_ENABLED': 'false', 'LOG_LEVEL': 'WARNING'})
        # A private code fixture verifies the actual registration form and
        # email-code consumption without claiming live QQ mail delivery.
        os.environ.update(env)
        sys.path.insert(0, str(ROOT / 'backend'))
        from app.database.bootstrap import initialize_database_schema
        from app.database.session import get_session_factory
        from app.models.account import EmailCode
        from app.auth.security import hash_code
        initialize_database_schema()
        with get_session_factory()() as db:
            now = datetime.now(timezone.utc)
            for email in ('991000001@qq.com', '991000002@qq.com'):
                db.add(EmailCode(email=email, purpose='REGISTER', code_hash=hash_code(email, 'REGISTER', '123456'),
                    expires_at=now + timedelta(hours=1), sent_at=now, day=now.date().isoformat(), daily_count=1, failed_attempts=0))
            db.commit()
        # A temporary Vite configuration keeps the repository proxy untouched.
        frontend_root = ROOT / 'frontend'
        vite_config = Path(temporary) / 'verification-vite.mjs'
        vite_module = (frontend_root / 'node_modules/vite/dist/node/index.js').as_uri()
        vue_module = (frontend_root / 'node_modules/@vitejs/plugin-vue/dist/index.mjs').as_uri()
        vite_config.write_text(f"import {{defineConfig}} from {json.dumps(vite_module)};\nimport vue from {json.dumps(vue_module)};\nexport default defineConfig({{root:{json.dumps(frontend_root.as_posix())},plugins:[vue()],resolve:{{alias:{{'@':{json.dumps((frontend_root/'src').as_posix())}}}}},server:{{host:'127.0.0.1',port:{frontend_port},strictPort:true,proxy:{{'/api':{json.dumps(backend_url)}}}}}}});", encoding='utf-8')
        flags = subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        with (OUTPUT / 'backend.log').open('w', encoding='utf-8') as backend_log, (OUTPUT / 'frontend.log').open('w', encoding='utf-8') as frontend_log:
            try:
                backend = subprocess.Popen([sys.executable, '-m', 'uvicorn', 'main:app', '--host', '127.0.0.1', '--port', str(backend_port)], cwd=ROOT / 'backend', env=env, stdout=backend_log, stderr=subprocess.STDOUT, creationflags=flags)
                processes.append(backend)
                frontend = subprocess.Popen(['node', str(frontend_root / 'node_modules/vite/bin/vite.js'), '--config', str(vite_config)], cwd=frontend_root, env=env, stdout=frontend_log, stderr=subprocess.STDOUT, creationflags=flags)
                processes.append(frontend)
                ready(backend_url + '/api/health', backend)
                ready(frontend_url, frontend)
                with sync_playwright() as p:
                    browser = p.chromium.launch(channel='msedge', headless=True)
                    recruiter_context = browser.new_context(viewport={'width': 1440, 'height': 1000}, base_url=frontend_url)
                    student_context = browser.new_context(viewport={'width': 1440, 'height': 1000}, base_url=frontend_url)
                    recruiter, student = recruiter_context.new_page(), student_context.new_page()
                    for page in (recruiter, student):
                        page.set_default_timeout(12000)
                        page.on('pageerror', lambda exc: errors.append(str(exc)))
                    recruiter.goto('/register?redirect=/profile')
                    recruiter.get_by_text('招聘者', exact=True).click()
                    field(recruiter, 'QQ 邮箱', '991000001@qq.com')
                    field(recruiter, '验证码', '123456')
                    field(recruiter, '姓名（可选）', '验证招聘经理')
                    field(recruiter, '密码', 'verification-password')
                    field(recruiter, '确认密码', 'verification-password')
                    recruiter.get_by_role('button', name='注册并进入', exact=True).click()
                    expect(recruiter).to_have_url(frontend_url + '/recruiter')
                    expect(recruiter.get_by_text('暂无招聘岗位', exact=True)).to_be_visible()
                    recruiter.reload()
                    expect(recruiter.get_by_role('tab', name='企业资料')).to_be_visible()
                    recruiter.get_by_role('button', name='打开个人菜单').click()
                    recruiter.get_by_text('退出登录', exact=True).click()
                    expect(recruiter).to_have_url(frontend_url + '/login')
                    field(recruiter, 'QQ 邮箱', '991000001@qq.com')
                    field(recruiter, '密码', 'verification-password')
                    recruiter.get_by_role('button', name='登录', exact=True).click()
                    expect(recruiter).to_have_url(frontend_url + '/recruiter')
                    checks.append('recruiter signup, login, logout, default redirect, refresh and honest empty state')
                    recruiter.get_by_role('button', name='创建岗位', exact=True).click()
                    field(recruiter, '岗位名称', '未完成草稿（验证）')
                    recruiter.get_by_role('button', name='保存并发布', exact=True).click()
                    recruiter.get_by_role('dialog', name='发布岗位').get_by_role('button', name='保存并发布', exact=True).click()
                    expect(recruiter).to_have_url(re.compile(r'/recruiter/jobs/\d+/edit\?publish_error='))
                    expect(recruiter.locator('.el-alert').get_by_text(re.compile('发布前请补充'))).to_be_visible()
                    expect(recruiter.get_by_label('岗位名称', exact=True)).to_have_value('未完成草稿（验证）')
                    drafts = authorized(recruiter, '/api/recruiter/jobs')['items']
                    assert len(drafts) == 1 and drafts[0]['status'] == 'draft'
                    authorized(recruiter, f"/api/recruiter/jobs/{drafts[0]['id']}", method='delete')
                    checks.append('failed publication preserves saved draft, input and visible validation message')
                    recruiter.goto('/recruiter?tab=profile')
                    recruiter.get_by_role('tab', name='企业资料').click()
                    for label, value in {'企业名称': '验证科技有限公司', '所属行业': '软件与信息服务', '企业所在城市': '成都',
                        '联系人': '验证招聘经理', '联系邮箱': 'hr@example.com', '企业简介': '浏览器验证专用企业资料，不代表真实招聘。'}.items():
                        field(recruiter, label, value)
                    recruiter.get_by_role('button', name='保存企业资料', exact=True).click()
                    expect(recruiter.get_by_text('企业资料已保存', exact=True)).to_be_visible()
                    recruiter.get_by_role('button', name='创建岗位', exact=True).click()
                    field(recruiter, '岗位名称', '前端开发实习生（验证）')
                    select(recruiter, '岗位分类', '前端')
                    field(recruiter, '工作城市', '成都')
                    field(recruiter, '薪资说明', '200–300 元/天')
                    field(recruiter, '技能标签', 'Vue、TypeScript')
                    field(recruiter, '岗位职责', '参与 Vue 界面开发与交互维护。\n和团队共同完成业务页面。')
                    field(recruiter, '任职要求', '了解 Vue 3 和 TypeScript，愿意学习。')
                    recruiter.get_by_role('button', name='保存并发布', exact=True).click()
                    recruiter.get_by_role('dialog', name='发布岗位').get_by_role('button', name='保存并发布', exact=True).click()
                    expect(recruiter).to_have_url(frontend_url + '/recruiter')
                    expect(recruiter.locator('.el-table').get_by_text('招聘中', exact=True)).to_be_visible()
                    capture(recruiter, OUTPUT / 'recruiter-desktop.png')
                    jobs = authorized(recruiter, '/api/recruiter/jobs')['items']
                    job_id = jobs[0]['id']
                    checks.append('company profile saved, job created and published through UI')
                    student.goto('/register?redirect=/recruitment')
                    field(student, 'QQ 邮箱', '991000002@qq.com')
                    field(student, '验证码', '123456')
                    field(student, '姓名（可选）', '验证同学')
                    field(student, '密码', 'verification-password')
                    field(student, '确认密码', 'verification-password')
                    student.get_by_role('button', name='注册并进入', exact=True).click()
                    expect(student).to_have_url(frontend_url + '/recruitment')
                    expect(student.get_by_role('link', name='查看岗位：前端开发实习生（验证）')).to_be_visible()
                    identity = authorized(student, '/api/auth/me')
                    # Seed a real version through the existing authenticated API;
                    # the feature under test is selection/preview/submission.
                    authorized(student, '/api/resume/versions', method='post', body={
                        'user_id': identity['profile_id'], 'name': '前端实习简历（验证）', 'target_job': '前端开发',
                        'personal_summary': '验证专用简历概要，愿意学习 Vue 与 TypeScript。'})
                    student.get_by_placeholder('搜索岗位、企业或技能').fill('前端')
                    student.get_by_role('button', name='搜索', exact=True).click()
                    expect(student.get_by_text('共 1 个招聘岗位', exact=True)).to_be_visible()
                    capture(student, OUTPUT / 'student-jobs-desktop.png')
                    student.get_by_role('link', name='查看岗位：前端开发实习生（验证）').click()
                    student.get_by_role('button', name='投递简历', exact=True).click()
                    expect(student.get_by_role('button', name='确认投递', exact=True)).to_be_disabled()
                    expect(student.get_by_text('验证专用简历概要，愿意学习 Vue 与 TypeScript。', exact=True)).to_be_visible()
                    student.get_by_text('我确认将上方简历及联系方式分享给该岗位招聘者', exact=True).click()
                    student.get_by_role('button', name='确认投递', exact=True).click()
                    expect(student.get_by_role('button', name='查看投递进度', exact=True)).to_be_visible()
                    checks.append('student role signup, job filtering, resume preview, consent and application')
                    recruiter.goto('/recruiter?tab=applications')
                    recruiter.get_by_role('button', name='查看简历', exact=True).click()
                    expect(recruiter.get_by_text('验证专用简历概要，愿意学习 Vue 与 TypeScript。', exact=True)).to_be_visible()
                    select(recruiter, '处理状态', '面试中')
                    field(recruiter, '给学生的反馈', '请通过联系邮箱沟通面试时间（验证）。')
                    recruiter.get_by_role('button', name='保存处理结果', exact=True).click()
                    expect(recruiter.get_by_role('dialog', name='查看投递简历')).not_to_be_visible()
                    capture(recruiter, OUTPUT / 'recruiter-applications-desktop.png')
                    student.get_by_role('button', name='查看投递进度', exact=True).click()
                    expect(student.get_by_text('面试中', exact=True)).to_be_visible()
                    expect(student.get_by_text('招聘反馈：请通过联系邮箱沟通面试时间（验证）。', exact=True)).to_be_visible()
                    capture(student, OUTPUT / 'student-applications-desktop.png')
                    checks.append('recruiter reads submitted snapshot and saves interview feedback; student sees it')
                    student.get_by_role('button', name='撤回投递', exact=True).click()
                    student.get_by_role('dialog', name='撤回投递').get_by_role('button', name='撤回', exact=True).click()
                    expect(student.get_by_text('已撤回', exact=True)).to_be_visible()
                    recruiter.goto('/recruiter')
                    recruiter.get_by_role('button', name='下架', exact=True).click()
                    recruiter.get_by_role('dialog', name='下架岗位').get_by_role('button', name='下架', exact=True).click()
                    expect(recruiter.locator('.el-table').get_by_text('已下架', exact=True)).to_be_visible()
                    student.goto('/recruitment')
                    expect(student.get_by_text('暂无符合条件的招聘岗位', exact=True)).to_be_visible()
                    student.goto(f'/recruitment/jobs/{job_id}')
                    expect(student.get_by_text('岗位不存在或已下架', exact=True)).to_be_visible()
                    checks.append('withdrawal, vacancy closing and unavailable old detail URL')
                    recruiter.goto('/profile')
                    expect(recruiter).to_have_url(frontend_url + '/recruiter')
                    student.goto('/recruiter')
                    expect(student).to_have_url(frontend_url + '/dashboard')
                    recruiter.goto('/settings')
                    expect(recruiter.get_by_text('当前招聘者', exact=True)).to_be_visible()
                    checks.append('role route guards and recruiter settings')
                    # Republish for non-empty mobile screenshots.
                    authorized(recruiter, f'/api/recruiter/jobs/{job_id}/status', method='post', body={'status': 'published'})
                    for page, path, filename in [(recruiter, '/recruiter', 'recruiter-mobile.png'), (student, '/recruitment', 'student-jobs-mobile.png')]:
                        page.set_viewport_size({'width': 390, 'height': 844})
                        page.goto(path)
                        expect((page.get_by_role('tabpanel', name='岗位管理').locator('.mobile-list') if page is recruiter else page).get_by_text('前端开发实习生（验证）', exact=True)).to_be_visible()
                        capture(page, OUTPUT / filename)
                        assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth'), 'Horizontal page overflow'
                    checks.append('390px mobile layouts without page overflow')
                    assert not errors, errors
                    checks.append('no browser page exceptions')
                    browser.close()
                result = {'status': 'passed', 'checks': checks, 'browser_errors': errors,
                    'database': 'private temporary SQLite, removed after run', 'email': 'verification code fixture; no live SMTP',
                    'screenshots': sorted(path.name for path in OUTPUT.glob('*.png'))}
                (OUTPUT / 'browser-results.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
                (OUTPUT / 'last-failure.json').unlink(missing_ok=True)
                print(json.dumps(result, ensure_ascii=False, indent=2))
            except Exception as exc:
                (OUTPUT / 'last-failure.json').write_text(json.dumps({'error': str(exc), 'completed_checks': checks}, ensure_ascii=False, indent=2), encoding='utf-8')
                raise
            finally:
                for process in reversed(processes):
                    if process.poll() is None:
                        process.terminate()
                        try: process.wait(timeout=10)
                        except subprocess.TimeoutExpired: process.kill(); process.wait(timeout=10)
                from app.database.connection import get_engine
                get_engine().dispose()


if __name__ == '__main__':
    main()
