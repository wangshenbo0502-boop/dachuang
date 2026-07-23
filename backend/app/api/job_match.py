"""
文件名称：job_match.py
文件作用：岗位匹配相关 API 接口定义。
当前阶段仅定义路由框架，具体接口逻辑后续实现。

未来功能：
    - 岗位列表查询
    - 基于用户画像的岗位智能匹配
    - 岗位详情与技能要求展示
    - 匹配度评分
"""

from fastapi import APIRouter

router = APIRouter()

# TODO: GET  /jobs          - 获取岗位列表
# TODO: GET  /jobs/{id}     - 获取岗位详情
# TODO: POST /match         - 触发岗位智能匹配
# TODO: GET  /match/{id}    - 获取匹配结果
