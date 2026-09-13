/**
 * 文件名称：StudioWorkbenchOverlay.jsx
 * 文件作用：AI 工作台 Overlay — 生成表单与简历/成长报告。
 */

import { useState } from "react";
import { useScene } from "../../context/SceneContext";
import { useUser } from "../../context/UserContext";
import { toGrowthOverlay, toResumeOverlay } from "../../adapters/studio";

export function ResumeFormBody({ getStaggerStyle }) {
  const { openOverlay } = useScene();
  const { hasUser, runResume, resumeLoading, resumeError, studioError } = useUser();
  const [targetJob, setTargetJob] = useState("");
  const [originalResume, setOriginalResume] = useState("");
  const [localErr, setLocalErr] = useState("");

  const handleGenerate = async () => {
    setLocalErr("");
    try {
      const data = await runResume({
        targetJob: targetJob.trim(),
        originalResume: originalResume.trim(),
      });
      openOverlay(toResumeOverlay(data));
    } catch (err) {
      setLocalErr(err?.message || "生成失败");
    }
  };

  return (
    <div className="profile-overlay" style={{ flex: 1, minHeight: 0, overflowY: "auto", ...getStaggerStyle(120) }}>
      {!hasUser && <p className="profile-hint">请先到就业画像房间创建并保存档案，再生成简历优化。</p>}
      <label className="profile-analysis">
        目标岗位 *
        <input value={targetJob} onChange={(e) => setTargetJob(e.target.value)} placeholder="如 Java后端开发工程师" />
      </label>
      <label className="profile-analysis" style={{ marginTop: "0.75rem", display: "flex", flexDirection: "column", gap: "0.3rem" }}>
        原始简历（可选）
        <textarea rows={6} value={originalResume} onChange={(e) => setOriginalResume(e.target.value)} placeholder="粘贴现有简历文本，便于对照优化" />
      </label>
      <button type="button" className="profile-btn" disabled={!hasUser || resumeLoading} onClick={handleGenerate}>
        {resumeLoading ? "生成中，请稍候…" : "生成简历优化"}
      </button>
      {(localErr || resumeError) && <p className="profile-banner err">{localErr || resumeError}</p>}
      {studioError && <p className="profile-banner err">{studioError}</p>}
    </div>
  );
}

export function GrowthFormBody({ getStaggerStyle }) {
  const { openOverlay } = useScene();
  const { hasUser, analysis, runGrowth, growthLoading, growthError, studioError } = useUser();
  const [targetJob, setTargetJob] = useState("");
  const [localErr, setLocalErr] = useState("");

  const handleGenerate = async () => {
    setLocalErr("");
    try {
      const data = await runGrowth({ targetJob: targetJob.trim() });
      openOverlay(toGrowthOverlay(data));
    } catch (err) {
      setLocalErr(err?.message || "生成失败");
    }
  };

  return (
    <div className="profile-overlay" style={{ flex: 1, minHeight: 0, overflowY: "auto", ...getStaggerStyle(120) }}>
      {!hasUser && <p className="profile-hint">请先到就业画像房间创建并保存档案，再生成成长规划。</p>}
      {hasUser && !analysis?.result && (
        <p className="profile-hint">若已有就业画像，规划会附带画像上下文；没有画像也可以直接生成。</p>
      )}
      <label className="profile-analysis">
        目标岗位 *
        <input value={targetJob} onChange={(e) => setTargetJob(e.target.value)} placeholder="如 AI应用开发工程师" />
      </label>
      <button type="button" className="profile-btn" disabled={!hasUser || growthLoading} onClick={handleGenerate}>
        {growthLoading ? "生成中，请稍候…" : "生成成长规划"}
      </button>
      {(localErr || growthError) && <p className="profile-banner err">{localErr || growthError}</p>}
      {studioError && <p className="profile-banner err">{studioError}</p>}
    </div>
  );
}

