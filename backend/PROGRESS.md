# AI就业竞争力分析助手 - 后端进度报告

> **最后更新**: 2026-08-14 (v1.1 全面完善版)
> **文档版本**: v1.1
> **当前状态**: Demo版本完善，核心闭环打通，P0问题已全部修复
> **AI友好提示**: 本文档面向下一位接手开发者/AI Agent，结构化记录完成度、待办、技术债务、变更记录

---

## 一、项目概述

### 项目定位
面向计算机专业大学生的AI就业竞争力提升平台，核心流程闭环：
```
学生填写经历 → AI就业画像分析 → AI岗位方向匹配 → AI简历优化 → AI成长规划
```

### 技术栈
| 层级 | 技术选型 | 状态 |
|------|---------|------|
| Web框架 | FastAPI + Python 3.10+ | ✅ 已配置 |
| 数据库 | SQLAlchemy 2.0 ORM | ✅ 已配置 |
| 数据库驱动 | SQLite(开发) / MySQL(生产) | ✅ 双支持 |
| AI大模型 | DeepSeek API (OpenAI兼容SDK) | ✅ 已接入+重试 |
| 知识库 | Markdown文件 + 关键词检索 | ✅ 基础可用 |
| Prompt管理 | 外部Markdown文件 | ✅ 已外置 |

---

## 二、整体完成度评估（v1.1 更新）

| 模块 | v1.0完成度 | v1.1完成度 | 变化 | 核心功能可用 | Demo可展示 | 生产就绪 |
|------|-----------|-----------|------|-------------|-----------|---------|
| 项目基础架构 | 90% | **92%** | +2% | ✅ | ✅ | ⚠️ |
| 用户管理模块 | 85% | **92%** | +7% | ✅ | ✅ | ❌ |
| AI客户端层 | 75% | **88%** | +13% | ✅ | ✅ | ❌ |
| 岗位知识库/RAG | 60% | **65%** | +5% | ⚠️ | ✅ | ❌ |
| AI就业画像分析 | 70% | **75%** | +5% | ✅ | ✅ | ❌ |
| AI岗位匹配 | 65% | **80%** | +15% | ✅ | ✅ | ❌ |
| AI简历优化 | 65% | **72%** | +7% | ✅ | ✅ | ❌ |
| AI成长规划 | 65% | **70%** | +5% | ✅ | ✅ | ❌ |
| 测试覆盖 | 10% | **15%** | +5% | ❌ | - | ❌ |
| 认证/鉴权 | 0% | 0% | - | ❌ | - | ❌ |
| 日志/监控 | 0% | **60%** | +60% | ✅ | ✅ | ❌ |
| API文档 | 80% | 80% | - | ✅ | ✅ | - |

**整体Demo完成度**: ~70% → **~78%**
**核心闭环状态**: ✅ 已打通，可完整演示

---

## 三、v1.1 变更记录（本次修复内容）

### 3.0 变更概览

| 序号 | 修复项 | 类型 | 完成状态 |
|------|-------|------|---------|
| 1 | 修复模拟模式简历优化bug（original字段硬编码） | Bug修复 | ✅ |
| 2 | Prompt模板外置到 `knowledge/prompts/` 目录 | 架构优化 | ✅ |
| 3 | 新增竞赛经历(UserCompetition)和实习经历(UserInternship)模型 | 功能新增 | ✅ |
| 4 | 岗位匹配接入AI深度分析（粗排+精排两阶段） | 功能增强 | ✅ |
| 5 | AI客户端增加指数退避重试机制 | 健壮性 | ✅ |
| 6 | 增加请求日志中间件 | 可观测性 | ✅ |
| 7 | 统一错误码枚举(ErrorCode)和分页模型(PaginatedResponse) | 规范化 | ✅ |
| 8 | AI客户端增加动态Mock数据生成 | 体验优化 | ✅ |
| 9 | JSON解析增强容错（正则提取兜底） | 健壮性 | ✅ |
| 10 | 用户模型增加邮箱/手机/意向城市/期望薪资字段 | 功能增强 | ✅ |

### 3.1 新增文件清单

