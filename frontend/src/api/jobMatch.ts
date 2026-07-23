/**
 * 文件名称：jobMatch.ts
 * 文件作用：岗位匹配相关 API 请求封装。
 * 当前阶段仅定义请求函数框架，具体接口后续实现。
 */

import http from "./index";

// TODO: 获取岗位列表
export function getJobList(params?: object) {}

// TODO: 获取岗位详情
export function getJobDetail(id: string) {}

// TODO: 触发岗位匹配
export function startJobMatch(data: object) {}

// TODO: 获取匹配结果
export function getMatchResult(id: string) {}
