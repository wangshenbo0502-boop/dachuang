"""Recruitment contracts using a private, disposable database and real HTTP APIs."""
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

import app.models
from app.database.connection import Base
from app.database.session import get_db
from app.database.bootstrap import ensure_compatibility_columns
from main import app


@pytest.fixture
def recruitment_api():
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    db = Session(engine)
    app.dependency_overrides[get_db] = lambda: db
    codes = {}
    with patch('app.api.auth._send_mail', side_effect=lambda email, code, purpose: codes.__setitem__(email, code)):
        with TestClient(app, raise_server_exceptions=False) as client:
            yield client, db, codes
    app.dependency_overrides.clear()
    db.close()
    engine.dispose()


def account(env, email, role='student'):
    client, _, codes = env
    assert client.post('/api/auth/email/send-code', json={'email': email}).status_code == 200
    result = client.post('/api/auth/register', json={
        'email': email, 'code': codes[email], 'password': 'correct-password',
        'confirm_password': 'correct-password', 'name': '验证用户', 'role': role,
    })
    assert result.status_code == 201, result.text
    data = result.json()['data']
    return data, {'Authorization': f"Bearer {data['access_token']}"}


PROFILE = {'company_name': '测试科技', 'industry': '软件', 'city': '成都', 'description': '验证企业简介',
           'contact_name': '招聘经理', 'contact_email': 'hr@example.com'}
JOB = {'title': 'Python 开发实习生', 'category': '后端', 'city': '成都', 'salary': '200元/天',
       'employment_type': '实习', 'education': '本科', 'experience': '不限',
       'description': '参与后端接口开发。', 'requirements': '掌握 Python 与 SQL。', 'tags': ['Python', 'SQL']}


def setup_job(env, email='111111111@qq.com'):
    client, _, _ = env
    identity, headers = account(env, email, 'recruiter')
    assert client.put('/api/recruiter/profile', headers=headers, json=PROFILE).status_code == 200
    result = client.post('/api/recruiter/jobs', headers=headers, json=JOB)
    assert result.status_code == 201, result.text
    return result.json()['data'], identity, headers


def publish(client, job, headers):
    response = client.post(f"/api/recruiter/jobs/{job['id']}/status", headers=headers, json={'status': 'published'})
    assert response.status_code == 200, response.text


def apply(env, job, email='222222222@qq.com'):
    client, _, _ = env
    student, headers = account(env, email)
    resume = client.post('/api/resume/versions', headers=headers, json={
        'user_id': student['user']['profile_id'], 'name': '测试简历', 'target_job': JOB['title'], 'personal_summary': '真实概要',
    })
    assert resume.status_code == 200, resume.text
    resume_id = resume.json()['data']['id']
    response = client.post(f"/api/recruitment/jobs/{job['id']}/apply", headers=headers, json={'resume_id': resume_id, 'note': '期待交流'})
    assert response.status_code == 201, response.text
    return response.json()['data'], student, headers, resume_id


def test_roles_registration_login_and_private_apis(recruitment_api):
    client, _, codes = recruitment_api
    recruiter, rh = account(recruitment_api, '333333333@qq.com', 'recruiter')
    assert recruiter['user']['role'] == 'recruiter'
    assert client.get('/api/auth/me', headers=rh).json()['data']['role'] == 'recruiter'
    login = client.post('/api/auth/login', json={'email': '333333333@qq.com', 'password': 'correct-password'})
    assert login.json()['data']['user']['role'] == 'recruiter'
    assert client.get(f"/api/users/{recruiter['user']['profile_id']}", headers=rh).status_code == 403
    assert client.post('/api/match', headers=rh, json={'skills': ['Python']}).status_code == 403
    assert client.get('/api/applications', headers=rh).status_code == 403
    student, sh = account(recruitment_api, '444444444@qq.com')
    assert student['user']['role'] == 'student'
    assert client.get('/api/recruiter/jobs', headers=sh).status_code == 403
    assert client.get('/api/recruiter/jobs').status_code == 401
    client.post('/api/auth/email/send-code', json={'email': '555555555@qq.com'})
    result = client.post('/api/auth/register', json={'email': '555555555@qq.com', 'code': codes['555555555@qq.com'],
        'password': 'correct-password', 'confirm_password': 'correct-password', 'role': 'admin'})
    assert result.status_code == 422


