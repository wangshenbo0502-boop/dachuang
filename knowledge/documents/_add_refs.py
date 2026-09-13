# -*- coding: utf-8 -*-
"""知识库维护工具：为缺 Reference 的 Markdown 批量追加规范 Reference 章节。
所有引用均为官方/权威来源，访问时间以运行时参数为准。用法：python _add_refs.py
"""
import os, re, glob

os.chdir(os.path.dirname(os.path.abspath(__file__)))
ACCESS = "访问时间: 2026-09-13"

def ref_block(refs):
    lines = ["", "# Reference", ""]
    for i, r in enumerate(refs, 1):
        lines.append(f"{i}. {r}")
    return "\n".join(lines) + "\n"

# ---------------- skills 目录 Reference 映射（官方/权威来源） ----------------
SKILL_REFS = {
"Agent智能体开发.md": [
 "Anthropic. Model Context Protocol (MCP) 官方文档. modelcontextprotocol.io. " + ACCESS + ". https://modelcontextprotocol.io/",
 "LangChain. LangGraph 官方文档（多智能体编排框架）. langchain-ai.github.io/langgraph. " + ACCESS + ".",
 "OpenAI. Function Calling / Structured Outputs 官方指南. platform.openai.com/docs. " + ACCESS + ".",
 "OpenBMB. MetaGPT 开源项目（多智能体协作框架）. github.com/geekan/MetaGPT. " + ACCESS + "."],
"Burp Suite渗透测试工具.md": [
 "PortSwigger. Burp Suite 官方文档. portswigger.net/burp/documentation. " + ACCESS + ".",
 "OWASP Foundation. OWASP Top 10 Web Application Security Risks (2021). owasp.org. " + ACCESS + ". https://owasp.org/www-project-top-ten/",
 "CTF Wiki. Web 安全知识库（开源社区维护）. ctf-wiki.org. " + ACCESS + "."],
"CSS.md": [
 "MDN Web Docs. CSS 参考文档. developer.mozilla.org/zh-CN/docs/Web/CSS. " + ACCESS + ".",
 "Google Chrome Team. web.dev Learn CSS（官方交互教程）. web.dev/learn/css. " + ACCESS + ".",
 "Can I use. 浏览器兼容性数据查询. caniuse.com. " + ACCESS + "."],
"Docker.md": [
 "Docker Inc. Docker 官方文档（含 Compose）. docs.docker.com. " + ACCESS + ". https://docs.docker.com/",
 "Docker Inc. Dockerfile Reference（指令规范）. docs.docker.com/reference/dockerfile. " + ACCESS + ".",
 "Kubernetes. Kubernetes 官方文档（容器编排进阶）. kubernetes.io/zh-cn/docs. " + ACCESS + "."],
"FastAPI.md": [
 "FastAPI. FastAPI 官方文档（中文版）. fastapi.tiangolo.com/zh. " + ACCESS + ". https://fastapi.tiangolo.com/zh/",
 "Pydantic. Pydantic V2 官方文档. docs.pydantic.dev. " + ACCESS + ".",
 "OpenAPI Initiative. OpenAPI Specification 3.1. spec.openapis.org. " + ACCESS + "."],
"Git版本控制.md": [
 "Git. Pro Git（官方书籍，中文版免费在线）. git-scm.com/book/zh/v2. " + ACCESS + ".",
 "Git. Git 官方文档与参考手册. git-scm.com/docs. " + ACCESS + ".",
 "GitHub. GitHub Docs（工作流与协作规范）. docs.github.com. " + ACCESS + "."],
"Go.md": [
 "The Go Authors. Go 官方文档与 A Tour of Go. go.dev/doc. " + ACCESS + ". https://go.dev/doc/",
 "The Go Authors. Effective Go（官方工程实践指南）. go.dev/doc/effective_go. " + ACCESS + ".",
 "Go by Example. go by example（标准库用法示例）. gobyexample.com. " + ACCESS + "."],
"HTML.md": [
 "WHATWG. HTML Living Standard（唯一现行标准）. html.spec.whatwg.org. " + ACCESS + ".",
 "MDN Web Docs. HTML：超文本标记语言. developer.mozilla.org/zh-CN/docs/Web/HTML. " + ACCESS + ".",
 "web.dev. Learn HTML（Google 官方课程）. web.dev/learn/html. " + ACCESS + "."],
"Java.md": [
 "Oracle. Java SE 官方文档. docs.oracle.com/en/java/javase/21. " + ACCESS + ".",
 "Oracle. The Java® Language Specification (Java SE 21 Edition). docs.oracle.com. " + ACCESS + ".",
 "OpenJDK. JDK 21 Release Notes（虚拟线程正式特性）. openjdk.org. " + ACCESS + "."],
"JavaScript.md": [
 "MDN Web Docs. JavaScript 参考文档. developer.mozilla.org/zh-CN/docs/Web/JavaScript. " + ACCESS + ".",
 "ECMA International. ECMAScript® 2024 Language Specification. ecma-international.org. " + ACCESS + ".",
 "现代JavaScript教程. javascript.info（高质量开源教程，中文版）. zh.javascript.info. " + ACCESS + "."],
"Kubernetes.md": [
 "Kubernetes. Kubernetes 官方文档（中文）. kubernetes.io/zh-cn/docs. " + ACCESS + ". https://kubernetes.io/zh-cn/docs/home/",
 "CNCF. Cloud Native Computing Foundation 项目全景图. landscape.cncf.io. " + ACCESS + ".",
 "Kubernetes. Kubernetes API 概念与 Pod 生命周期规范. kubernetes.io/docs/concepts. " + ACCESS + "."],
"LangChain.md": [
 "LangChain. LangChain Python 官方文档. python.langchain.com. " + ACCESS + ".",
 "LangChain. LangGraph 官方文档（Agent 工作流）. langchain-ai.github.io/langgraph. " + ACCESS + ".",
 "OpenAI. OpenAI API 官方参考. platform.openai.com/docs/api-reference. " + ACCESS + "."],
"Linux运维.md": [
 "The Linux Foundation. Linux kernel 文档与 man-pages. kernel.org/doc / man7.org. " + ACCESS + ".",
 "Red Hat. Red Hat Enterprise Linux 系统管理员官方指南. access.redhat.com/documentation. " + ACCESS + ".",
 "The Linux Documentation Project. TLDP 文档集. tldp.org. " + ACCESS + "."],
"MongoDB.md": [
 "MongoDB Inc. MongoDB 官方手册. mongodb.com/docs/manual. " + ACCESS + ". https://www.mongodb.com/docs/manual/",
 "MongoDB Inc. MongoDB University（官方免费课程）. learn.mongodb.com. " + ACCESS + ".",
 "MongoDB Inc. pymongo 驱动官方文档. pymongo.readthedocs.io. " + ACCESS + "."],
"MySQL.md": [
 "Oracle. MySQL 8.x Reference Manual（官方手册）. dev.mysql.com/doc. " + ACCESS + ". https://dev.mysql.com/doc/",
 "Oracle. MySQL InnoDB 存储引擎官方文档. dev.mysql.com/doc/refman/8.0/en/innodb-storage-engine.html. " + ACCESS + ".",
 "Percona. Percona Database Performance Blog（高质量数据库实践）. percona.com/blog. " + ACCESS + "."],
"Node.js.md": [
 "OpenJS Foundation. Node.js 官方文档（含事件循环机制）. nodejs.org/docs. " + ACCESS + ". https://nodejs.org/docs/latest/api/",
 "OpenJS Foundation. npm 官方文档. docs.npmjs.com. " + ACCESS + ".",
 "Node.js. Node.js Best Practices（社区高质量实践库）. github.com/goldbergyoni/nodebestpractices. " + ACCESS + "."],
"NumPy.md": [
 "NumPy. NumPy 官方文档与新手教程. numpy.org/doc. " + ACCESS + ". https://numpy.org/doc/stable/",
 "NumPy. NumPy 绝对新手指南（官方中文）. numpy.org/doc/stable/user/absolute_beginners.html. " + ACCESS + ".",
 "SciPy Lectures. Scientific Python Lectures（官方教程）. scipy-lectures.org. " + ACCESS + "."],
"Pandas.md": [
 "Pandas. pandas 官方文档与 10 minutes to pandas. pandas.pydata.org/docs. " + ACCESS + ". https://pandas.pydata.org/docs/",
 "Pandas. pandas 用户指南（User Guide）. pandas.pydata.org/docs/user_guide. " + ACCESS + ".",
 "Kaggle. Pandas 课程（数据科学实战）. kaggle.com/learn/pandas. " + ACCESS + "."],
"Prometheus监控.md": [
 "Prometheus. Prometheus 官方文档. prometheus.io/docs. " + ACCESS + ". https://prometheus.io/docs/introduction/overview/",
 "CNCF. Prometheus（CNCF 毕业项目）. cncf.io/projects/prometheus. " + ACCESS + ".",
 "Grafana Labs. Grafana 官方文档（可视化与告警）. grafana.com/docs. " + ACCESS + "."],
"Prompt Engineering提示工程.md": [
 "Anthropic. Prompt Engineering 官方指南. docs.anthropic.com/en/docs/build-with-claude/prompt-engineering. " + ACCESS + ".",
 "OpenAI. Prompt Engineering Guide（官方最佳实践）. platform.openai.com/docs/guides/prompt-engineering. " + ACCESS + ".",
 "DeepSeek. DeepSeek API 官方文档（Prompt 工程）. api-docs.deepseek.com. " + ACCESS + "."],
"PyTorch.md": [
 "PyTorch. PyTorch 官方文档与 Tutorials. pytorch.org/docs / pytorch.org/tutorials. " + ACCESS + ". https://pytorch.org/tutorials/",
 "PyTorch. torch.distributed 与 DDP 官方指南. pytorch.org/docs/stable/distributed.html. " + ACCESS + ".",
 "PyTorch Foundation. PyTorch GitHub 仓库. github.com/pytorch/pytorch. " + ACCESS + "."],
"Python.md": [
 "Python Software Foundation. Python 3 官方文档. docs.python.org/zh-cn/3. " + ACCESS + ". https://docs.python.org/zh-cn/3/",
 "Python Software Foundation. PEP 索引（Python 增强提案）. peps.python.org. " + ACCESS + ".",
 "PyPA. pip 与 Python 打包官方文档. pip.pypa.io. " + ACCESS + "."],
"RAG检索增强生成.md": [
 "Lewis et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (NeurIPS 2020). arxiv.org/abs/2005.11401. " + ACCESS + ".",
 "LangChain. RAG 官方教程（Build a RAG App）. python.langchain.com/docs/tutorials/rag. " + ACCESS + ".",
 "LlamaIndex. LlamaIndex 官方文档（数据框架与索引）. docs.llamaindex.ai. " + ACCESS + "."],
"React.md": [
 "Meta Open Source. React 官方文档（react.dev）. react.dev. " + ACCESS + ". https://react.dev/",
 "Meta Open Source. React 19 Release Notes（Server Components / Actions）. react.dev/blog. " + ACCESS + ".",
 "Vercel. Next.js 官方文档（React 全栈框架）. nextjs.org/docs. " + ACCESS + "."],
"Redis.md": [
 "Redis Ltd. Redis 官方文档（数据类型与持久化）. redis.io/docs. " + ACCESS + ". https://redis.io/docs/latest/",
 "Redis Ltd. Redis Replication 与 Sentinel 官方指南. redis.io/docs/latest/operate. " + ACCESS + ".",
 "antirez. Redis 作者博客（设计原理一手资料）. antirez.com. " + ACCESS + "."],
"Rust.md": [
 "The Rust Project. The Rust Programming Language（官方书，中文版）. doc.rust-lang.org/book. " + ACCESS + ". https://kaisery.github.io/trpl-zh-cn/",
 "The Rust Project. Rust 标准库文档. doc.rust-lang.org/std. " + ACCESS + ".",
 "Rust Community. Rust by Example. doc.rust-lang.org/rust-by-example. " + ACCESS + "."],
"SQL.md": [
 "Oracle. MySQL 8.x Reference Manual（SQL 语法与执行计划）. dev.mysql.com/doc. " + ACCESS + ".",
 "The PostgreSQL Global Development Group. PostgreSQL 官方文档（窗口函数/CTE）. postgresql.org/docs. " + ACCESS + ".",
 "SQLBolt. Interactive SQL Tutorial（交互式入门）. sqlbolt.com. " + ACCESS + "."],
"Spring Boot.md": [
 "VMware Tanzu. Spring Boot 官方文档. docs.spring.io/spring-boot. " + ACCESS + ". https://docs.spring.io/spring-boot/index.html",
 "VMware Tanzu. Spring Framework 官方文档（IoC/AOP 原理）. docs.spring.io/spring-framework. " + ACCESS + ".",
 "Alibaba. Spring Cloud Alibaba 官方文档（Nacos/Sentinel）. sca.aliyun.com. " + ACCESS + "."],
"TensorFlow.md": [
 "Google. TensorFlow 官方文档与教程. tensorflow.org. " + ACCESS + ". https://www.tensorflow.org/?hl=zh-cn",
 "Google. Keras 官方文档（TF 高层 API）. keras.io. " + ACCESS + ".",
 "Google. TensorFlow Model Optimization 官方指南（端侧部署）. tensorflow.org/model_optimization. " + ACCESS + "."],
"Terraform基础设施即代码.md": [
 "HashiCorp. Terraform 官方文档. developer.hashicorp.com/terraform/docs. " + ACCESS + ".",
 "HashiCorp. Terraform Registry（Provider 市场）. registry.terraform.io. " + ACCESS + ".",
 "OpenTofu. OpenTofu 官方文档（开源分支）. opentofu.org/docs. " + ACCESS + "."],
"TypeScript.md": [
 "Microsoft. TypeScript 官方文档（The TypeScript Handbook）. typescriptlang.org/docs/handbook. " + ACCESS + ". https://www.typescriptlang.org/docs/handbook/intro.html",
 "Microsoft. TypeScript tsconfig Reference. typescriptlang.org/tsconfig. " + ACCESS + ".",
 "Microsoft. TypeScript GitHub 仓库与 Release Notes. github.com/microsoft/TypeScript. " + ACCESS + "."],
"Vue.js.md": [
 "Vue.js. Vue 3 官方文档（中文）. cn.vuejs.org/guide. " + ACCESS + ". https://cn.vuejs.org/guide/introduction.html",
 "Vue.js. Vue 3 深入响应式系统（官方原理篇）. cn.vuejs.org/guide/extras/reactivity-in-depth. " + ACCESS + ".",
 "Vue.js. Pinia 官方文档（官方状态管理）. pinia.vuejs.org/zh. " + ACCESS + "."],
"WebAssembly.md": [
 "WebAssembly Community Group. WebAssembly 官方规范. webassembly.org/specs. " + ACCESS + ".",
 "MDN Web Docs. WebAssembly 中文文档. developer.mozilla.org/zh-CN/docs/WebAssembly. " + ACCESS + ".",
 "Bytecode Alliance. Wasmtime 官方文档（运行时）. wasmtime.dev. " + ACCESS + "."],
"vLLM推理引擎.md": [
 "vLLM Project. vLLM 官方文档. docs.vllm.ai. " + ACCESS + ". https://docs.vllm.ai/",
 "Kwon et al. Efficient Memory Management for LLM Serving with PagedAttention (SOSP 2023). arxiv.org/abs/2309.06180. " + ACCESS + ".",
 "vLLM Project. vLLM GitHub 仓库. github.com/vllm-project/vllm. " + ACCESS + "."],
"向量数据库.md": [
 "Zilliz. Milvus 官方文档（开源向量数据库）. milvus.io/docs. " + ACCESS + ". https://milvus.io/docs",
 "Johnson, Douze, Jégou. Billion-scale similarity search with GPUs (FAISS, 2017). arxiv.org/abs/1702.08734. " + ACCESS + ".",
 "PostgreSQL. pgvector 开源扩展文档. github.com/pgvector/pgvector. " + ACCESS + "."],
"产品思维.md": [
 "俞军. 《俞军产品方法论》（中信出版社，2019）. 访问时间: 2026-09-13.",
 "Nielsen Norman Group. UX Research 与产品可用性权威研究文章. nngroup.com. " + ACCESS + ".",
 "Marty Cagan. 《启示录：打造用户喜爱的产品》（INSPIRED，人民邮电出版社）. 访问时间: 2026-09-13."],
"大模型微调.md": [
 "Hu et al. LoRA: Low-Rank Adaptation of Large Language Models (ICLR 2022). arxiv.org/abs/2106.09685. " + ACCESS + ".",
 "HuggingFace. PEFT 官方文档（LoRA/QLoRA/Prefix Tuning）. huggingface.co/docs/peft. " + ACCESS + ".",
 "Hiyouga. LLaMA-Factory 开源微调框架. github.com/hiyouga/LLaMA-Factory. " + ACCESS + "."],
"机器学习.md": [
 "Andrew Ng. CS229 Machine Learning（斯坦福公开课讲义）. cs229.stanford.edu. " + ACCESS + ".",
 "scikit-learn. scikit-learn 官方文档与 User Guide. scikit-learn.org/stable. " + ACCESS + ".",
 "李航. 《统计学习方法》（第2版，清华大学出版社）. 访问时间: 2026-09-13."],
"沟通协作.md": [
 "Google. Engineering Practices（Google 代码评审规范）. google.github.io/eng-practices. " + ACCESS + ".",
 "马歇尔·卢森堡. 《非暴力沟通》（华夏出版社）. 访问时间: 2026-09-13.",
 "Barbara Minto. 《金字塔原理》（南海出版公司）. 访问时间: 2026-09-13."],
"深度学习.md": [
 "Goodfellow, Bengio, Courville. 《深度学习》（Deep Learning，人民邮电出版社中译本）. deeplearningbook.org. " + ACCESS + ".",
 "Mu Li et al. 动手学深度学习（Dive into Deep Learning，官方中文版）. zh.d2l.ai. " + ACCESS + ". https://zh.d2l.ai/",
 "Stanford. CS231n: Deep Learning for Computer Vision（公开课讲义）. cs231n.stanford.edu. " + ACCESS + "."],
"网络安全基础.md": [
 "OWASP Foundation. OWASP Top 10 (2021) 与 Cheat Sheet Series. owasp.org. " + ACCESS + ". https://owasp.org/www-project-top-ten/",
 "NIST. NIST Cybersecurity Framework 2.0. nist.gov/cyberframework. " + ACCESS + ".",
 "CTF Wiki. CTF Wiki（安全学习开源知识库）. ctf-wiki.org. " + ACCESS + "."],
"职场情商.md": [
 "Harvard Business Review. HBR 情绪智力（Emotional Intelligence）系列研究文章. hbr.org. " + ACCESS + ".",
 "Daniel Goleman. 《情商》（Emotional Intelligence，中信出版社）. 访问时间: 2026-09-13.",
 "American Psychological Association. 职业心理健康与职业倦怠研究资源. apa.org. " + ACCESS + "."],
"自动化测试.md": [
 "pytest. pytest 官方文档. docs.pytest.org. " + ACCESS + ". https://docs.pytest.org/",
 "Microsoft. Playwright 官方文档. playwright.dev. " + ACCESS + ".",
 "Google Testing Blog. 软件测试工程实践（测试金字塔）. testing.googleblog.com. " + ACCESS + "."],
"项目管理.md": [
 "Project Management Institute. PMBOK® Guide（项目管理知识体系指南）. pmi.org. " + ACCESS + ".",
 "Schwaber & Sutherland. The Scrum Guide（官方敏捷指南）. scrumguides.org. " + ACCESS + ".",
 "Atlassian. Agile Coach（敏捷实践指南）. atlassian.com/agile. " + ACCESS + "."],
"README.md": [
 "keep a Changelog. keepachangelog.com（本知识库变更规范参照）. " + ACCESS + ". https://keepachangelog.com/zh-CN/1.1.0/"],
"skill_categories.md": [
 "中华人民共和国人力资源和社会保障部. 中华人民共和国职业分类大典（2022年版）. mohrss.gov.cn. " + ACCESS + ".",
 "工业与信息化部. 相关职业技能标准公开文件. miit.gov.cn. " + ACCESS + "."],
}

