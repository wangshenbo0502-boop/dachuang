"""
文件名称：skill_synonyms.py
文件作用：技能同义词/别名映射表，用于提升岗位匹配的准确率。
将技能的不同表述统一映射到标准名称，解决"Spring" vs "SpringBoot"等匹配问题。
"""

# 技能别名 -> 标准化名称
SKILL_ALIAS_MAP: dict[str, str] = {
    # ── Java 生态 ──
    "java": "java",
    "j2ee": "java",
    "javaee": "java",
    "spring": "spring",
    "springboot": "springboot",
    "spring boot": "springboot",
    "springcloud": "springcloud",
    "spring cloud": "springcloud",
    "springmvc": "springmvc",
    "spring mvc": "springmvc",
    "mybatis": "mybatis",
    "mybatisplus": "mybatis",
    "mybatis-plus": "mybatis",
    "hibernate": "hibernate",
    "jpa": "jpa",
    "maven": "maven",
    "gradle": "gradle",

    # ── Python 生态 ──
    "django": "django",
    "flask": "flask",
    "fastapi": "fastapi",
    "tornado": "tornado",

    # ── 前端 ──
    "js": "javascript",
    "javascript": "javascript",
    "ecmascript": "javascript",
    "es6": "javascript",
    "ts": "typescript",
    "typescript": "typescript",
    "react": "react",
    "reactjs": "react",
    "react.js": "react",
    "vue": "vue",
    "vuejs": "vue",
    "vue.js": "vue",
    "vue3": "vue",
    "vue2": "vue",
    "angular": "angular",
    "angularjs": "angular",
    "angular.js": "angular",
    "jquery": "jquery",
    "html": "html",
    "html5": "html",
    "css": "css",
    "css3": "css",
    "sass": "sass",
    "scss": "sass",
    "less": "less",
    "webpack": "webpack",
    "vite": "vite",
    "babel": "babel",
    "node": "nodejs",
    "nodejs": "nodejs",
    "node.js": "nodejs",
    "npm": "npm",
    "yarn": "yarn",
    "pnpm": "pnpm",

    # ── 数据库 ──
    "mysql": "mysql",
    "mariadb": "mysql",
    "postgresql": "postgresql",
    "postgres": "postgresql",
    "pg": "postgresql",
    "sqlite": "sqlite",
    "mongodb": "mongodb",
    "mongo": "mongodb",
    "redis": "redis",
    "elasticsearch": "elasticsearch",
    "es": "elasticsearch",
    "cassandra": "cassandra",
    "neo4j": "neo4j",
    "oracle": "oracle",
    "sqlserver": "sqlserver",
    "sql server": "sqlserver",
    "mssql": "sqlserver",

    # ── 消息队列 ──
    "rabbitmq": "rabbitmq",
    "rabbit": "rabbitmq",
    "kafka": "kafka",
    "rocketmq": "rocketmq",
    "activemq": "activemq",
    "pulsar": "pulsar",
    "redis mq": "redis",

    # ── 云原生/DevOps ──
    "docker": "docker",
    "kubernetes": "kubernetes",
    "k8s": "kubernetes",
    "k3s": "kubernetes",
    "jenkins": "jenkins",
    "gitlab": "gitlab",
    "gitlab ci": "gitlab",
    "github": "github",
    "github actions": "github",
    "ansible": "ansible",
    "terraform": "terraform",
    "nginx": "nginx",
    "apache": "apache",
    "tomcat": "tomcat",
    "linux": "linux",
    "ubuntu": "linux",
    "centos": "linux",
    "unix": "linux",
    "shell": "shell",
    "bash": "shell",

    # ── AI/ML ──
    "ml": "machine_learning",
    "machine learning": "machine_learning",
    "机器学习": "machine_learning",
    "ai": "ai",
    "人工智能": "ai",
    "dl": "deep_learning",
    "deep learning": "deep_learning",
    "深度学习": "deep_learning",
    "nlp": "nlp",
    "自然语言处理": "nlp",
    "cv": "computer_vision",
    "computer vision": "computer_vision",
    "计算机视觉": "computer_vision",
    "pytorch": "pytorch",
    "tensorflow": "tensorflow",
    "tf": "tensorflow",
    "keras": "keras",
    "scikit-learn": "scikit_learn",
    "sklearn": "scikit_learn",
    "scikit": "scikit_learn",
    "pandas": "pandas",
    "numpy": "numpy",
    "matplotlib": "matplotlib",
    "opencv": "opencv",

    # ── 移动端 ──
    "android": "android",
    "ios": "ios",
    "swift": "swift",
    "kotlin": "kotlin",
    "flutter": "flutter",
    "react native": "react_native",
    "rn": "react_native",

    # ── 其他语言 ──
    "c": "c",
    "cpp": "c++",
    "c++": "c++",
    "cplusplus": "c++",
    "c#": "csharp",
    "csharp": "csharp",
    "go": "go",
    "golang": "go",
    "rust": "rust",
    "ruby": "ruby",
    "php": "php",
    "scala": "scala",
    "r": "r",
    "perl": "perl",
    "matlab": "matlab",

    # ── 版本控制 ──
    "git": "git",
    "svn": "svn",
    "subversion": "svn",

    # ── 测试 ──
    "junit": "junit",
    "pytest": "pytest",
    "unittest": "unittest",
    "selenium": "selenium",
    "jmeter": "jmeter",
    "postman": "postman",

    # ── 大数据 ──
    "hadoop": "hadoop",
    "spark": "spark",
    "flink": "flink",
    "hive": "hive",
    "hbase": "hbase",
    "airflow": "airflow",
    "etl": "etl",
    "数据仓库": "data_warehouse",
    "data warehouse": "data_warehouse",

    # ── 其他常用 ──
    "rest": "restful_api",
    "restful": "restful_api",
    "rest api": "restful_api",
    "restful api": "restful_api",
    "graphql": "graphql",
    "grpc": "grpc",
    "websocket": "websocket",
    "oauth": "oauth",
    "jwt": "jwt",
    "sso": "sso",
    "微服务": "microservices",
    "microservices": "microservices",
    "microservice": "microservices",
    "分布式": "distributed_systems",
    "distributed": "distributed_systems",
    "高并发": "high_concurrency",
    "并发编程": "concurrency",
    "concurrency": "concurrency",
    "数据结构": "data_structures",
    "data structures": "data_structures",
    "算法": "algorithms",
    "algorithms": "algorithms",
    "设计模式": "design_patterns",
    "design patterns": "design_patterns",
    "网络协议": "network_protocols",
    "tcp": "network_protocols",
    "http": "network_protocols",
    "https": "network_protocols",
}


def normalize_skill(skill_name: str) -> str:
    """将技能名标准化为统一形式。

    Args:
        skill_name: 原始技能名（大小写不敏感）

    Returns:
        标准化后的技能名，未匹配则返回原始名称的小写形式
    """
    key = skill_name.strip().lower()
    return SKILL_ALIAS_MAP.get(key, key)


def normalize_skills(skill_names: list[str]) -> list[str]:
    """批量标准化技能名列表，去重后返回。

    Args:
        skill_names: 原始技能名列表

    Returns:
        去重后的标准化技能名列表
    """
    seen: set[str] = set()
    result: list[str] = []
    for name in skill_names:
        normalized = normalize_skill(name)
        if normalized and normalized not in seen:
            seen.add(normalized)
            result.append(normalized)
    return result


def is_skill_match(skill_a: str, skill_b: str) -> bool:
    """判断两个技能名是否匹配（考虑别名）。

    Args:
        skill_a: 技能名A
        skill_b: 技能名B

    Returns:
        是否匹配
    """
    return normalize_skill(skill_a) == normalize_skill(skill_b)