def test_default_role_and_migration_preserve_existing_data(recruitment_api):
    client, _, codes = recruitment_api
    client.post('/api/auth/email/send-code', json={'email': '666666666@qq.com'})
    response = client.post('/api/auth/register', json={'email': '666666666@qq.com', 'code': codes['666666666@qq.com'],
        'password': 'correct-password', 'confirm_password': 'correct-password'})
    assert response.json()['data']['user']['role'] == 'student'
    engine = create_engine('sqlite://')
    with engine.begin() as conn:
        conn.execute(text('CREATE TABLE accounts (id INTEGER PRIMARY KEY, email VARCHAR(100))'))
        conn.execute(text("INSERT INTO accounts VALUES (7, 'legacy@qq.com')"))
    assert ensure_compatibility_columns(engine) == ['accounts.role']
    assert ensure_compatibility_columns(engine) == []
    with engine.connect() as conn:
        assert conn.execute(text('SELECT id,email,role FROM accounts')).one() == (7, 'legacy@qq.com', 'student')
    engine.dispose()


def test_job_lifecycle_search_and_cross_recruiter_ownership(recruitment_api):
    client, _, _ = recruitment_api
    job, _, rh = setup_job(recruitment_api)
    _, sh = account(recruitment_api, '222222222@qq.com')
    assert client.get('/api/recruitment/jobs', headers=sh).json()['data']['total'] == 0
    assert client.get(f"/api/recruitment/jobs/{job['id']}", headers=sh).status_code == 404
    publish(client, job, rh)
    result = client.get('/api/recruitment/jobs', headers=sh, params={'keyword': 'Python', 'city': '成都', 'category': '后端'})
    assert result.json()['data']['total'] == 1
    assert client.get('/api/recruitment/jobs', headers=sh, params={'city': '上海'}).json()['data']['total'] == 0
    assert client.get(f"/api/recruitment/jobs/{job['id']}", headers=sh).json()['data']['company_name'] == PROFILE['company_name']
    assert client.put(f"/api/recruiter/jobs/{job['id']}", headers=rh, json=JOB).status_code == 409
    _, other = account(recruitment_api, '777777777@qq.com', 'recruiter')
    for method, path, payload in [('get', '', None), ('put', '', JOB), ('post', '/status', {'status': 'closed'}), ('delete', '', None)]:
        assert client.request(method, f"/api/recruiter/jobs/{job['id']}{path}", headers=other, json=payload).status_code == 404
    assert client.post(f"/api/recruiter/jobs/{job['id']}/status", headers=rh, json={'status': 'closed'}).status_code == 200
    assert client.get(f"/api/recruitment/jobs/{job['id']}", headers=sh).status_code == 404
    assert client.put(f"/api/recruiter/jobs/{job['id']}", headers=rh, json={**JOB, 'title': '更新岗位'}).status_code == 200
    assert client.delete(f"/api/recruiter/jobs/{job['id']}", headers=rh).status_code == 200


def test_publish_requires_complete_job_and_company(recruitment_api):
    client, _, _ = recruitment_api
    _, rh = account(recruitment_api, '111111111@qq.com', 'recruiter')
    job = client.post('/api/recruiter/jobs', headers=rh, json={'title': '草稿'}).json()['data']
    assert client.post(f"/api/recruiter/jobs/{job['id']}/status", headers=rh, json={'status': 'published'}).status_code == 400
    client.put(f"/api/recruiter/jobs/{job['id']}", headers=rh, json=JOB)
    assert client.post(f"/api/recruiter/jobs/{job['id']}/status", headers=rh, json={'status': 'published'}).status_code == 400
    assert client.put('/api/recruiter/profile', headers=rh, json={**PROFILE, 'contact_email': 'invalid'}).status_code == 422
    assert client.post('/api/recruiter/jobs', headers=rh, json={**JOB, 'recruiter_id': 999}).status_code == 422