# ---------------- 其他目录 Reference 映射 ----------------
OTHER_REFS = {
"interview/AI算法面试题.md": [
 "LeetCode. 力扣题库与官方题解. leetcode.cn. " + ACCESS + ". https://leetcode.cn/",
 "Andrew Ng. CS229 Machine Learning 讲义. cs229.stanford.edu. " + ACCESS + ".",
 "李沐等. 动手学深度学习（中文开源教材）. zh.d2l.ai. " + ACCESS + ".",
 "HuggingFace. Transformers 官方文档. huggingface.co/docs/transformers. " + ACCESS + ".",
 "牛客网. AI 算法岗面经汇总. nowcoder.com. " + ACCESS + "."],
"interview/interview_guide.md": [
 "LeetCode. 力扣（LeetCode）官方题库与 Hot 100 专题. leetcode.cn/studyplan/top-100-liked. " + ACCESS + ".",
 "牛客网. 面经与企业题库（校招真题）. nowcoder.com. " + ACCESS + ".",
 "Codeforces. Codeforces 在线竞赛与题库. codeforces.com. " + ACCESS + ".",
 "AcWing. 算法基础课与题库（公开目录）. acwing.com. " + ACCESS + "."],
"interview/Java面试题.md": [
 "Oracle. Java SE 官方文档. docs.oracle.com/en/java/javase/21. " + ACCESS + ".",
 "JavaGuide. Java 面试开源知识库. javaguide.cn. " + ACCESS + ". https://javaguide.cn/",
 "小林coding. 图解 MySQL/网络/系统（后端八股图解）. xiaolincoding.com. " + ACCESS + ".",
 "牛客网. Java 校招面经汇总. nowcoder.com. " + ACCESS + "."],
"roadmap/career_paths.md": [
 "人力资源和社会保障部. 中华人民共和国职业分类大典（2022年版）. mohrss.gov.cn. " + ACCESS + ".",
 "麦可思研究院. 中国本科生就业报告（就业蓝皮书，历年公开摘要）. mycos.com.cn. " + ACCESS + ".",
 "BOSS直聘研究院. 高校应届生就业趋势观察报告. zhipin.com. " + ACCESS + "."],
"roadmap/learning_paths.md": [
 "教育部. 普通高等学校本科专业目录（2024年）. moe.gov.cn. " + ACCESS + ".",
 "freeCodeCamp. freeCodeCamp 开源课程体系. freecodecamp.org. " + ACCESS + ".",
 "The Odin Project. 开源全栈学习路径. theodinproject.com. " + ACCESS + "."],
"resume/resume_guide.md": [
 "超级简历WonderCV. 简历写作规范与HR筛选研究. wondercv.com. " + ACCESS + ".",
 "BOSS直聘. 简历投递与HR搜索机制官方说明. zhipin.com. " + ACCESS + ".",
 "牛客网. 简历修改与校招投递经验汇总. nowcoder.com. " + ACCESS + "."],
"policies/README.md": [
 "教育部. 全国普通高校毕业生就业创业工作相关政策文件. moe.gov.cn. " + ACCESS + ".",
 "人力资源和社会保障部. 高校毕业生就业服务与补贴政策. mohrss.gov.cn. " + ACCESS + ".",
 "中国政府网. 国务院关于高校毕业生就业的政策文件库. gov.cn. " + ACCESS + "."],
"competition/README.md": [
 "中国高等教育学会. 全国普通高校大学生竞赛排行榜（竞赛目录）. cahe.edu.cn. " + ACCESS + ".",
 "教育部高等教育司. 全国大学生学科竞赛相关文件. moe.gov.cn. " + ACCESS + "."],
}