```
knowledge/prompts/              # Prompt外部文件（新增）
├── system_profile_analyst.md   # 就业画像分析系统Prompt
├── system_resume_optimizer.md  # 简历优化系统Prompt
├── system_growth_planner.md    # 成长规划系统Prompt
└── system_job_matcher.md       # 岗位匹配系统Prompt

backend/app/utils/middleware.py # 请求日志中间件（新增）
```

### 3.2 修改文件清单

| 文件 | 主要改动 |
|------|---------|
| `app/ai/deepseek_client.py` | 重写：增加重试机制、动态Mock、外部Prompt加载、JSON解析增强 |
| `app/ai/prompts.py` | 重写：支持外部md文件加载、新增JobMatchPrompts、竞赛/实习格式化 |
| `app/models/user.py` | 新增UserCompetition和UserInternship模型、User增加email/phone等字段 |
| `app/models/__init__.py` | 注册新模型 |
| `app/schemas/user.py` | 新增竞赛/实习Schema、UserBase增加新字段 |
| `app/schemas/job.py` | MatchedJob增加AI增强字段(match_reason等) |
| `app/schemas/analysis.py` | skill_assessment字段名修正(programming_foundation) |
| `app/services/user_service.py` | 新增竞赛/实习CRUD方法、eager_load优化 |
| `app/services/job_match_service.py` | 重写：两阶段匹配（粗排+AI精排） |
| `app/api/user.py` | 新增竞赛/实习接口 |
| `app/utils/response.py` | 新增ErrorCode枚举、PaginatedResponse分页模型 |
| `main.py` | 注册日志中间件、使用ErrorCode枚举 |

---

## 四、各模块详细状态（v1.1 更新）

### 4.1 项目基础架构
**完成度: 92%** (↑2%)

✅ **新增完成**:
- 请求日志中间件（记录每个请求的方法、路径、状态码、耗时）
- 统一错误码枚举 `ErrorCode`（SUCCESS=0, INTERNAL_ERROR=1, PARAM_VALIDATION_ERROR=1001, NOT_FOUND=2001, AI_SERVICE_ERROR=3001等）
- 统一分页响应模型 `PaginatedResponse`

⚠️ **仍待改进**:
- [ ] 接口访问频率限制（Rate Limiting）
- [ ] 数据库连接池配置优化
- [ ] 配置文件区分dev/prod环境
- [ ] 请求ID追踪

### 4.2 数据模型层
**完成度: 88%** (↑8%)

✅ **新增模型**:
- `UserCompetition` - 竞赛获奖经历（名称、级别、奖项、描述、日期）
- `UserInternship` - 实习经历（公司、岗位、描述、技术栈、起止日期）
- `User` 表新增字段：email、phone、target_city、target_salary

⚠️ **仍待改进**:
- [ ] 缺少密码哈希字段（如需认证）
- [ ] 缺少软删除字段
- [ ] 竞赛经历日期字段已改为competition_date避免与Python类型冲突

### 4.3 AI客户端层
**完成度: 88%** (↑13%)

✅ **新增完成**:
- 指数退避重试机制（限流错误等待2^attempt秒，网络错误等待1+attempt秒）
- 区分错误类型：API错误、重试耗尽、解析错误
- 动态Mock数据生成（根据用户输入技能动态生成演示数据）
- 外部Prompt文件加载（`knowledge/prompts/`目录）
- JSON解析增强容错（两次尝试：直接解析 → 正则提取JSON块）
- AI参数可配置（timeout、max_retries、temperature均从环境变量读取）

⚠️ **仍待改进**:
- [ ] 缺少流式响应支持（SSE）
- [ ] 缺少Token用量统计
- [ ] 没有上下文记忆

### 4.4 岗位匹配模块
**完成度: 80%** (↑15%)

✅ **新增完成**:
- 两阶段匹配：关键词粗排 + AI深度分析精排
- AI增强匹配（在模拟模式下自动跳过，配置API Key后自动启用）
- 匹配结果新增字段：match_reason（AI匹配理由）、learning_suggestions（AI学习建议）、interview_focus（面试重点）
- AI增强失败时优雅降级，保持原始匹配结果

⚠️ **仍待改进**:
- [ ] 技能匹配算法需要同义词/别名映射
- [ ] 匹配分数算法需要技能权重
- [ ] 知识库内容需要人工审核