def test_apply_snapshot_duplicate_resume_ownership_and_feedback(recruitment_api):
    client, _, _ = recruitment_api
    job, _, rh = setup_job(recruitment_api)
    publish(client, job, rh)
    application, student, sh, resume_id = apply(recruitment_api, job)
    path = f"/api/recruitment/jobs/{job['id']}/apply"
    assert client.post(path, headers=sh, json={'resume_id': resume_id}).status_code == 409
    _, other_student = account(recruitment_api, '333333333@qq.com')
    assert client.post(path, headers=other_student, json={'resume_id': resume_id}).status_code == 403
    assert client.post(path, headers=sh, json={'resume_id': resume_id, 'student_id': 999}).status_code == 422
    client.put(f'/api/resume/versions/{resume_id}', headers=sh, json={'personal_summary': '改后概要'})
    received = client.get('/api/recruiter/applications', headers=rh).json()['data']['items'][0]
    assert received['resume_snapshot']['personal_summary'] == '真实概要'
    assert received['note'] == '期待交流'
    _, other_recruiter = account(recruitment_api, '444444444@qq.com', 'recruiter')
    assert client.get('/api/recruiter/applications', headers=other_recruiter).json()['data']['total'] == 0
    target = f"/api/recruiter/applications/{application['id']}"
    assert client.patch(target, headers=other_recruiter, json={'status': 'reviewing', 'feedback': '偷看'}).status_code == 404
    assert client.patch(target, headers=rh, json={'status': 'interview', 'feedback': '请联系招聘经理安排面试'}).status_code == 200
    mine = client.get('/api/recruitment/applications', headers=sh).json()['data']['items'][0]
    assert mine['status'] == 'interview'
    assert mine['feedback'] == '请联系招聘经理安排面试'
    assert client.get('/api/recruitment/applications', headers=other_student).json()['data']['total'] == 0
    assert client.post(f"/api/recruitment/applications/{application['id']}/withdraw", headers=other_student).status_code == 404
    assert client.delete(f"/api/recruiter/jobs/{job['id']}", headers=rh).status_code == 409
    client.post(f"/api/recruiter/jobs/{job['id']}/status", headers=rh, json={'status': 'closed'})
    assert client.delete(f"/api/recruiter/jobs/{job['id']}", headers=rh).status_code == 409
    assert client.post(path, headers=other_student, json={'resume_id': resume_id}).status_code == 404
    assert client.get('/api/recruitment/applications', headers=sh).json()['data']['total'] == 1


@pytest.mark.parametrize('terminal', ['offered', 'rejected', 'withdrawn'])
def test_terminal_statuses_cannot_be_reopened(recruitment_api, terminal):
    client, _, _ = recruitment_api
    job, _, rh = setup_job(recruitment_api)
    publish(client, job, rh)
    application, _, sh, _ = apply(recruitment_api, job)
    target = f"/api/recruiter/applications/{application['id']}"
    if terminal == 'withdrawn':
        assert client.post(f"/api/recruitment/applications/{application['id']}/withdraw", headers=sh).status_code == 200
    else:
        if terminal == 'offered':
            client.patch(target, headers=rh, json={'status': 'interview', 'feedback': ''})
        assert client.patch(target, headers=rh, json={'status': terminal, 'feedback': '处理结果'}).status_code == 200
    assert client.patch(target, headers=rh, json={'status': 'reviewing', 'feedback': '重新开始'}).status_code == 409
    assert client.post(f"/api/recruitment/applications/{application['id']}/withdraw", headers=sh).status_code == 409