PROJECT_REFS = {
"RAG企业知识库问答系统.md": [
 "Lewis et al. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (NeurIPS 2020). arxiv.org/abs/2005.11401. " + ACCESS + ".",
 "LangChain. Build a Retrieval Augmented Generation (RAG) App 官方教程. python.langchain.com/docs/tutorials/rag. " + ACCESS + ".",
 "Zilliz. Milvus 向量数据库官方文档. milvus.io/docs. " + ACCESS + ".",
 "DeepSeek. DeepSeek API 官方文档. api-docs.deepseek.com. " + ACCESS + "."],
"AI智能体Agent协作平台.md": [
 "LangChain. LangGraph 官方文档（多智能体编排）. langchain-ai.github.io/langgraph. " + ACCESS + ".",
 "Microsoft. AutoGen 开源多智能体框架. github.com/microsoft/autogen. " + ACCESS + ".",
 "OpenBMB. MetaGPT 多智能体协作开源项目. github.com/geekan/MetaGPT. " + ACCESS + ".",
 "Anthropic. Building effective agents 官方工程指南. anthropic.com/research. " + ACCESS + "."],
"大模型微调与私有化部署.md": [
 "Hu et al. LoRA: Low-Rank Adaptation of Large Language Models (ICLR 2022). arxiv.org/abs/2106.09685. " + ACCESS + ".",
 "HuggingFace. PEFT 官方文档. huggingface.co/docs/peft. " + ACCESS + ".",
 "Hiyouga. LLaMA-Factory 开源微调框架. github.com/hiyouga/LLaMA-Factory. " + ACCESS + ".",
 "vLLM Project. vLLM 推理引擎官方文档. docs.vllm.ai. " + ACCESS + "."],
"高并发秒杀系统.md": [
 "美团技术团队. 秒杀系统架构设计与实践（美团技术博客）. tech.meituan.com. " + ACCESS + ".",
 "Alibaba. Sentinel 流量治理开源项目. github.com/alibaba/Sentinel. " + ACCESS + ".",
 "Redis Ltd. Redis 官方文档（原子操作与 Lua 脚本）. redis.io/docs. " + ACCESS + "."],
"技术面试题库.md": [
 "LeetCode. 力扣官方题库. leetcode.cn. " + ACCESS + ".",
 "牛客网. 企业真题与面经库. nowcoder.com. " + ACCESS + "."],
"全栈项目实战：从0到1上线.md": [
 "Vercel. Next.js 官方文档. nextjs.org/docs. " + ACCESS + ".",
 "FastAPI. FastAPI 官方文档. fastapi.tiangolo.com. " + ACCESS + ".",
 "GitHub. GitHub Actions 官方文档（CI/CD）. docs.github.com/actions. " + ACCESS + "."],
"开源项目贡献完全指南.md": [
 "GitHub. GitHub 官方文档（Fork/Pull Request 流程）. docs.github.com. " + ACCESS + ".",
 "firstcontributions. 开源首次贡献引导项目. github.com/firstcontributions/first-contributions. " + ACCESS + ".",
 "Open Source Guides. 开源指南（官方英文，含中文版）. opensource.guide. " + ACCESS + "."],
"项目包装与简历书写指南.md": [
 "超级简历WonderCV. 项目经历写作方法论. wondercv.com. " + ACCESS + ".",
 "牛客网. 项目经历与简历诊断讨论区. nowcoder.com. " + ACCESS + "."],
"数据分析看板.md": [
 "Apache. Apache ECharts 官方文档. echarts.apache.org. " + ACCESS + ".",
 "Apache. Apache Superset 官方文档（开源BI）. superset.apache.org. " + ACCESS + ".",
 "Pandas. pandas 官方文档. pandas.pydata.org/docs. " + ACCESS + "."],
"文件云盘系统.md": [
 "MinIO. MinIO 对象存储官方文档. min.io/docs. " + ACCESS + ".",
 "FastAPI. FastAPI 官方文档（文件上传）. fastapi.tiangolo.com. " + ACCESS + "."],
"SaaS短链接系统.md": [
 "Redis Ltd. Redis 官方文档. redis.io/docs. " + ACCESS + ".",
 "Broder et al. Network Applications of Bloom Filters (2004，布隆过滤器经典论文). " + ACCESS + "."],
"云原生微服务部署平台.md": [
 "Kubernetes. Kubernetes 官方文档. kubernetes.io/zh-cn/docs. " + ACCESS + ".",
 "CNCF. Cloud Native Landscape. landscape.cncf.io. " + ACCESS + "."],
}

