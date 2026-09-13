/**
 * 文件名称：JobMatchPanel.jsx
 * 文件作用：岗位匹配房间轻量入口 + GlobalOverlay 内搜索/匹配表单。
 */

import { useScene } from "../../context/SceneContext";
import { useJobMatch } from "../../context/JobMatchContext";
import { JOB_CATEGORIES, toJobMatchPanelOverlay } from "../../adapters/jobMatch";
import "../../styles/JobMatchPanel.scss";

/** 嵌入 GlobalOverlay 的完整控制表单 */
export function JobMatchPanelBody({ getStaggerStyle }) {
  const {
    mode,
    keyword,
    setKeyword,
    category,
    setCategory,
    total,
    displayItems,
    listLoading,
    listError,
    matchLoading,
    matchError,
    notice,
    searchJobs,
    runMatch,
    backToBrowse,
  } = useJobMatch();

  const isEmpty = !listLoading && displayItems.length === 0;
  const modeLabel = mode === "match" ? "技能匹配结果" : "岗位浏览";

  return (
    <div className="job-match-form" style={getStaggerStyle?.(120)}>
      <div className="job-match-header">
        <span className="job-match-mode">{modeLabel}</span>
        {mode === "match" && (
          <button type="button" className="job-match-link" onClick={backToBrowse}>
            返回浏览
          </button>
        )}
      </div>

      {mode === "browse" && (
        <div className="job-match-filters">
          <input
            type="search"
            placeholder="关键词（如 Java、前端）"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && searchJobs()}
            aria-label="岗位关键词"
          />
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            aria-label="岗位分类"
          >
            {JOB_CATEGORIES.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
          <button type="button" className="job-match-btn" disabled={listLoading} onClick={searchJobs}>
            {listLoading ? "搜索中…" : "搜索"}
          </button>
        </div>
      )}

      <div className="job-match-actions">
        <button
          type="button"
          className="job-match-btn primary"
          disabled={matchLoading}
          onClick={runMatch}
        >
          {matchLoading ? "匹配中…" : "开始匹配"}
        </button>
        {mode === "browse" && total > 0 && (
          <span className="job-match-count">共 {total} 个岗位</span>
        )}
      </div>

      {notice && <p className="job-match-banner warn">{notice}</p>}
      {listError && mode === "browse" && <p className="job-match-banner err">{listError}</p>}
      {matchError && <p className="job-match-banner err">{matchError}</p>}
      {isEmpty && !listError && !matchError && (
        <p className="job-match-hint">
          {mode === "match" ? "未找到匹配岗位，请调整技能或分类后重试。" : "暂无岗位，请更换关键词或分类。"}
        </p>
      )}
      {listLoading && mode === "browse" && (
        <p className="job-match-hint">正在加载岗位…</p>
      )}
    </div>
  );
}

/** 场景中仅保留小型入口，不遮挡天空与卡片 */
export default function JobMatchPanel() {
  const { currentRoom, isInRoom, openOverlay } = useScene();
  const { listError, matchError } = useJobMatch();

  if (!isInRoom || currentRoom !== "gallery") return null;

  const toast = listError || matchError;

  return (
    <div className="job-match-entry" role="region" aria-label="岗位搜索入口">
      {toast && (
        <p className="job-match-toast" role="status">
          {toast.includes("HTTP") || toast.includes("网络")
            ? "岗位数据暂不可用，请检查后端服务"
            : toast}
        </p>
      )}
      <button
        type="button"
        className="job-match-fab"
        onClick={() => openOverlay(toJobMatchPanelOverlay())}
        aria-label="打开岗位搜索与匹配"
      >
        岗位搜索
      </button>
    </div>
  );
}
