/**
 * 文件名称：ProfileOverlay.jsx
 * 文件作用：就业档案表单 + 画像报告，嵌入 GlobalOverlay 纸张卡片。
 */

import { useEffect, useState } from "react";
import { useUser } from "../../context/UserContext";

const PROFICIENCY = ["了解", "熟悉", "掌握", "精通"];

const emptyBasic = {
  name: "",
  school: "",
  major: "",
  grade: "",
  bio: "",
  email: "",
  phone: "",
  target_city: "",
  target_salary: "",
};

export default function ProfileOverlay({ onShowReport }) {
  const {
    profile,
    loading,
    error,
    hasUser,
    saveBasic,
    saveSkills,
    saveProjects,
    saveCompetitions,
    saveInternships,
    runAnalysis,
    analysisLoading,
    analysisError,
    analysisHistory,
    loadAnalysisItem,
  } = useUser();

  const [tab, setTab] = useState("basic");
  const [form, setForm] = useState(emptyBasic);
  const [targetJob, setTargetJob] = useState("");
  const [notice, setNotice] = useState("");
  const [skills, setSkills] = useState([]);
  const [projects, setProjects] = useState([]);
  const [competitions, setCompetitions] = useState([]);
  const [internships, setInternships] = useState([]);
  const [draft, setDraft] = useState({
    skill: { name: "", proficiency: "熟悉", description: "" },
    project: { name: "", role: "", description: "", tech_stack: "", start_date: "", end_date: "" },
    competition: { name: "", level: "校级", award: "参与奖", description: "", competition_date: "" },
    internship: { company: "", position: "", description: "", tech_stack: "", start_date: "", end_date: "" },
  });

  useEffect(() => {
    if (!profile) {
      setForm(emptyBasic);
      setSkills([]);
      setProjects([]);
      setCompetitions([]);
      setInternships([]);
      return;
    }
    setForm({
      name: profile.name || "",
      school: profile.school || "",
      major: profile.major || "",
      grade: profile.grade || "",
      bio: profile.bio || "",
      email: profile.email || "",
      phone: profile.phone || "",
      target_city: profile.target_city || "",
      target_salary: profile.target_salary || "",
    });
    setSkills(profile.skills || []);
    setProjects(profile.projects || []);
    setCompetitions(profile.competitions || []);
    setInternships(profile.internships || []);
  }, [profile]);

  const field = (key) => ({
    value: form[key],
    onChange: (e) => setForm((s) => ({ ...s, [key]: e.target.value })),
  });

  const handleSaveBasic = async () => {
    setNotice("");
    try {
      await saveBasic({
        name: form.name.trim(),
        school: form.school.trim(),
        major: form.major.trim(),
        grade: form.grade.trim(),
        bio: form.bio,
        email: form.email,
        phone: form.phone,
        target_city: form.target_city,
        target_salary: form.target_salary,
      });
      setNotice("资料已保存");
    } catch {
      /* error 已在 store */
    }
  };

  const handleGenerate = async () => {
    setNotice("");
    try {
      const data = await runAnalysis(targetJob.trim());
      onShowReport?.(data);
    } catch {
      /* store 已记错误 */
    }
  };

  return (
    <div className="profile-overlay">
      {error && <p className="profile-banner err">{error}</p>}
      {notice && <p className="profile-banner ok">{notice}</p>}
      {hasUser && <p className="profile-hint">档案 #{profile.id} · {profile.name}</p>}
      {!hasUser && <p className="profile-hint">尚未建档，填写必填项后创建。</p>}

      <div className="profile-tabs">
        {[
          ["basic", "资料"],
          ["skills", "技能"],
          ["projects", "项目"],
          ["competitions", "竞赛"],
          ["internships", "实习"],
          ["analysis", "画像"],
        ].map(([key, label]) => (
          <button
            key={key}
            type="button"
            className={tab === key ? "on" : ""}
            onClick={() => setTab(key)}
          >
            {label}
          </button>
        ))}
      </div>

      {tab === "basic" && (
        <div className="profile-grid">
          <label>姓名 *<input {...field("name")} placeholder="张三" /></label>
          <label>学校 *<input {...field("school")} placeholder="某大学" /></label>
          <label>专业 *<input {...field("major")} placeholder="计算机科学与技术" /></label>
          <label>年级 *<input {...field("grade")} placeholder="大三" /></label>
          <label>意向城市<input {...field("target_city")} placeholder="杭州" /></label>
          <label>期望薪资<input {...field("target_salary")} placeholder="15k-20k" /></label>
          <label className="span2">自我评价<textarea {...field("bio")} rows={3} /></label>
          <button type="button" className="profile-btn" disabled={loading} onClick={handleSaveBasic}>
            {loading ? "保存中…" : hasUser ? "更新资料" : "创建档案"}
          </button>
        </div>
      )}

      {tab === "skills" && (
        <ExperienceEditor
          disabled={!hasUser}
          rows={skills}
          render={(s, i) => (
            <div key={i} className="exp-row">
              <b>{s.name}</b> <span>{s.proficiency}</span>
              <button type="button" onClick={() => setSkills(skills.filter((_, j) => j !== i))}>移除</button>
            </div>
          )}
          onSave={() => saveSkills(skills).then(() => setNotice("技能已保存"))}
          addLabel="添加技能"
          onAdd={() => {
            if (!draft.skill.name.trim()) return;
            setSkills([...skills, { ...draft.skill }]);
            setDraft((d) => ({ ...d, skill: { name: "", proficiency: "熟悉", description: "" } }));
          }}
        >
          <input
            placeholder="技能名"
            value={draft.skill.name}
            onChange={(e) => setDraft((d) => ({ ...d, skill: { ...d.skill, name: e.target.value } }))}
          />
          <select
            value={draft.skill.proficiency}
            onChange={(e) => setDraft((d) => ({ ...d, skill: { ...d.skill, proficiency: e.target.value } }))}
          >
            {PROFICIENCY.map((p) => <option key={p}>{p}</option>)}
          </select>
        </ExperienceEditor>
      )}

      {tab === "projects" && (
        <ExperienceEditor
          disabled={!hasUser}
          rows={projects}
          render={(p, i) => (
            <div key={i} className="exp-row">
              <b>{p.name}</b> <span>{p.role}</span>
              <button type="button" onClick={() => setProjects(projects.filter((_, j) => j !== i))}>移除</button>
            </div>
          )}
          onSave={() => saveProjects(projects).then(() => setNotice("项目已保存"))}
          addLabel="添加项目"
          onAdd={() => {
            const p = draft.project;
            if (!p.name.trim() || !p.role.trim() || !p.description.trim()) return;
            setProjects([...projects, { ...p, tech_stack: p.tech_stack.split(/[,，、\s]+/).filter(Boolean) }]);
            setDraft((d) => ({ ...d, project: { name: "", role: "", description: "", tech_stack: "", start_date: "", end_date: "" } }));
          }}
        >
          <input placeholder="项目名 *" value={draft.project.name} onChange={(e) => setDraft((d) => ({ ...d, project: { ...d.project, name: e.target.value } }))} />
          <input placeholder="角色 *" value={draft.project.role} onChange={(e) => setDraft((d) => ({ ...d, project: { ...d.project, role: e.target.value } }))} />
          <input placeholder="描述 *" className="span2" value={draft.project.description} onChange={(e) => setDraft((d) => ({ ...d, project: { ...d.project, description: e.target.value } }))} />
        </ExperienceEditor>
      )}

      {tab === "competitions" && (
        <ExperienceEditor
          disabled={!hasUser}
          rows={competitions}
          render={(c, i) => (
            <div key={i} className="exp-row">
              <b>{c.name}</b> <span>{c.award}</span>
              <button type="button" onClick={() => setCompetitions(competitions.filter((_, j) => j !== i))}>移除</button>
            </div>
          )}
          onSave={() => saveCompetitions(competitions).then(() => setNotice("竞赛已保存"))}
          addLabel="添加竞赛"
          onAdd={() => {
            if (!draft.competition.name.trim()) return;
            setCompetitions([...competitions, { ...draft.competition }]);
            setDraft((d) => ({ ...d, competition: { name: "", level: "校级", award: "参与奖", description: "", competition_date: "" } }));
          }}
        >
          <input placeholder="竞赛名 *" value={draft.competition.name} onChange={(e) => setDraft((d) => ({ ...d, competition: { ...d.competition, name: e.target.value } }))} />
          <input placeholder="奖项" value={draft.competition.award} onChange={(e) => setDraft((d) => ({ ...d, competition: { ...d.competition, award: e.target.value } }))} />
        </ExperienceEditor>
      )}

      {tab === "internships" && (
        <ExperienceEditor
          disabled={!hasUser}
          rows={internships}
          render={(c, i) => (
            <div key={i} className="exp-row">
              <b>{c.company}</b> <span>{c.position}</span>
              <button type="button" onClick={() => setInternships(internships.filter((_, j) => j !== i))}>移除</button>
            </div>
          )}
          onSave={() => saveInternships(internships).then(() => setNotice("实习已保存"))}
          addLabel="添加实习"
          onAdd={() => {
            if (!draft.internship.company.trim() || !draft.internship.position.trim()) return;
            setInternships([...internships, {
              ...draft.internship,
              tech_stack: draft.internship.tech_stack.split(/[,，、\s]+/).filter(Boolean),
            }]);
            setDraft((d) => ({ ...d, internship: { company: "", position: "", description: "", tech_stack: "", start_date: "", end_date: "" } }));
          }}
        >
          <input placeholder="公司 *" value={draft.internship.company} onChange={(e) => setDraft((d) => ({ ...d, internship: { ...d.internship, company: e.target.value } }))} />
          <input placeholder="岗位 *" value={draft.internship.position} onChange={(e) => setDraft((d) => ({ ...d, internship: { ...d.internship, position: e.target.value } }))} />
        </ExperienceEditor>
      )}

      {tab === "analysis" && (
        <div className="profile-analysis">
          <label>目标岗位（可选）
            <input value={targetJob} onChange={(e) => setTargetJob(e.target.value)} placeholder="如 Java后端开发工程师" />
          </label>
          <button type="button" className="profile-btn" disabled={!hasUser || analysisLoading} onClick={handleGenerate}>
            {analysisLoading ? "生成中，请稍候…" : "生成就业画像"}
          </button>
          {analysisError && <p className="profile-banner err">{analysisError}</p>}
          {!hasUser && <p className="profile-hint">创建档案后才能调用画像接口。</p>}
          {analysisHistory.length > 0 && (
            <div className="history-list">
              <h4>历史记录</h4>
              {analysisHistory.map((h) => (
                <button
                  key={h.id}
                  type="button"
                  className="hist-item"
                  onClick={async () => {
                    const data = await loadAnalysisItem(h.id);
                    onShowReport?.(data);
                  }}
                >
                  #{h.id} {h.target_job || "未指定岗位"} · {h.comprehensive_score} 分 · {h.created_at}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function ExperienceEditor({ disabled, rows, render, onSave, onAdd, addLabel, children }) {
  const [busy, setBusy] = useState(false);
  const [err, setErr] = useState("");
  return (
    <div>
      {disabled && <p className="profile-hint">请先创建档案</p>}
      {rows.length ? rows.map(render) : <p className="profile-hint">暂无记录</p>}
      <div className="profile-add">{children}
        <button type="button" disabled={disabled} onClick={onAdd}>{addLabel}</button>
      </div>
      <button
        type="button"
        className="profile-btn"
        disabled={disabled || busy}
        onClick={async () => {
          setErr("");
          setBusy(true);
          try {
            await onSave();
          } catch (e) {
            setErr(e?.message || "保存失败");
          } finally {
            setBusy(false);
          }
        }}
      >
        {busy ? "保存中…" : "整组保存"}
      </button>
      {err && <p className="profile-banner err">{err}</p>}
    </div>
  );
}

export function AnalysisReport({ analysis }) {
  if (!analysis?.result) {
    return <p className="profile-hint">暂无画像结果。</p>;
  }
  const r = analysis.result;
  return (
    <div className="analysis-report">
      <div className="score-row">
        <div className="big">{r.comprehensive_score}</div>
        <div>
          <div>{analysis.target_job || "未指定岗位"}</div>
          <div>{r.current_level}</div>
          {analysis.is_mock && <span className="mock-tag">Mock 演示</span>}
        </div>
      </div>
      <p>{r.profile_summary}</p>
      <h4>技术方向</h4>
      <p>{r.technical_direction}</p>
      {r.core_advantages?.length > 0 && (
        <>
          <h4>核心优势</h4>
          <ul>{r.core_advantages.map((x) => <li key={x}>{x}</li>)}</ul>
        </>
      )}
      {r.areas_to_improve?.length > 0 && (
        <>
          <h4>待提升</h4>
          <ul>{r.areas_to_improve.map((x) => <li key={x}>{x}</li>)}</ul>
        </>
      )}
      {r.recommended_directions?.length > 0 && (
        <>
          <h4>推荐方向</h4>
          <ul>
            {r.recommended_directions.map((d) => (
              <li key={d.job_title}>{d.job_title} · {d.match_rate}%</li>
            ))}
          </ul>
        </>
      )}
    </div>
  );
}