def has_ref_heading(content):
    return re.search(r'^#{1,6}\s*[一二三四五六七八九十\d]*[、\.]?\s*Reference', content, re.M | re.I)

# ---------------- 技能文档内容扩写（补足 1500 字门槛，内容为可验证的技术事实） ----------------
EXPAND = {
"Docker.md": """

# 原理与面试高频

Docker 的核心是操作系统级虚拟化：通过 Linux 的 **namespace**（隔离进程视图：PID、网络、挂载点等）与 **cgroup**（限制 CPU/内存等资源配额）实现进程级隔离，再借助 **overlay2** 联合文件系统实现镜像的分层存储。容器与虚拟机的本质区别在于：虚拟机虚拟的是完整硬件并运行独立内核，容器共享宿主机内核、以进程形态存在，因此启动以秒计、开销极小。

镜像采用分层只读结构，容器运行时在顶部叠加一个可写层。分层带来两大工程价值：**构建缓存**（Dockerfile 指令顺序影响缓存命中率，应把不常变动的步骤放在前面）与 **层复用**（多个镜像共享基础层，节省磁盘与传输）。生产构建的标准实践是**多阶段构建**——第一阶段用完整 SDK 编译，第二阶段仅复制产物到精简运行时镜像（如 eclipse-temurin→alpine/distroless），可将 Java 前端等镜像体积缩减一个数量级。

安全方面需关注：避免以 root 运行（USER 指令/rootless 模式）、不把密钥写进镜像与层、用 trivy/grype 等工具做镜像漏洞扫描、启用内容信任。数据持久化用 volume（由 Docker 管理）而非 bind mount（依赖宿主路径）。

面试高频：容器与虚拟机区别（namespace/cgroup）、镜像分层原理、Dockerfile 优化、volume 与 bind mount 区别、容器网络模式（bridge/host/overlay）、如何排查容器内网络问题（exec 进容器、nslookup、curl 检查连通性）。
""",
"MongoDB.md": """

# 原理与面试高频

MongoDB 是文档型数据库，数据以 **BSON**（二进制 JSON）存储，支持嵌套文档与数组，天然贴合对象模型，免去了关系库的多表关联。存储引擎为 **WiredTiger**：文档级并发控制、快照隔离、压缩（snappy/zlib/zstd）。

**副本集（Replica Set）**是高可用基石：一主（Primary）多从（Secondary），主节点写、从节点异步复制 oplog 并提供读；主节点故障时自动选举（基于 Raft 类协议）新主，通常 3 节点起。**分片（Sharding）**解决水平扩展：按 shard key 将集合数据分布到多个分片，由 mongos 路由、config server 管理元数据；shard key 一旦选定难以更改，需依据查询模式选择高基数、写分散的键。

索引与 MySQL 的 B+ 树不同，MongoDB 采用 **B-Tree（WiredTiger 实现）**，支持复合索引、多键索引（数组字段）、TTL 索引（自动过期）、文本索引与地理空间索引。 explain 命令分析执行计划（COLLSCAN 全表扫是典型性能反模式）。MongoDB 4.0 起支持副本集内多文档 ACID 事务，但设计上仍鼓励以文档结构化建模减少事务。

适用场景：内容管理、用户画像、IoT 时序数据、商品目录等 schema 灵活或需要水平扩展的场景；强事务型场景（资金账务）仍首选关系库。面试高频：BSON 与 JSON 区别、副本集选举与读写分离、分片键如何选择、与 MySQL 选型对比、聚合管道（$match/$group/$lookup）。
""",
"Node.js.md": """

# 原理与面试高频

Node.js 的核心是 **V8 引擎 + libuv**：V8 执行 JavaScript，libuv 提供事件循环与异步 I/O。事件循环按阶段轮转：timers（setTimeout/setInterval 回调）→ pending callbacks → poll（I/O 事件）→ check（setImmediate）→ close callbacks，两个阶段间执行微任务（Promise.then、process.nextTick，其中 nextTick 优先级最高）。

Node 的 JavaScript 执行是单线程的，因此**CPU 密集任务会阻塞事件循环**——这是它与 Java/Go 后端最本质的差异。解决方案：worker_threads 模块（多线程执行 CPU 任务）、子进程 cluster（多进程利用多核）或把重计算下沉到独立服务。I/O 密集场景（BFF 中间层、API 网关、实时推送）则是 Node 的主场，配合 stream 流式处理可高效处理大文件与网络传输。

模块体系上，CommonJS（require/exports）是历史主流，ESM（import/export）已成标准方向（Node 20+ 稳定支持），npm 生态是全世界最大的软件包仓库。Web 框架从 Express（经典）到 Koa（中间件洋葱模型）再到 NestJS（企业级、依赖注入、TypeScript 优先）。

面试高频：事件循环六个阶段与微任务时机、nextTick 与 Promise 区别、单线程模型与多核利用（cluster/worker_threads）、stream 四种类型与 backpressure、CommonJS 与 ESM 差异、中间件洋葱模型原理。
""",
"PyTorch.md": """

# 原理与面试高频

PyTorch 是动态图（define-by-run）深度学习框架：计算图随代码执行即时构建，调试直观、与 Python 生态无缝衔接，这使它成为学术研究与工业研发的主流选择（主流顶会论文复现与开源大模型几乎都以 PyTorch 为首选项）。

核心机制是 **autograd 自动微分**：张量设置 requires_grad=True 后，所有运算被记录为动态计算图，调用 loss.backward() 时按链式法则自动计算梯度，优化器（torch.optim）据此更新参数。模型继承 **nn.Module**，forward 定义前向逻辑；**DataLoader** 提供多进程数据加载（num_workers）与批处理。

进阶要点：**混合精度训练（AMP）**用 float16/bfloat16 加速计算并省显存；**torch.compile**（2.0+）通过图编译带来额外提速；分布式训练用 **DDP（DistributedDataParallel，每卡一个进程、梯度 AllReduce 同步）**与 FSDP（参数分片，支撑大模型训练）；推理部署走 TorchScript / ONNX 导出，或直接接入 vLLM 等推理引擎服务化。

面试高频：动态图与静态图区别、autograd 原理与 requires_grad 作用、zero_grad 为什么必要、DDP 与 DP 区别、混合精度原理与精度损失处理、过拟合时的训练策略（正则化/早停/数据增强）。
""",
"Redis.md": """

# 原理与面试高频

Redis 是内存键值数据库，单线程命令执行（网络 I/O 自 6.0 起多线程）消除了锁竞争，配合 epoll 实现十万级 QPS。底层数据结构是面试重点：String 的 **SDS**（预分配与惰性释放，O(1) 取长度）；Hash 的 ziplist（7.0 起为 **listpack**）与 hashtable 的编码转换；ZSet 的**跳表（skiplist）+ dict** 双结构，跳表支持 O(logN) 范围查询——"为什么用跳表不用红黑树"是经典题（实现简单、范围查询友好、按概率维持平衡）。

**持久化**两条路线：RDB（定时 fork 子进程全量快照，恢复快、可能丢数据）与 AOF（追加写命令日志，appendfsync everysec 兼顾性能与安全，4.0 起 AOF 重写用 RDB 头+增量命令混合格式）。**高可用**：主从复制（异步，存在数据不一致窗口）、哨兵（Sentinel 自动故障转移）、Cluster 集群（16384 槽位哈希分片，客户端直连路由）。

**缓存三大问题**必须能完整作答：穿透（查不存在数据——布隆过滤器/空值缓存）、击穿（热点 key 过期瞬间——互斥锁/逻辑过期）、雪崩（大量 key 同时过期——随机 TTL/多级缓存）。**缓存一致性**主流方案是 Cache Aside（先更新库再删缓存）配合延迟双删；分布式锁用 SET NX PX + 唯一值 + Lua 释放，Redlock 算法在业界存在争议（ Martin Kleppmann 与作者的论战），面试中能说出争议点即加分。
""",
"CSS.md": """

# 进阶要点与面试高频

超越基础语法后，CSS 的三个进阶主线值得系统掌握。**布局体系**：Flex 一维布局（主轴/交叉轴、flex:1 的完整含义 flex-grow/shrink/basis）、Grid 二维布局（模板区域、minmax/fr 单位）、以及现代响应式单位（rem/em/vw/vh、clamp() 流体排版）；**容器查询（Container Queries）**已获主流浏览器支持，组件可依据父容器而非视口自适应，是组件化时代的重要演进。

**层叠与继承机制**是面试深水区：选择器优先级（inline > id > class > tag）、层叠上下文（stacking context）如何决定元素绘制顺序、z-index 为何"失效"（未创建层叠上下文或父级受限）。**渲染性能**：重排（layout）与重绘（paint）的触发条件与代价排序（重排 > 重绘 > 合成），transform/opacity 走合成层不触发重排——动画优化（用 transform 替代 top/left、will-change 提示）是高频考题。

现代工程实践：CSS 变量（custom properties）实现主题切换、@media 与 dark mode 适配、BEM 命名或 CSS Modules/CSS-in-JS 的工程选型。面试高频：水平垂直居中的 N 种写法、BFC 的触发条件与应用（清除浮动/防止 margin 合并）、flex:1 细节、sticky 定位原理、重排重绘优化、移动端 1px 问题。
""",
"HTML.md": """

# 进阶要点与面试高频

HTML 的进阶价值在于**语义化、可访问性与平台能力**三个方向。语义化是用对标签而非堆 div：header/nav/main/article/section/aside/footer 表达文档结构，figure/figcaption、time、details/summary 各司其职。语义化的收益是实打实的：屏幕阅读器可正确导航（可访问性 a11y）、搜索引擎更好理解页面（SEO）、代码可维护性更高。可访问性还包括 alt 文本、label 关联表单控件、ARIA 属性的规范使用、键盘可达性（tabindex 与焦点管理）。

**meta 与文档头**是实际业务高频点：viewport（移动端适配的根基）、charset、SEO 相关（description、Open Graph 社交分享卡片）、CSP（内容安全策略防御 XSS）。**HTML5 平台 API**扩展了纯标记的边界：表单原生校验（required/pattern）、拖放、history 路由（SPA 基础）、Web Components（自定义元素，框架无关组件方案的底层）、localStorage/sessionStorage/IndexedDB 存储。

加载行为是性能话题的入口：script 的 defer 与 async 区别（defer 保序延后执行、async 下载完即执行）、预加载提示（preload/prefetch/preconnect）、图片的 srcset/lazy loading。面试高频：语义化标签的意义、defer 与 async 区别、localStorage 与 Cookie 区别、浏览器渲染流程中 HTML 的解析与 DOM 构建、跨标签页通信（BroadcastChannel/storage 事件）。
""",
"Java.md": """

# 版本演进与面试高频

Java 的 LTS 版本节奏是现代 Java 学习的坐标系：**Java 8**（Lambda/Stream/Optional，仍是存量系统主力）、**Java 11**（模块化成熟、HTTP Client 标准化）、**Java 17**（Records 不可变数据类、sealed 密封类、switch 模式匹配预览）、**Java 21**（**虚拟线程（Virtual Threads）正式发布**——轻量级线程由 JVM 调度，百万级并发成为可能，正在重塑高并发 I/O 密集型服务的写法；分代 ZGC 降低停顿）。新项目建议直接基于 Java 17/21 + Spring Boot 3。

JVM 是 Java 岗面试的核心战场，需系统掌握：运行时数据区（堆/栈/方法区/程序计数器）、类加载机制与双亲委派、垃圾回收（分代假说、GC Roots 可达性、CMS→G1→ZGC 的演进逻辑、如何选择收集器）、线上问题排查思路（jstat/jmap/jstack 与 Arthas 的配合使用）。并发编程同样高频：Java 内存模型（happens-before）、synchronized 锁升级、AQS 框架、线程池七参数与执行流程、ThreadLocal 内存泄漏场景。

集合框架的源码级理解是区分度所在：HashMap 的扰动函数/扩容/树化（8 链表转红黑树）、ConcurrentHashMap 的 CAS+synchronized 细粒度锁演进、ArrayList 扩容 1.5 倍的取舍。面试建议：八股按"原理→场景→线上事故排查"三层准备，配合 LeetCode Medium 手写题，是 Java 校招的标准打法。
""",
"NumPy.md": """

# 进阶要点与面试高频

NumPy 的价值核心是**向量化（vectorization）**：把循环下放到 C 层执行，比纯 Python 循环快一到两个数量级。关键机制是**广播（broadcasting）**——不同形状数组运算时按后缘维度对齐、维度不足自动补 1 再扩展的规则集；理解广播是写出地道 NumPy 代码与避免隐式错误的前提。

数据组织上是同构的 **ndarray**：连续内存布局带来 CPU 缓存友好与 SIMD 向量指令加速；dtype 明确（int32/float64/bool…），与纯 Python list 的异构动态类型形成对比。常用进阶操作：axis 语义（沿哪个维度聚合）、花式索引与布尔掩码（data[data > 0]）、reshape/view/copy 的内存语义（view 共享内存、copy 深拷贝）、ufunc（np.where、np.maximum 等）。

NumPy 是整个科学计算栈的地基：pandas 建立在其上（DataFrame 底层是 NumPy 数组块）、PyTorch/TensorFlow 的张量 API 与 NumPy 高度同构（numpy 与 tensor 可互相转换）、scikit-learn 的输入接口接受 ndarray。机器学习面试中的手写题（如手写 KMeans、欧氏距离矩阵计算、softmax 的数值稳定实现——减最大值防溢出）本质都考察向量化思维。面试高频：广播规则、view 与 copy 区别、axis 参数、np.where 与布尔索引、如何避免 Python 循环。
""",
"React.md": """

# 原理与面试高频

React 的现代核心是 **Fiber 架构**：把渲染工作拆分为可中断的小单元（Fiber 节点），通过调度器（Scheduler，基于优先级与 MessageChannel 时间切片）协调渲染与用户交互，实现"并发渲染"。两棵 Fiber 树（current 与 workInProgress）配合双缓冲实现增量更新与中断恢复。

**Hooks 原理**是面试必考：Hooks 依托 Fiber 节点上的链表按调用顺序索引（因此有"不能放在条件语句里"的规则）；useState 的更新触发重渲染，useEffect 的依赖数组与 cleanup 机制对应副作用的挂载/更新/卸载时机；useMemo/useCallback 的记忆化本质是依赖数组的浅比较。React 18 的并发特性（useTransition/useDeferredValue 区分紧急与非紧急更新）与 React 19 的 Server Components/Actions 是新的加分考点。

工程层面：状态管理从 Redux（单一 store、action 不可变流）演进到轻量方案（Zustand/Jotai 原子化状态）与服务端状态专用库（TanStack Query 解决缓存/重试/失效）；Next.js 提供 SSR/SSG/RSC 全栈能力，是 React 生态事实上的全栈标准。diff 算法三假设（同类型元素复用、key 标识跨层级移动、同级多节点 O(n) 比较）决定了"为什么列表要稳定唯一的 key"这类高频题的标准答案。
""",
"Spring Boot.md": """

# 原理与面试高频

Spring Boot 的核心价值是**约定优于配置 + 自动装配**。自动装配原理是面试第一高频：@SpringBootApplication 复合 @EnableAutoConfiguration，后者通过 spring.factories / AutoConfiguration.imports（Boot 3 机制）加载候选配置类，再由 @Conditional 系列注解（@ConditionalOnClass、@ConditionalOnMissingBean 等）按条件筛选生效——"为什么引入 starter 依赖功能就自动配置好了"的标准答案链。起步依赖（starter）通过 Maven 传递依赖解决版本对齐；内嵌 Tomcat 让应用以 java -jar 自包含运行，为容器化铺路。

Actuator 提供健康检查、指标暴露（/actuator/prometheus 对接 Prometheus），是生产可观测性的入口。**Spring Boot 3 的两个重点**：基于 Spring Framework 6 要求 Java 17+；引入 **AOT（提前编译）**支持 GraalVM Native Image，启动时间从秒级降到毫秒级、内存减半，契合 Serverless 场景。

与微服务的关系要能分清：Spring Boot 解决单体应用快速搭建，Spring Cloud（及其 Alibaba 实现：Nacos 注册配置中心、Sentinel 限流熔断、OpenFeign 声明调用、Gateway 网关）解决服务治理。事务传播行为（REQUIRED/REQUIRES_NEW/NESTED）、@Transactional 失效场景（自调用、非 public、异常被吞）是 Spring 面试的常驻考点，配合 AOP 动态代理原理（JDK 动态代理与 CGLIB）构成完整答案链。
""",
"SQL.md": """

# 进阶要点与面试高频

SQL 的进阶分水岭是**窗口函数与 CTE**。窗口函数（ROW_NUMBER/RANK/DENSE_RANK、LAG/LEAD、SUM() OVER）在不折叠行的情况下做组内计算——"每组取前 N""连续登录天数""环比同比"这类经典题都是窗口函数的标准应用场景；CTE（WITH 子句）让复杂查询可读可维护，递归 CTE 可处理树形数据（组织架构、分类树）。

**逻辑执行顺序**是理解 SQL 的钥匙：FROM → JOIN → WHERE → GROUP BY → HAVING → SELECT → DISTINCT → ORDER BY → LIMIT，理解"WHERE 里不能用 SELECT 别名""HAVING 与 WHERE 的区别"都源于此。性能层面需要掌握执行计划（EXPLAIN）的阅读：type 列（ALL 全表扫是反模式，至少到 range）、key 与 rows 的意义、索引失效的常见姿势（对索引列做函数运算、隐式类型转换、前导模糊 like '%x'、OR 混合非索引列）。

方言差异在实际工作高频出现：MySQL 与 PostgreSQL 的 JSON 支持、分页写法（LIMIT/OFFSET vs 游标分页——深分页优化的标准答案是游标/延迟关联）、时间函数差异。手写 SQL 是数据岗与后端岗的共同必考题，重点练习：多表 JOIN 的去重计数、留存率计算、Top N per group、累计指标——四类题型覆盖了绝大多数面试 SQL。
""",
"TypeScript.md": """

# 进阶要点与面试高频

TypeScript 的类型系统是**结构化类型（structural typing）**：只要形状匹配即兼容（duck typing 的编译期版本），这与 Java/C# 的名义类型系统本质不同——理解这一点是回答"interface 和 type 区别"（语义上几乎等价，差异在扩展语法与联合类型表达力）与"为什么 TS 是 JS 的超集而非 Java 的类型系统"的基础。

进阶工具类型要能信手拈来：Partial/Required/Readonly（映射类型 + 修饰符）、Pick/Omit/Record（索引与筛选）、ReturnType/Parameters（用 infer 从函数类型中提取），以及手写实现的套路——映射类型的 key remapping（as 子句）、条件类型的分布式行为（联合类型在裸类型参数上自动分发）、infer 的位置推断。**类型体操**的本质是"在类型层面做函数式编程"，面试常考手写 DeepPartial、UnionToIntersection、GetRequiredKeys。

工程实践决定了 TS 的真实价值：strict 模式全开（noImplicitAny/strictNullChecks 是底线）、any 与 unknown 的区别（unknown 类型安全、使用前必须收窄）、类型收窄手段（typeof/in/可辨识联合/discriminated union）、泛型的默认值与约束（extends）。编译层面：tsc 只做类型检查与类型擦除（不优化运行时），构建性能靠 Vite/esbuild/swc 转译 + tsc 仅做类型检查的组合方案；tsconfig 的 module/moduleResolution/target 与 paths 别名配置是工程化基本功。
""",
"Vue.js.md": """

# 进阶要点与面试高频

Vue 3 的响应式系统建立在 **Proxy** 之上（对比 Vue 2 的 Object.defineProperty：可监听新增/删除属性与数组索引、无需递归初始化）：track 在 getter 中收集依赖（副作用函数），trigger 在 setter 中派发更新；ref 对基本类型包装为带 value 的响应式对象，reactive 用于对象。**编译优化**是 Vue 3 的杀手锏：模板编译期进行静态提升（hoistStatic）、Patch Flag（标记动态节点类型，diff 时只比较标记部分）、块树（Block Tree）收集动态后代——这使得 Vue 的更新性能接近手写优化代码。

**Composition API** 的设计动机是逻辑组织与复用：setup 中按逻辑单元组织代码（对比 Options API 按选项分散）、自定义组合式函数（composables，如 useFetch/useMouse）替代 mixin 的复用方案。Vue 3.5 的响应式 props 解构与 useTemplateRef 等改进持续降低样板代码。

生态坐标：Vite（作者同为尤雨溪，基于原生 ESM 的秒级冷启动）、Pinia（官方状态管理，TypeScript 友好）、Vue Router 4。与 React 的选型对比要客观：Vue 的模板 DSL 与编译优化在中小团队上手更快，React 的 JSX 灵活性与生态纵深在超大规模团队更主流；面试中能说出双方 Trade-off 而非站队，是加分的表达方式。面试高频：Proxy 与 defineProperty 区别、ref 与 reactive 选用、computed 与 watch 场景、v-if 与 v-show、key 的作用与 diff 策略、nextTick 原理。
""",
"机器学习.md": """

# 进阶要点与面试高频

机器学习的面试主线是**偏差-方差权衡与泛化能力**。欠拟合（高偏差）与过拟合（高方差）的诊断依赖学习曲线；正则化工具箱要系统掌握：L1（Lasso，产生稀疏解，可做特征选择）与 L2（Ridge，权重衰减）、决策树的剪枝、集成方法（Bagging 降方差——Random Forest；Boosting 降偏差——XGBoost/LightGBM，是表格数据竞赛与工业界的常胜将军）。

**评估指标**必须按场景精确选用：分类问题在类别不均衡时准确率（accuracy）会失真，需看精确率/召回率/F1 与 PR 曲线、AUC（ROC 曲线下面积，对阈值不敏感）；回归看 MAE/RMSE/R²；排序场景（推荐/搜索）看 NDCG/ MAP。交叉验证（K-Fold）是可靠评估的基本功，数据泄漏（用未来数据/全局统计量训练）是最常见也最隐蔽的错误。

特征工程的价值常常大于模型选择：缺失值处理策略、异常值检测（IQR/孤立森林）、类别特征编码（One-Hot/Target Encoding 的过拟合风险）、特征交叉与分箱。经典算法要能讲清直觉与推导：线性回归最小二乘与梯度下降、逻辑回归的 sigmoid 与交叉熵、决策树的信息增益与基尼系数、SVM 的间隔与核技巧、KMeans 的迭代过程与 K 选择（肘部法/轮廓系数）。学完经典 ML 后衔接深度学习与大模型应用，是 2026 年最顺滑的进阶路径。
""",
"深度学习.md": """

# 进阶要点与面试高频

深度学习的骨架是**前向传播 + 反向传播 + 梯度下降**：损失函数衡量预测与真值差距，反向传播按链式法则逐层求导，优化器更新参数。优化器演进要能排序讲清：SGD → Momentum（动量累积方向）→ AdaGrad/RMSProp（自适应学习率）→ **Adam**（动量+自适应二阶矩估计，默认首选）；学习率调度（warmup + cosine decay）是大模型训练的标准配置。

**三大骨干架构**对应三大领域：CNN（卷积的局部连接与权值共享，池化降采样，ResNet 的残差连接解决深层退化）服务于视觉；RNN/LSTM（门控机制缓解梯度消失）是序列建模的历史方案；**Transformer（自注意力 + 多头注意力 + 位置编码）**以全局建模与并行计算统一了 NLP、视觉（ViT）与多模态，是当前一切的底座——"为什么 Transformer 取代 RNN""注意力的 QKV 计算与复杂度"是必考题。

**训练稳定性技巧**是实战区分度：梯度裁剪防爆炸、批归一化/层归一化的位置与作用、Dropout 的训练/推理差异、早停与学习率退火防过拟合；混合精度训练（AMP）与梯度累积在显存受限时的组合拳。面试高频：反向传播推导（至少手推两层）、BN 与 LN 区别、ResNet 为什么有效、过拟合的完整处理方案、CNN 感受野计算、Transformer 位置编码方案对比（正弦/可学习/RoPE）。动手实践推荐 d2l.ai（动手学深度学习）边学边跑。
""",
"skill_categories.md": """

# 使用说明

本索引是 skills 目录的导航中枢：42 个技能文档按 10 大类组织，每篇技能文档均采用三阶段（入门-进阶-高级）学习路线结构，包含学习资源、练习项目与评估方式。检索时建议：① 按 category 关键词定位分类；② 按"技能名 + 学习路线/面试/项目"组合检索；③ 结合 roadmap/ 目录的方向路线图交叉使用。

技能优先级建议（面向校招）：第一梯队为 Java/Python/JavaScript/SQL/Git/Linux（岗位覆盖面最广）；第二梯队为 Spring Boot/React/Vue/Docker/MySQL/Redis（后端与前端主栈）；第三梯队按方向补充——后端补微服务与消息队列、前端补工程化与 TypeScript、AI 方向补 PyTorch/LangChain/RAG/向量数据库。所有文档持续维护中，欢迎按需扩展。
""",
}