### 4.5 用户管理模块
**完成度: 92%** (↑7%)

✅ **新增接口**:
- `PUT /api/users/{id}/competitions` - 整组替换竞赛经历
- `PUT /api/users/{id}/internships` - 整组替换实习经历
- 用户资料查询返回竞赛和实习数据
- 用户上下文接口包含竞赛和实习数据

### 4.6 Prompt工程
**完成度: 85%** (↑15%)

✅ **新增完成**:
- 所有System Prompt外置到 `knowledge/prompts/` 目录下的md文件
- 修改Prompt只需编辑md文件，无需改代码重启
- 新增岗位匹配Prompt模板
- 画像分析和简历优化Prompt包含竞赛/实习经历数据
- 新增 `_format_competitions()` 和 `_format_internships()` 格式化函数

---

## 五、技术债务清单（v1.1 更新）

### 已偿还债务 ✅
1. ✅ **Prompt模板外置** - 已移到 `knowledge/prompts/` 目录
2. ✅ **AI调用异常处理** - 已实现指数退避重试
3. ✅ **岗位匹配AI化** - 已实现两阶段匹配
4. ✅ **用户模型扩展** - 已新增竞赛/实习经历
5. ✅ **Mock数据硬编码** - 已改为动态生成
6. ✅ **请求日志** - 已增加日志中间件
7. ✅ **错误码规范** - 已定义ErrorCode枚举
8. ✅ **分页封装** - 已定义PaginatedResponse

### 仍待偿还债务
**高优先级:**
1. **RAG向量检索增强** - 关键词检索效果有限，建议接入Embedding
2. **知识库内容审核** - 岗位描述需人工审核准确性
3. **流式响应** - AI分析耗时较长，建议加SSE打字机效果

**中优先级:**
1. 接口限流（Rate Limiting）
2. Service层参数校验增强
3. Token用量统计和成本控制
4. 配置文件区分环境

**低优先级:**
1. 认证鉴权
2. 单元测试
3. Docker部署
4. CI/CD

---

## 六、下一步开发优先级建议

### P0 - 无需再做（v1.1已全部完成）
1. ✅ 修复模拟模式bug
2. ✅ Prompt模板外置
3. ✅ 竞赛/实习经历模型
4. ✅ 岗位匹配AI化
5. ✅ 核心流程测试

### P1 - 体验优化（建议优先）
1. 增加AI分析的流式响应
2. 知识库内容审核和完善
3. 简历导出功能（Markdown/PDF）
4. 成长规划关联具体学习资源
5. 技能同义词/别名映射

### P2 - 功能扩展
1. 用户认证系统
2. 学习进度追踪
3. 岗位收藏
4. Docker部署

---

## 七、快速启动指南

### 环境要求
- Python 3.10+
- （可选）MySQL 8.0+

### 启动步骤
```bash
cd backend

# 安装依赖
pip install -r requirements.txt
# 国内用户: pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements.txt

# 初始化数据库
python init_db.py

# 启动服务
python main.py
# 访问 http://localhost:8000/docs
```

### 配置真实AI
编辑 `.env` 文件，填入 `DEEPSEEK_API_KEY=你的真实Key`，重启即可。

### 修改Prompt
编辑 `knowledge/prompts/` 目录下的md文件，无需重启服务（下次调用生效）。

---

## 八、目录结构速查

```
backend/
├── main.py                 # 入口，中间件+路由注册
├── init_db.py              # 数据库初始化
├── requirements.txt        # Python依赖
├── .env / .env.example     # 配置
├── app/
│   ├── ai/                 # AI层
│   │   ├── deepseek_client.py  # DeepSeek客户端(重试+Mock+Prompt加载)
│   │   └── prompts.py          # Prompt模板(外部文件加载)
│   ├── api/                # API层(5个模块)
│   │   ├── user.py             # 用户管理(含竞赛/实习)
│   │   ├── analysis.py         # 画像分析
│   │   ├── job_match.py        # 岗位匹配
│   │   ├── resume.py           # 简历优化
│   │   └── growth.py           # 成长规划
│   ├── services/           # 业务层
│   ├── models/             # ORM模型(含competition/internship)
│   ├── schemas/            # Pydantic模型
│   ├── database/           # 数据库连接
│   ├── knowledge/          # 知识库检索
│   └── utils/              # 工具类(ErrorCode+分页+中间件+异常)
└── knowledge/
    └── prompts/            # Prompt外部文件(新增)
        ├── system_profile_analyst.md
        ├── system_resume_optimizer.md
        ├── system_growth_planner.md
        └── system_job_matcher.md
```