def test_pagination_and_invalid_status(recruitment_api):
    client, _, _ = recruitment_api
    job, _, rh = setup_job(recruitment_api)
    publish(client, job, rh)
    application, _, sh, _ = apply(recruitment_api, job)
    client.post('/api/recruiter/jobs', headers=rh, json=JOB)
    page = client.get('/api/recruiter/jobs', headers=rh, params={'page_size': 1, 'page': 2}).json()['data']
    assert page['total'] == 2 and len(page['items']) == 1
    assert client.get('/api/recruitment/jobs', headers=sh, params={'page': 0}).status_code == 422
    assert client.patch(f"/api/recruiter/applications/{application['id']}", headers=rh, json={'status': 'withdrawn'}).status_code == 422
    assert client.patch(f"/api/recruiter/applications/{application['id']}", headers=rh, json={'status': 'offered'}).status_code == 409


def test_only_selected_resume_entries_are_shared(recruitment_api):
    client, _, _ = recruitment_api
    job, _, rh = setup_job(recruitment_api)
    publish(client, job, rh)
    student, sh = account(recruitment_api, '222222222@qq.com')
    uid = student['user']['profile_id']
    skills = client.put(f'/api/users/{uid}/skills', headers=sh, json={'skills': [
        {'name': 'Python', 'proficiency': '熟悉', 'description': '允许分享'},
        {'name': '私人技能', 'proficiency': '了解', 'description': '不分享'},
    ]}).json()['data']
    version = client.post('/api/resume/versions', headers=sh, json={
        'user_id': uid, 'name': '选择性分享', 'target_job': '后端', 'selected_skills': [skills[0]['id']],
    }).json()['data']
    result = client.post(f"/api/recruitment/jobs/{job['id']}/apply", headers=sh, json={'resume_id': version['id']})
    assert result.status_code == 201, result.text
    snapshot = result.json()['data']['resume_snapshot']
    assert [skill['name'] for skill in snapshot['profile']['skills']] == ['Python']
    assert '私人技能' not in str(snapshot)
    assert 'user_id' not in str(snapshot)


def test_job_search_includes_skill_tags(recruitment_api):
    client, _, _ = recruitment_api
    job, _, rh = setup_job(recruitment_api)
    client.put(f"/api/recruiter/jobs/{job['id']}", headers=rh, json={**JOB, 'tags': ['Kubernetes']})
    publish(client, job, rh)
    _, sh = account(recruitment_api, '222222222@qq.com')
    assert client.get('/api/recruitment/jobs', headers=sh, params={'keyword': 'Kubernetes'}).json()['data']['total'] == 1


def test_snapshot_preserves_accepted_resume_expression(recruitment_api):
    client, _, _ = recruitment_api
    job, _, rh = setup_job(recruitment_api)
    publish(client, job, rh)
    student, sh = account(recruitment_api, '222222222@qq.com')
    uid = student['user']['profile_id']
    project = client.put(f'/api/users/{uid}/projects', headers=sh, json={'projects': [
        {'name': '已选项目', 'role': '开发', 'description': '档案描述', 'tech_stack': ['Python']},
    ]}).json()['data'][0]
    version = client.post('/api/resume/versions', headers=sh, json={
        'user_id': uid, 'name': '优化后简历', 'target_job': '后端', 'selected_projects': [project['id']],
        'optimized_content': {'optimized_projects': [{'project_name': '已选项目', 'optimized': '用户采纳的简历表达'}]},
    }).json()['data']
    result = client.post(f"/api/recruitment/jobs/{job['id']}/apply", headers=sh, json={'resume_id': version['id']})
    assert result.json()['data']['resume_snapshot']['profile']['projects'][0]['description'] == '用户采纳的简历表达'


def test_inactive_recruiter_vacancies_are_unavailable(recruitment_api):
    from app.models.account import Account
    client, db, _ = recruitment_api
    job, identity, rh = setup_job(recruitment_api)
    publish(client, job, rh)
    _, sh = account(recruitment_api, '222222222@qq.com')
    db.get(Account, identity['user']['id']).is_active = False
    db.commit()
    assert client.get('/api/recruitment/jobs', headers=sh).json()['data']['total'] == 0
    assert client.get(f"/api/recruitment/jobs/{job['id']}", headers=sh).status_code == 404
