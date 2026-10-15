"""Fictional recruiter accounts and vacancies for local demos of 站内招聘.

Every company here is invented and labelled "（示例）" so demo data is never
mistaken for a real employer. Seeding is idempotent: accounts are matched by
email and vacancies by (recruiter, title), so re-running only fills gaps.
"""
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.security import hash_password
from app.models.account import Account
from app.models.recruitment import RecruiterProfile, RecruitmentJob
from app.models.user import User
from app.schemas.recruitment import RecruiterProfileInput, RecruitmentJobInput

DEMO_NOTICE = "本企业为系统演示用的虚构企业，岗位信息仅用于功能展示，不代表真实招聘。"


def _job(title, category, city, salary, employment_type, education, experience, duties, requirements, tags):
    return {
        "title": title, "category": category, "city": city, "salary": salary,
        "employment_type": employment_type, "education": education, "experience": experience,
        "description": duties, "requirements": requirements, "tags": tags,
    }


DEMO_COMPANIES = [
    {
        "email": "demo-recruiter-01@qq.com",
        "profile": {
            "company_name": "星河云科技（示例）", "industry": "云计算 / 企业服务", "city": "杭州",
            "description": "面向中小企业提供云原生 SaaS 平台。" + DEMO_NOTICE,
            "contact_name": "林老师（示例）", "contact_email": "demo-recruiter-01@qq.com",
        },
        "jobs": [
            _job("Java 后端开发实习生", "后端", "杭州", "200-260元/天", "实习", "本科", "在校生",
                 "参与 SaaS 平台订单与计费模块开发；编写接口文档与单元测试；配合排查线上问题。",
                 "计算机相关专业；熟悉 Java 与 Spring Boot；了解 MySQL 索引与事务；每周可实习 4 天以上。",
                 ["Java", "Spring Boot", "MySQL", "Redis", "Git"]),
            _job("前端开发工程师（校招）", "前端", "杭州", "12-18K·14薪", "全职", "本科", "应届生",
                 "负责管理后台与数据看板开发；与设计、后端协作完成需求；沉淀通用组件。",
                 "熟悉 Vue 3 或 React；掌握 TypeScript；了解浏览器渲染与性能优化；有完整项目经历。",
                 ["Vue", "TypeScript", "JavaScript", "CSS", "Vite"]),
            _job("云原生运维实习生", "运维", "杭州", "180-220元/天", "实习", "本科", "在校生",
                 "协助维护 Kubernetes 集群与 CI/CD 流水线；编写自动化脚本；整理监控告警规则。",
                 "熟悉 Linux 常用命令；了解 Docker 与 Kubernetes 基本概念；会 Shell 或 Python 脚本。",
                 ["Linux", "Docker", "Kubernetes", "Shell", "Python"]),
            _job("软件测试工程师（校招）", "测试", "杭州", "9-13K", "全职", "本科", "应届生",
                 "设计功能与接口测试用例；维护自动化测试脚本；跟踪缺陷并推动修复。",
                 "了解软件测试流程与用例设计方法；会使用 Postman 或 JMeter；有 Python 自动化经验优先。",
                 ["Python", "Postman", "Selenium", "SQL", "Linux"]),
        ],
    },
    {
        "email": "demo-recruiter-02@qq.com",
        "profile": {
            "company_name": "青藤智能（示例）", "industry": "人工智能", "city": "北京",
            "description": "专注大模型应用与智能客服产品。" + DEMO_NOTICE,
            "contact_name": "周老师（示例）", "contact_email": "demo-recruiter-02@qq.com",
        },
        "jobs": [
            _job("大模型应用开发实习生", "AI", "北京", "300-400元/天", "实习", "本科", "在校生",
                 "基于大模型搭建 RAG 问答与 Agent 工作流；评估检索与回答质量；编写服务端接口。",
                 "熟悉 Python；了解 Prompt 设计、向量检索与 RAG 基本原理；有 LangChain 或类似项目经历优先。",
                 ["Python", "LLM", "RAG", "FastAPI", "向量数据库"]),
            _job("机器学习算法工程师（校招）", "AI", "北京", "25-35K·15薪", "全职", "硕士", "应届生",
                 "负责意图识别与对话推荐模型的训练和优化；搭建离线评估体系；推进模型上线。",
                 "机器学习、深度学习基础扎实；熟练使用 PyTorch；有 NLP 方向论文或竞赛成果优先。",
                 ["Python", "PyTorch", "NLP", "深度学习", "机器学习"]),
            _job("AI 产品经理实习生", "产品", "北京", "200-250元/天", "实习", "本科", "在校生",
                 "参与智能客服产品需求调研与竞品分析；撰写 PRD；跟进模型效果评测与用户反馈。",
                 "对大模型产品有兴趣；逻辑清晰、表达良好；会使用 Axure 或 Figma；有数据分析能力优先。",
                 ["产品设计", "需求分析", "Axure", "数据分析", "LLM"]),
            _job("Python 后端开发工程师", "后端", "北京", "18-28K", "全职", "本科", "1-3年",
                 "负责模型服务网关、会话存储和计费接口开发；优化服务性能与稳定性。",
                 "熟练掌握 Python 与 FastAPI 或 Django；熟悉 PostgreSQL、Redis；了解异步编程与消息队列。",
                 ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker"]),
        ],
    },
    {
        "email": "demo-recruiter-03@qq.com",
        "profile": {
            "company_name": "海川数据（示例）", "industry": "大数据 / 金融科技", "city": "上海",
            "description": "为金融机构提供数据中台与风控分析服务。" + DEMO_NOTICE,
            "contact_name": "陈老师（示例）", "contact_email": "demo-recruiter-03@qq.com",
        },
        "jobs": [
            _job("数据分析实习生", "数据", "上海", "200-280元/天", "实习", "本科", "在校生",
                 "完成业务指标统计与专题分析；搭建数据看板；输出分析报告与改进建议。",
                 "熟练使用 SQL；会用 Python（Pandas）或 Excel 做数据处理；统计学基础良好。",
                 ["SQL", "Python", "Pandas", "数据可视化", "统计学"]),
            _job("大数据开发工程师（校招）", "数据", "上海", "16-24K·14薪", "全职", "本科", "应届生",
                 "参与数据仓库建模与 ETL 任务开发；维护实时计算链路；保障数据质量。",
                 "熟悉 Java 或 Scala；了解 Hadoop、Spark、Flink 中至少一种；熟悉 SQL 与数仓分层理念。",
                 ["Spark", "Hadoop", "Flink", "SQL", "Java"]),
            _job("风控策略分析师", "数据", "上海", "15-22K", "全职", "硕士", "1-3年",
                 "基于交易数据设计反欺诈与信用风控策略；监控策略效果并持续迭代。",
                 "统计、数学或计算机相关专业；熟练使用 SQL 与 Python；了解常用分类模型与评估指标。",
                 ["SQL", "Python", "机器学习", "风控", "统计学"]),
            _job("Go 后端开发实习生", "后端", "上海", "250-300元/天", "实习", "本科", "在校生",
                 "参与数据服务 API 与任务调度系统开发；编写单元测试；参与代码评审。",
                 "熟悉 Go 或愿意快速学习；了解 HTTP、RPC 与 MySQL；有开源或课程项目经历。",
                 ["Go", "MySQL", "gRPC", "Linux", "Git"]),
        ],
    },
    {
        "email": "demo-recruiter-04@qq.com",
        "profile": {
            "company_name": "北辰互娱（示例）", "industry": "游戏 / 移动互联网", "city": "深圳",
            "description": "研发休闲手游与小程序游戏。" + DEMO_NOTICE,
            "contact_name": "黄老师（示例）", "contact_email": "demo-recruiter-04@qq.com",
        },
        "jobs": [
            _job("Android 开发工程师（校招）", "移动端", "深圳", "15-22K·14薪", "全职", "本科", "应届生",
                 "负责游戏社区 App 功能开发与性能优化；跟进崩溃与卡顿问题。",
                 "熟悉 Kotlin 或 Java；了解 Android 组件与生命周期；有上架应用或完整项目优先。",
                 ["Kotlin", "Java", "Android", "Jetpack", "Git"]),
            _job("小程序前端开发实习生", "前端", "深圳", "180-240元/天", "实习", "不限", "在校生",
                 "参与微信小程序游戏活动页开发；还原设计稿；配合联调接口。",
                 "熟悉 JavaScript 与 CSS；了解微信小程序开发；做过个人作品或课程项目。",
                 ["JavaScript", "微信小程序", "CSS", "Vue", "Git"]),
            _job("游戏运营实习生", "运营", "深圳", "150-200元/天", "实习", "本科", "在校生",
                 "策划并执行线上活动；整理玩家反馈；跟踪留存、付费等运营数据。",
                 "热爱游戏、沟通能力强；会用 Excel 做数据整理；有社团或活动组织经历优先。",
                 ["活动策划", "数据分析", "Excel", "用户运营"]),
        ],
    },
    {
        "email": "demo-recruiter-05@qq.com",
        "profile": {
            "company_name": "启明安全（示例）", "industry": "网络安全", "city": "成都",
            "description": "提供企业安全评估、渗透测试与安全运营服务。" + DEMO_NOTICE,
            "contact_name": "王老师（示例）", "contact_email": "demo-recruiter-05@qq.com",
        },
        "jobs": [
            _job("安全测试实习生", "安全", "成都", "180-250元/天", "实习", "本科", "在校生",
                 "在授权范围内参与 Web 应用安全测试；复现并整理漏洞报告；协助修复验证。",
                 "了解 OWASP Top 10；会使用 Burp Suite；有 CTF 参赛经历优先。",
                 ["Web安全", "Burp Suite", "Python", "Linux", "CTF"]),
            _job("安全开发工程师（校招）", "安全", "成都", "13-18K", "全职", "本科", "应届生",
                 "开发漏洞扫描与资产管理平台；编写检测插件；维护规则库。",
                 "熟悉 Python 或 Go；了解常见 Web 漏洞原理；熟悉 HTTP 协议与 Linux。",
                 ["Python", "Go", "Web安全", "Linux", "HTTP"]),
            _job("Linux 运维工程师", "运维", "成都", "10-15K", "全职", "大专", "1-3年",
                 "负责客户环境部署与巡检；维护监控、日志与备份系统；处理故障工单。",
                 "熟悉 Linux 系统管理；会 Shell 脚本；了解 Nginx、MySQL 运维；有 RHCE 等证书优先。",
                 ["Linux", "Shell", "Nginx", "MySQL", "Zabbix"]),
        ],
    },
]


def seed_demo_recruitment(db: Session, password: str) -> dict[str, int]:
    """Create or refresh demo recruiters, then publish any missing demo vacancies."""
    if len(password) < 8:
        raise ValueError("演示账号密码至少 8 位")
    password_hash = hash_password(password)
    now = datetime.now(timezone.utc)
    created_accounts = created_jobs = 0
    for company in DEMO_COMPANIES:
        email = company["email"]
        profile_data = RecruiterProfileInput(**company["profile"]).model_dump()
        account = db.scalar(select(Account).where(Account.email == email))
        if account is None:
            person = User(name=profile_data["contact_name"], school="—", major="—", grade="—", email=email)
            db.add(person)
            db.flush()
            account = Account(username=email.split("@")[0], email=email, password_hash=password_hash,
                              profile_id=person.id, email_verified=True, role="recruiter")
            db.add(account)
            db.flush()
            created_accounts += 1
        elif account.role != "recruiter":
            db.rollback()
            raise ValueError(f"{email} 已被非招聘者账号占用，未写入任何演示数据")
        else:
            # Re-running sets the password given this time and signs out old sessions.
            account.password_hash = password_hash
            account.token_version += 1

        profile = db.get(RecruiterProfile, account.id)
        if profile is None:
            profile = RecruiterProfile(account_id=account.id)
            db.add(profile)
        for key, value in profile_data.items():
            setattr(profile, key, value)

        existing = set(db.scalars(select(RecruitmentJob.title).where(RecruitmentJob.recruiter_id == account.id)))
        for job in company["jobs"]:
            if job["title"] in existing:
                continue
            fields = RecruitmentJobInput(**job).model_dump()
            db.add(RecruitmentJob(recruiter_id=account.id, company_name=profile_data["company_name"],
                                  status="published", moderation_status="allowed", published_at=now, **fields))
            created_jobs += 1
    db.commit()
    return {
        "companies": len(DEMO_COMPANIES),
        "jobs": sum(len(company["jobs"]) for company in DEMO_COMPANIES),
        "created_accounts": created_accounts,
        "created_jobs": created_jobs,
    }
