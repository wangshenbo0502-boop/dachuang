/**
 * 文件名称：contactInfo.js
 * 文件作用：联系房间展示用的团队信息（静态配置，后期可直接改这里）。
 * 说明：后端暂无留言/反馈接口（见 docs/02 第 11 章），表单发送走 mailto。
 */

export const CONTACT_INFO = {
  teamName: "asffga",
  email: "3477399270@qq.com",
  phone: "13233334444",
  intro:
    "asffga 团队打造 AI 就业竞争力分析助手，帮助学生梳理就业画像、匹配岗位并规划成长路径，欢迎随时联系交流。",
};

export function mailtoUrl({ subject = "", body = "", fromEmail = "" } = {}) {
  const lines = [];
  if (fromEmail) lines.push(`来自：${fromEmail}`);
  if (body) lines.push("", body);
  const params = new URLSearchParams();
  if (subject) params.set("subject", subject);
  const text = lines.join("\n").trim();
  if (text) params.set("body", text);
  const qs = params.toString();
  return `mailto:${CONTACT_INFO.email}${qs ? `?${qs}` : ""}`;
}

export function telUrl() {
  return `tel:${CONTACT_INFO.phone}`;
}
