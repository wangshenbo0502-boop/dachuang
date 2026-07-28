---
title: Linux运维
category: skills
tags: [运维, Linux, 服务器]
source: [鸟哥的Linux私房菜, Linux官方文档, 掘金运维专栏, BOSS直聘运维岗位JD]
last_update: 2026-07-28
---

# Linux运维

> Linux 是服务器操作系统的绝对主流，是后端、运维、DevOps、安全岗位的基础技能，掌握 Linux 是进入云计算时代的必备通行证。

- **就业影响**: 高（几乎所有技术岗位的基础要求，Linux 运维向云原生/DevOps 转型薪资涨幅 30%-100%）
- **前置技能**: 操作系统基础
- **关联系能**: Docker, Kubernetes, DevOps, 网络安全
- **学习总周期**: 约 9 周（可根据基础调整）
- **推荐学习方式**: 命令行实操 + Shell 脚本练习 + 项目实战 + 云平台实践

---

## 技能图谱概览

```
Linux 运维
├── 基础操作
│   ├── 文件与目录管理
│   ├── 用户与权限管理
│   ├── 进程与服务管理
│   └── 文本处理工具
├── Shell 编程
│   ├── 基础语法
│   ├── 流程控制
│   ├── 函数与数组
│   └── awk/sed 高级
├── 系统管理
│   ├── 磁盘与文件系统
│   ├── 性能监控与调优
│   ├── 日志管理
│   └── 定时任务
├── 网络与安全
│   ├── 网络配置与排障
│   ├── 防火墙配置
│   └── 系统安全加固
├── 高级运维
│   ├── 高可用集群
│   ├── 自动化运维（Ansible）
│   ├── 监控体系
│   └── 故障排查
└── 云原生方向
    ├── Docker 容器化
    ├── Kubernetes 编排
    └── IaC 基础设施即代码
```

---

## 阶段 1 — 目标：了解（预估 2 周）

**学习主题：**
- 常用文件操作命令（ls/cd/pwd/mkdir/rm/cp/mv/touch/ln 软硬链接/find 高级用法/grep 正则）
- 进程与系统管理（ps aux/top/htop/kill/nice/renice/nohup/&/jobs/fg/bg/进程优先级）
- 网络基础命令（ifconfig/ip addr/ping/netstat/ss/traceroute/mtr/curl/wget/telnet/nc）
- 文件权限与用户管理（chmod 数字与符号法/chown/chgrp/useradd/usermod/userdel/sudo 配置/visudo）
- Shell 脚本基础（变量定义与引用、echo/printf 输出、read 输入、管道 |、重定向 > >> <、$() 命令替换、基础脚本结构）
- 软件包管理（yum/rpm 与 apt/dpkg 对比、仓库配置 repo/source.list、软件安装卸载查询、yum groups、PPA）
- 服务管理（systemctl/service、服务启停状态、enable/disable 开机自启、journalctl 日志查看、systemd 单元文件基础）
- 文件系统基础（ext4/xfs 文件系统、mount/umount 挂载、fdisk/parted 磁盘分区、swap 分区创建与启用、df/du 磁盘使用）
- 文本处理工具（cat/more/less/head/tail/sort/uniq/wc/cut/paste/tr 基础用法）
- Vim 编辑器基础（三种模式、常用命令、配置 .vimrc、多文件编辑）