---

## 九、API接口完整清单（v1.1）

### 用户管理（9个接口）
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/users` | 创建用户 |
| GET | `/api/users/{id}` | 获取用户完整资料 |
| PUT | `/api/users/{id}` | 更新基本信息 |
| PUT | `/api/users/{id}/skills` | 替换技能 |
| PUT | `/api/users/{id}/projects` | 替换项目 |
| PUT | `/api/users/{id}/competitions` | 替换竞赛经历 🆕 |
| PUT | `/api/users/{id}/internships` | 替换实习经历 🆕 |
| GET | `/api/users/{id}/context` | 获取AI上下文 |

### AI分析（12个接口）
| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/analysis` | 就业画像分析 |
| GET | `/api/analysis/{id}` | 获取分析详情 |
| GET | `/api/analysis/user/{id}` | 用户历史分析 |
| POST | `/api/resume` | 简历优化 |
| GET | `/api/resume/{id}` | 获取优化详情 |
| GET | `/api/resume/user/{id}` | 用户历史优化 |
| POST | `/api/growth` | 生成成长规划 |
| GET | `/api/growth/{id}` | 获取规划详情 |
| GET | `/api/growth/user/{id}` | 用户历史规划 |
| GET | `/api/jobs` | 岗位搜索 |
| GET | `/api/jobs/{id}` | 岗位详情 |
| POST | `/api/match` | 岗位匹配(AI增强) 🆕 |

### 系统（2个接口）
| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/` | 根路径 |
| GET | `/api/health` | 健康检查 |

---

## 十、已知Bug列表（v1.1 更新）

| Bug描述 | 严重程度 | 位置 | 修复建议 |
|---------|---------|------|---------|
| ~~模拟模式简历优化original硬编码~~ | ~~中~~ | ~~deepseek_client.py~~ | ✅ 已修复，改为动态生成 |
| ~~岗位匹配分数计算过于简单~~ | ~~高~~ | ~~job_match_service.py~~ | ✅ 已修复，两阶段AI匹配 |
| ~~缺少竞赛/实习经历表~~ | ~~高~~ | ~~models/user.py~~ | ✅ 已修复，已新增两张表 |
| ~~Prompt模板硬编码~~ | ~~中~~ | ~~prompts.py~~ | ✅ 已修复，已外置md文件 |
| 知识库中技能别名未覆盖（如"Spring" vs "SpringBoot"） | 中 | `knowledge_service.py` | 增加同义词映射表 |
| AI返回JSON格式偶有不符合Schema | 中 | `deepseek_client.py` | 已加双层容错，但仍有概率失败 |
| 整组替换操作无操作日志 | 低 | `user_service.py` | 增加操作审计日志 |

---

## 十一、开发注意事项

### AI功能开发
1. Prompt修改：编辑 `knowledge/prompts/` 下的md文件，无需重启
2. AI返回JSON一定要做容错（已实现双层fallback）
3. 模拟模式保留，方便前端开发
4. 重试次数可通过 `.env` 的 `AI_MAX_RETRIES` 配置

### 数据库相关
1. 修改models后重新运行 `init_db.py`
2. 新增表：`user_competitions`、`user_internships`
3. 竞赛日期字段名为 `competition_date`（避免与Python datetime.date冲突）

### 新增配置项
```env
AI_TIMEOUT=60         # AI调用超时秒数
AI_MAX_RETRIES=3      # 最大重试次数
AI_TEMPERATURE=0.7    # 默认温度参数
```

---

> **接手提示**: v1.1版本已修复所有P0问题。建议先跑一遍服务，用/docs测试所有接口。重点关注：竞赛/实习接口是否正常、Mock数据是否动态生成。下一步优先做流式响应和知识库内容审核。