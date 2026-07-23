"""
文件名称：resume.py
文件作用：简历优化相关 API 接口定义。
当前阶段仅定义路由框架，具体接口逻辑后续实现。

未来功能：
    - 简历内容解析与结构化
    - AI 简历优化建议
    - 简历模板管理
    - 简历导出（PDF/Word）
"""

from fastapi import APIRouter

router = APIRouter()

# TODO: POST /optimize     - 提交简历进行AI优化
# TODO: GET  /result/{id}  - 获取优化结果
# TODO: GET  /templates    - 获取简历模板列表
# TODO: POST /export       - 导出优化后简历