**学习资源：**
- [鸟哥的Linux私房菜 - 基础篇](https://linux.vbird.org/) — 经典教程 · 免费 · 入门 · 中文
- [Linux 官方文档](https://www.kernel.org/doc/html/latest/) — 官方文档 · 免费 · 入门 · 英文
- [菜鸟教程 - Linux 教程](https://www.runoob.com/linux/linux-tutorial.html) — 在线教程 · 免费 · 入门 · 中文
- [掘金 - Linux 运维专栏](https://juejin.cn/) — 技术社区 · 免费 · 入门 · 中文
- [Linux man 手册](https://man7.org/linux/man-pages/) — 参考手册 · 免费 · 入门 · 英文

**练习项目：**
- 在虚拟机中安装 CentOS Stream 或 Ubuntu Server，配置静态网络与 SSH 远程登录，设置防火墙规则
- 编写一个 Shell 脚本，实现自动备份指定目录到指定位置，按日期命名，并记录备份日志
- 使用 find 和 grep 组合命令，在 /var/log 目录中查找包含 error 关键字的所有日志文件并统计行数
- 配置 sudo 权限，创建一个普通用户，让其只能执行特定的管理员命令（如重启服务、查看日志）
- 用 systemd 管理一个自定义服务（如一个 Python Web 应用），实现开机自启、状态监控与日志查看
- 使用 Vim 编辑一个 100 行的配置文件，练习光标移动、复制粘贴、查找替换、多窗口编辑等操作

**评估方式：** 实操 — 能独立完成 Linux 系统安装与基础配置，熟练使用 40+ 常用命令，能编写简单的 Shell 脚本完成自动化任务，通过 RHCSA 级别基础操作考核，熟练使用 Vim 编辑文件

---

## 阶段 2 — 目标：熟悉（预估 3 周）

**学习主题：**
- Shell 脚本进阶（条件判断 if/elif/else/case、循环 for/while/until/break/continue、函数定义与调用、数组操作、正则表达式、sed 流编辑器、awk 文本处理、grep 高级用法）
- 性能监控与调优入门（top/htop 详解、free 内存、vmstat 虚拟内存、iostat 磁盘 IO、sar 系统活动报告、dstat 综合监控、CPU/内存/磁盘/网络瓶颈分析思路）
- 日志管理（rsyslog 配置与日志转发、logrotate 日志轮转配置、日志分析常用命令、ELK Stack 基础概念、journalctl 高级用法）
- 定时任务与计划任务（crontab 语法与配置、at 一次性任务、anacron 异步定时、定时任务排错、环境变量问题、日志记录）
- 网络配置与排障（网卡配置文件、路由表 route/ip route、防火墙 iptables 四表五链/firewalld zone、TCP Wrappers、网络故障排查方法论、tcpdump 抓包）
- 磁盘管理进阶（LVM 逻辑卷管理 PV/VG/LV、创建扩展缩小快照、磁盘配额 quota、RAID 基础 0/1/5/10、磁盘健康检测 smartctl、文件系统检查 fsck）
- 进程与服务深度管理（systemd 单元文件详解、socket 激活、资源限制 cgroup、服务依赖关系、.target 与运行级别、故障排查）
- 安全基础配置（SSH 安全加固、防火墙策略、SELinux/AppArmor 基础、fail2ban 防暴力破解、端口扫描与入侵检测基础、rootkit 检测）
- 编译安装与源码管理（源码编译三步走 configure/make/make install、依赖问题解决、环境变量配置、卸载方法）

**学习资源：**
- [鸟哥的Linux私房菜 - 服务器篇](https://linux.vbird.org/) — 经典教程 · 免费 · 进阶 · 中文
- [掘金 - Linux 运维进阶专栏](https://juejin.cn/) — 技术社区 · 免费 · 进阶 · 中文
- [Linux Performance - Brendan Gregg](https://www.brendangregg.com/linuxperf.html) — 性能调优 · 免费 · 进阶 · 英文
- [《Linux Shell 脚本攻略》](https://book.douban.com/subject/26923289/) — 技术书籍 · 付费 · 进阶 · 中文
- [Linux 就该这么学](https://www.linuxprobe.com/) — 在线教程 · 部分免费 · 进阶 · 中文

**练习项目：**
- 编写一个系统监控 Shell 脚本（150 行以上），监控 CPU、内存、磁盘、网络使用率，超过阈值发送告警邮件，并记录历史数据
- 使用 LVM 管理磁盘，完成 PV 创建、VG 创建、LV 创建、扩展、缩小、快照、删除等完整操作流程
- 配置 rsyslog + logrotate，实现多台服务器日志集中收集与按天轮转，保留 30 天日志
- 使用 iptables/firewalld 配置一套完整的服务器防火墙规则，包括开放必要端口、限制 SSH 访问频率、防止 SYN Flood、端口转发
- 使用 awk/sed 处理一份 Nginx 访问日志（10 万行以上），统计 TOP10 IP、访问最多的 URL、状态码分布、响应时间分布、爬虫流量占比
- 搭建一个 LAMP/LNMP 环境，从源码编译安装 Nginx/Apache、MySQL/MariaDB、PHP，配置虚拟主机与数据库连接

**评估方式：** 实操 — 能编写 100 行以上的复杂 Shell 脚本，独立完成系统性能分析与瓶颈定位，熟练配置 LVM 与防火墙，能通过日志分析定位常见系统故障，具备独立搭建 LAMP/LNMP 环境的能力

---

## 阶段 3 — 目标：掌握（预估 4 周）

**学习主题：**
- 系统调优深入（内核参数优化 sysctl.conf、文件描述符限制 ulimit、TCP 协议栈调优、内存管理调优、IO 调度算法选择、NUMA 架构优化、大页内存）
- 高可用集群架构（Keepalived + LVS/HAProxy、双机热备、VRRP 协议、故障自动切换、健康检查、脑裂问题处理、负载均衡算法）
- 自动化运维（Ansible 入门与进阶、Playbook 编写、Roles 设计、Inventory 管理、变量与模板 Jinja2、批量部署与配置管理、Ansible Tower/AWX）
- 安全加固与等保合规（系统安全基线、漏洞扫描与修复、入侵检测 HIDS OSSEC/OSquery、等保三级系统加固要求、审计规则 auditd、文件完整性检查）
- 故障排查方法论（5W2H 分析法、故障树分析 FTA、从现象到根因的排查思路、经典故障案例库、事后复盘与改进、MTTR/MTBF 指标）
- 企业级运维规范（变更管理流程、发布流程灰度/蓝绿/金丝雀、监控告警体系分级、应急预案制定、SOP 标准操作流程、运维文档管理）
- 云原生运维基础（Docker 容器化深入、Kubernetes 核心概念 Pod/Deployment/Service、云平台运维 AWS/阿里云、IaC 基础设施即代码 Terraform、GitOps）
- 监控体系建设（Prometheus + Grafana 深度使用、Exporter 生态、PromQL 进阶、告警规则与 Alertmanager、Zabbix 深度定制、SLO/SLA/SLI 管理）
- 数据库运维基础（MySQL 主从复制、备份与恢复、性能优化、慢查询分析、Redis 运维、MongoDB 基础运维）
- 运维开发能力（Python 运维脚本开发、运维平台设计思路、API 接口开发、前端基础、运维效能工具链）

**学习资源：**
- [BOSS直聘 - 高级运维工程师 JD 分析](https://www.zhipin.com/) — 招聘调研 · 免费 · 高级 · 中文
- [掘金 - 云原生运维专栏](https://juejin.cn/) — 技术社区 · 免费 · 高级 · 中文
- [Ansible 官方文档](https://docs.ansible.com/) — 官方文档 · 免费 · 高级 · 英文
- [《性能之巅：洞悉系统、企业与云计算》](https://book.douban.com/subject/26585782/) — 技术书籍 · 付费 · 高级 · 中文
- [Prometheus 官方文档](https://prometheus.io/docs/) — 官方文档 · 免费 · 高级 · 英文

**练习项目：**
- 使用 Ansible 编写一套完整的 Web 集群自动化部署 Playbook，包含 Nginx 负载均衡 + Tomcat 应用 + MySQL 主从 + Redis 缓存，实现一键部署
- 搭建 Keepalived + Nginx + Tomcat 高可用集群，实现主备自动切换、健康检查、会话保持，验证故障自动转移
- 基于 Prometheus + Grafana + Alertmanager 搭建一套完整的服务器监控告警体系，覆盖 CPU/内存/磁盘/网络/服务状态/数据库，配置分级告警
- 对一台生产级服务器进行全面安全加固，包括系统基线、SSH 安全、防火墙、SELinux、审计规则、入侵检测，输出加固报告与基线检查脚本
- 模拟一次线上重大故障（如服务雪崩、磁盘满、网络中断、数据库慢查询），完成故障排查、应急恢复、根因分析与复盘报告
- 搭建一套 MySQL 主从复制 + 读写分离环境，配置备份策略、监控告警与故障切换方案

**评估方式：** 综合实战 — 能独立设计并实现企业级自动化运维方案，完成高可用集群搭建与调优，建立完整的监控告警体系，具备独立处理线上重大故障的能力，达到中级运维工程师及以上水平，具备向云原生/DevOps 方向进阶的基础

---

## 常见面试题

1. **基础类**：Linux 系统的启动流程是怎样的？从开机到登录界面经历了哪些阶段？
2. **进程管理**：什么是僵尸进程和孤儿进程？如何产生和处理？
3. **磁盘管理**：LVM 的原理是什么？PV、VG、LV 三者的关系是什么？LVM 有哪些优缺点？
4. **性能调优**：如何排查系统 CPU 占用过高的问题？请描述完整的排查思路和用到的工具。
5. **网络排障**：用户反馈网站访问慢，如何从 Linux 服务器端排查网络问题？
6. **Shell 脚本**：如何批量替换目录下所有文件中的某个字符串？请至少写出三种方法。
7. **安全加固**：Linux 服务器被入侵后，如何进行应急响应和系统加固？
8. **高可用**：Keepalived 的工作原理是什么？VRRP 协议如何实现故障自动切换？脑裂问题如何解决？
9. **自动化运维**：Ansible 的工作原理是什么？和 SaltStack、Puppet 相比有什么优缺点？
10. **职业发展**：Linux 运维工程师的职业发展路径有哪些？如何向 DevOps/SRE/云原生方向转型？

---

## 学习路径建议

- **入门阶段（1-2个月）**：掌握 Linux 基础命令和 Shell 脚本基础，熟悉文件系统、用户管理、进程管理、网络配置，考取 RHCSA 认证或同等水平，能独立完成服务器基础配置与日常维护。
- **进阶阶段（2-5个月）**：深入学习 Shell 脚本编程、性能监控与调优、LVM 磁盘管理、防火墙配置、日志管理、服务部署，掌握 LAMP/LNMP 环境搭建，具备中级运维工程师的基础能力。
- **深入阶段（5-10个月）**：学习 Ansible 自动化运维、Keepalived 高可用、Prometheus 监控、MySQL 运维、Docker 容器化、Kubernetes 入门，开始向云原生和 DevOps 方向转型。
- **职业发展**：传统运维 → 自动化运维 → DevOps/SRE → 云原生架构师/技术专家，薪资随能力提升呈现阶梯式增长，向云原生转型普遍有 30%-100% 的薪资涨幅。
- **持续学习**：关注掘金、思否、Linux 中国等技术社区，学习 Terraform、Kubernetes、Service Mesh 等云原生技术，考取 CKA、CKAD、RHCE 等认证，保持对新技术的学习热情。
