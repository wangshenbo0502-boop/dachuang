/**
 * 文件名称：JobMatchOverlay.jsx
 * 文件作用：岗位详情与匹配信息展示，嵌入 GlobalOverlay 纸张卡片。
 */

export function JobDetailBody({ job, match, blocks, loadError }) {
  if (loadError) {
    return <p className="job-match-banner err">{loadError}</p>;
  }
  if (!job) {
    return <p className="job-match-hint">暂无岗位详情。</p>;
  }

  return (
    <div className="job-detail-body">
      <div className="job-meta-row">
        <span className="job-tag">{job.category}</span>
        {(job.tags ?? []).map((t) => (
          <span key={t} className="job-tag muted">{t}</span>
        ))}
      </div>

      {match?.match_score != null && (
        <div className="job-match-score">
          <span className="big">{Math.round(match.match_score)}</span>
          <span>匹配度</span>
        </div>
      )}

      {match && (
        <div className="job-match-block">
          {match.matched_skills?.length > 0 && (
            <>
              <h4>已匹配技能</h4>
              <ul>{match.matched_skills.map((s) => <li key={s}>{s}</li>)}</ul>
            </>
          )}
          {match.missing_skills?.length > 0 && (
            <>
              <h4>待补充技能</h4>
              <ul>{match.missing_skills.map((s) => <li key={s}>{s}</li>)}</ul>
            </>
          )}
          {match.match_reason && (
            <>
              <h4>匹配理由</h4>
              <p>{match.match_reason}</p>
            </>
          )}
          {match.learning_suggestions?.length > 0 && (
            <>
              <h4>学习建议</h4>
              <ul>{match.learning_suggestions.map((s) => <li key={s}>{s}</li>)}</ul>
            </>
          )}
          {match.interview_focus?.length > 0 && (
            <>
              <h4>面试重点</h4>
              <ul>{match.interview_focus.map((s) => <li key={s}>{s}</li>)}</ul>
            </>
          )}
        </div>
      )}

      <div className="job-content-blocks">
        {(blocks ?? []).map((b, i) => {
          if (b.type === "h") {
            const Tag = b.level <= 2 ? "h3" : "h4";
            return <Tag key={i}>{b.text}</Tag>;
          }
          if (b.type === "li") {
            return <p key={i} className="job-li">· {b.text}</p>;
          }
          return <p key={i}>{b.text}</p>;
        })}
        {(!blocks || blocks.length === 0) && (
          <p className="job-match-hint">暂无正文内容。</p>
        )}
      </div>
    </div>
  );
}