export function ResumeReport({ resume, loadError, loadingDetail }) {
  if (loadingDetail) return <p className="profile-hint">正在加载优化详情…</p>;
  if (loadError) return <p className="profile-banner err">{loadError}</p>;
  if (!resume?.result) return <p className="profile-hint">暂无简历优化结果。</p>;
  const r = resume.result;
  return (
    <div className="analysis-report">
      <div className="score-row">
        <div className="big">{r.resume_score}</div>
        <div>
          <div>{resume.target_job || "未指定岗位"}</div>
          <div>简历评分</div>
          {resume.is_mock && <span className="mock-tag">Mock 演示</span>}
        </div>
      </div>
      {r.personal_summary && <p>{r.personal_summary}</p>}
      {r.optimized_skills?.length > 0 && (
        <>
          <h4>技能优化</h4>
          <ul>
            {r.optimized_skills.map((s, i) => (
              <li key={`${s.original}-${i}`}>
                <strong>{s.original}</strong>
                {s.optimized ? ` → ${s.optimized}` : ""}
              </li>
            ))}
          </ul>
        </>
      )}
      {r.optimized_projects?.length > 0 && (
        <>
          <h4>项目描述优化</h4>
          {r.optimized_projects.map((p, i) => (
            <div key={`${p.project_name}-${i}`} style={{ marginBottom: "0.8rem" }}>
              <strong>{p.project_name}</strong>
              {p.original && <p style={{ margin: "0.2rem 0", color: "#666" }}>原文：{p.original}</p>}
              {p.optimized && <p style={{ margin: "0.2rem 0" }}>优化：{p.optimized}</p>}
              {p.highlight_tags?.length > 0 && <p style={{ margin: 0, color: "#555" }}>标签：{p.highlight_tags.join("、")}</p>}
            </div>
          ))}
        </>
      )}
      {r.overall_suggestions?.length > 0 && (
        <>
          <h4>总体建议</h4>
          <ul>{r.overall_suggestions.map((x) => <li key={x}>{x}</li>)}</ul>
        </>
      )}
    </div>
  );
}

export function GrowthReport({ growth, loadError, loadingDetail }) {
  if (loadingDetail) return <p className="profile-hint">正在加载规划详情…</p>;
  if (loadError) return <p className="profile-banner err">{loadError}</p>;
  if (!growth?.result) return <p className="profile-hint">暂无成长规划结果。</p>;
  const r = growth.result;
  return (
    <div className="analysis-report">
      <div className="score-row">
        <div className="big" style={{ fontSize: "1.6rem", maxWidth: "40%" }}>{r.expected_timeline || "规划"}</div>
        <div>
          <div>{growth.target_job || "未指定岗位"}</div>
          {growth.is_mock && <span className="mock-tag">Mock 演示</span>}
        </div>
      </div>
      {r.current_situation && (
        <>
          <h4>当前情况</h4>
          <p>{r.current_situation}</p>
        </>
      )}
      {r.ability_gaps?.length > 0 && (
        <>
          <h4>能力差距</h4>
          <ul>
            {r.ability_gaps.map((g, i) => (
              <li key={`${g.skill}-${i}`}>
                <strong>{g.skill}</strong>
                {g.importance ? ` · ${g.importance}` : ""}
                {g.difficulty ? ` · 难度${g.difficulty}` : ""}
                {g.description ? ` — ${g.description}` : ""}
              </li>
            ))}
          </ul>
        </>
      )}
      {r.learning_roadmap?.length > 0 && (
        <>
          <h4>学习路线</h4>
          {r.learning_roadmap.map((stage, i) => (
            <div key={`${stage.stage}-${i}`} style={{ marginBottom: "0.8rem" }}>
              <strong>{stage.stage}</strong>
              {stage.focus && <p style={{ margin: "0.2rem 0" }}>重点：{stage.focus}</p>}
              {stage.tasks?.length > 0 && <ul>{stage.tasks.map((t) => <li key={t}>{t}</li>)}</ul>}
              {stage.milestone && <p style={{ margin: 0, color: "#555" }}>里程碑：{stage.milestone}</p>}
            </div>
          ))}
        </>
      )}
      {r.recommended_projects?.length > 0 && (
        <>
          <h4>推荐项目</h4>
          <ul>
            {r.recommended_projects.map((p, i) => (
              <li key={`${p.name}-${i}`}>
                <strong>{p.name}</strong>
                {p.difficulty ? ` · ${p.difficulty}` : ""}
                {p.description ? ` — ${p.description}` : ""}
                {p.tech_stack?.length ? `（${p.tech_stack.join("、")}）` : ""}
              </li>
            ))}
          </ul>
        </>
      )}
      {r.recommended_resources?.length > 0 && (
        <>
          <h4>推荐资源</h4>
          <ul>{r.recommended_resources.map((x) => <li key={x}>{x}</li>)}</ul>
        </>
      )}
      {r.interview_prep_tips?.length > 0 && (
        <>
          <h4>面试准备</h4>
          <ul>{r.interview_prep_tips.map((x) => <li key={x}>{x}</li>)}</ul>
        </>
      )}
    </div>
  );
}