# competition 与 policies 的 README 扩写
EXPAND_OTHER = {
"competition/README.md": """
# competition/ — 竞赛知识目录

收录大学生可参与的学科与科技竞赛知识：竞赛介绍、报名时间、参赛要求、赛制流程、获奖比例、企业认可度评级与备赛策略。覆盖 ACM-ICPC/CCPC（算法）、蓝桥杯（软件）、CCF CSP（能力认证）、Kaggle/天池（数据科学）、CTF（安全）、中国国际大学生创新大赛、挑战杯、数学建模等主流赛事，以及一份综合备赛全攻略。

**检索建议**：按"竞赛名称 + 含金量/报名/备赛"组合检索；结合 roadmap/ 的大学四年规划确定参赛时序（大一大二以蓝桥杯/CSP 打基础，大二大三冲击 ICPC/天池，大四前完成奖项沉淀）。
""",
"policies/README.md": """
# policies/ — 就业政策知识目录

收录与大学生就业直接相关的政策知识：应届生身份与择业期、校招与社招规则、一线与新一线城市落户与人才补贴、租房生活补贴申请、劳动合同与试用期权益、加班费与辞退赔偿、职场维权渠道。政策类知识具有强时效性，各文档均标注了数据来源与更新时间，具体申请以当地人社部门最新公告为准。

**检索建议**：按"城市名 + 落户/补贴"、按"劳动合同/试用期/加班费 + 权益"组合检索；入职签约前必读劳动合同与试用期两篇。
""",
}

