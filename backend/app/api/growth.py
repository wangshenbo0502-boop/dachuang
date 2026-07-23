"""
文件名称：growth.py
文件作用：成长规划相关 API 接口定义。
当前阶段仅定义路由框架，具体接口逻辑后续实现。

未来功能：
    - 基于能力评估生成成长路线
    - 学习资源推荐
    - 阶段性目标设定与跟踪
    - 进度可视化数据
"""

from fastapi import APIRouter

router = APIRouter()

# TODO: POST /plan         - 生成个性化成长规划
# TODO: GET  /plan/{id}    - 获取成长规划详情
# TODO: PUT  /progress     - 更新学习进度
# TODO: GET  /resources    - 获取推荐学习资源
