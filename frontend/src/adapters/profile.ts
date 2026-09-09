/**
 * 文件名称：profile.ts
 * 文件作用：用户资料 / 画像结果 → 3D 房间与 Overlay 所需结构，字段转换集中在此。
 */

import type {
  AnalysisHistoryItem,
  CompetitionItem,
  InternshipItem,
  ProfileAnalysisResponse,
  ProjectItem,
  SkillItem,
  UserProfile,
} from "@/api/types";

export interface IntroView {
  name: string;
  brand: string;
  motto1: string;
  motto2: string;
}

export interface OverlayItem {
  label: string;
  date: string;
  description?: string;
  image?: string | null;
  url?: string | null;
}

export interface OverlayPayload {
  id: string;
  layout: "experience_list" | "profile_form" | "analysis_report";
  title: string;
  items?: OverlayItem[];
  emptyText?: string;
  platformConfig: { label: string; color?: string; icon?: string };
  analysis?: ProfileAnalysisResponse | null;
  history?: AnalysisHistoryItem[];
}

const EMPTY_INTRO: IntroView = {
  name: "尚未建档",
  brand: "点击右上角档案完善资料",
  motto1: "填写学校、专业与技能",
  motto2: "让 AI 生成你的就业画像",
};

function joinNonEmpty(parts: Array<string | undefined | null>, sep = " · "): string {
  return parts.map((p) => (p ?? "").trim()).filter(Boolean).join(sep);
}

export function toIntroView(profile: UserProfile | null): IntroView {
  if (!profile) return EMPTY_INTRO;
  const motto = (profile.bio || "").trim();
  return {
    name: profile.name || "未填写姓名",
    brand: joinNonEmpty([profile.school, profile.grade]) || "完善学校与年级",
    motto1: motto ? wrapLine(motto, 0, 22) : joinNonEmpty([profile.major, profile.target_city]) || "补充自我评价",
    motto2: motto ? wrapLine(motto, 22, 22) : profile.target_salary ? `期望薪资：${profile.target_salary}` : "生成画像前请先保存档案",
  };
}

function wrapLine(text: string, start: number, len: number): string {
  const slice = text.slice(start, start + len);
  if (!slice) return "";
  return start + len < text.length ? `${slice}…` : slice;
}

export function toJourneyView(profile: UserProfile | null): { left: string; right: string; subtitle: string } {
  if (!profile) {
    return { left: "待填写", right: "待填写", subtitle: "保存档案后显示学校与实习" };
  }
  const intern = profile.internships?.[0];
  const left = joinNonEmpty([profile.grade, profile.school]) || "学校未填";
  const right = intern
    ? joinNonEmpty([intern.company, intern.position], " ")
    : profile.major || "实习未填";
  return {
    left: shorten(left, 12),
    right: shorten(right, 12),
    subtitle: joinNonEmpty([profile.major, profile.target_city]) || "我的学习与实践路径",
  };
}

function shorten(text: string, max: number): string {
  return text.length > max ? `${text.slice(0, max)}…` : text;
}

export function toSkillBalloonLabels(profile: UserProfile | null, fallback: string[]): string[] {
  const names = (profile?.skills ?? []).map((s) => s.name).filter(Boolean);
  return fallback.map((label, i) => names[i] || label);
}

function mapCompetition(item: CompetitionItem): OverlayItem {
  return {
    label: item.name,
    date: joinNonEmpty([item.level, item.award, item.competition_date], " · ") || "日期未填",
    description: item.description || "",
  };
}

function mapProject(item: ProjectItem): OverlayItem {
  return {
    label: item.name,
    date: joinNonEmpty([item.role, item.start_date, item.end_date], " · ") || "项目经历",
    description: item.description || (item.tech_stack || []).join(" / "),
  };
}

function mapInternship(item: InternshipItem): OverlayItem {
  return {
    label: `${item.company} · ${item.position}`,
    date: joinNonEmpty([item.start_date, item.end_date], " — ") || "实习经历",
    description: item.description || (item.tech_stack || []).join(" / "),
  };
}

export function toExperienceOverlays(profile: UserProfile | null): {
  competitions: OverlayPayload;
  internships: OverlayPayload;
  projects: OverlayPayload;
} {
  const competitions = profile?.competitions ?? [];
  const internships = profile?.internships ?? [];
  const projects = profile?.projects ?? [];
  return {
    competitions: {
      id: "exp-competitions",
      layout: "experience_list",
      title: "竞赛经历",
      items: competitions.map(mapCompetition),
      emptyText: "暂无竞赛记录。打开档案页添加后，这里会同步显示。",
      platformConfig: { label: "竞赛", icon: "🏆" },
    },
    internships: {
      id: "exp-internships",
      layout: "experience_list",
      title: "实习经历",
      items: internships.map(mapInternship),
      emptyText: "暂无实习记录。打开档案页补充公司与岗位。",
      platformConfig: { label: "实习", icon: "📅" },
    },
    projects: {
      id: "exp-projects",
      layout: "experience_list",
      title: "项目经历",
      items: projects.map(mapProject),
      emptyText: "暂无项目记录。打开档案页添加项目后再回来查看。",
      platformConfig: { label: "项目", icon: "👑" },
    },
  };
}

export function toProfileFormOverlay(): OverlayPayload {
  return {
    id: "profile-form",
    layout: "profile_form",
    title: "就业档案",
    platformConfig: { label: "档案", icon: "✎" },
  };
}

export function toAnalysisOverlay(
  analysis: ProfileAnalysisResponse | null,
  history: AnalysisHistoryItem[] = []
): OverlayPayload {
  return {
    id: "analysis-report",
    layout: "analysis_report",
    title: analysis ? "就业画像报告" : "就业画像",
    analysis,
    history,
    emptyText: "尚未生成画像。先保存档案，再点击生成。",
    platformConfig: { label: "画像", icon: "✦" },
  };
}

/** PUT 整组替换时去掉后端回写的 id / user_id */
export function toSkillPayload(skills: SkillItem[]): SkillItem[] {
  return skills.map(({ name, proficiency, description }) => ({
    name,
    proficiency,
    description: description || "",
  }));
}

export function toProjectPayload(projects: ProjectItem[]): ProjectItem[] {
  return projects.map(({ name, role, description, tech_stack, start_date, end_date }) => ({
    name,
    role,
    description,
    tech_stack: tech_stack || [],
    start_date,
    end_date,
  }));
}

export function toCompetitionPayload(items: CompetitionItem[]): CompetitionItem[] {
  return items.map(({ name, level, award, description, competition_date }) => ({
    name,
    level,
    award,
    description,
    competition_date,
  }));
}

export function toInternshipPayload(items: InternshipItem[]): InternshipItem[] {
  return items.map(({ company, position, description, tech_stack, start_date, end_date }) => ({
    company,
    position,
    description,
    tech_stack: tech_stack || [],
    start_date,
    end_date,
  }));
}