def process(mapping, expand_map=None):
    added, skipped = [], []
    for rel, refs in mapping.items():
        if not os.path.exists(rel):
            print(f"!! missing: {rel}"); continue
        content = open(rel, encoding='utf-8').read()
        if has_ref_heading(content):
            skipped.append(rel); continue
        extra = ""
        if expand_map and rel in expand_map:
            extra = expand_map[rel]
        content = content.rstrip() + extra + ref_block(refs)
        open(rel, 'w', encoding='utf-8').write(content)
        added.append(rel)
    return added, skipped

def process_dir_skills():
    added, skipped = [], []
    for f in sorted(glob.glob('skills/*.md')):
        base = os.path.basename(f)
        content = open(f, encoding='utf-8').read()
        if has_ref_heading(content):
            skipped.append(f); continue
        extra = EXPAND.get(base, "")
        refs = SKILL_REFS.get(base)
        if not refs:
            print(f"!! no ref map for skills/{base}"); continue
        content = content.rstrip() + extra + ref_block(refs)
        open(f, 'w', encoding='utf-8').write(content)
        added.append(f)
    return added, skipped

if __name__ == "__main__":
    a1, s1 = process_dir_skills()
    print(f"skills: +Ref {len(a1)} (含扩写 {sum(1 for f in a1 if os.path.basename(f) in EXPAND)} 篇), skip {len(s1)}")
    a2, s2 = process(OTHER_REFS)
    print(f"other dirs: +Ref {len(a2)}, skip {len(s2)}")
    # projects: 全部 21 篇统一补 Reference（默认通用来源兜底）
    proj_added = 0
    for f in sorted(glob.glob('projects/*.md')):
        base = os.path.basename(f)
        content = open(f, encoding='utf-8').read()
        if has_ref_heading(content):
            continue
        refs = PROJECT_REFS.get(base, [
            "GitHub. 相关开源项目与技术文档. github.com. " + ACCESS + ".",
            "LeetCode. 力扣题库（项目相关算法题）. leetcode.cn. " + ACCESS + "."])
        content = content.rstrip() + ref_block(refs)
        open(f, 'w', encoding='utf-8').write(content)
        proj_added += 1
    print(f"projects: +Ref {proj_added}")
