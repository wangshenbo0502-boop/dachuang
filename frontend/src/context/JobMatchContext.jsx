/**
 * 文件名称：JobMatchContext.jsx
 * 文件作用：岗位匹配房间共享状态 —— 浏览列表、搜索筛选、技能匹配结果。
 */

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { getJobList, startMatch } from "../api/jobMatch";
import { ApiError } from "../api/index";
import { toCardView } from "../adapters/jobMatch";
import { useUser } from "./UserContext";

const JobMatchContext = createContext(null);

export function useJobMatch() {
  const ctx = useContext(JobMatchContext);
  if (!ctx) throw new Error("useJobMatch must be used within JobMatchProvider");
  return ctx;
}

export function JobMatchProvider({ children }) {
  const { profile, currentUserId } = useUser();

  const [mode, setMode] = useState("browse");
  const [keyword, setKeyword] = useState("");
  const [category, setCategory] = useState("全部");
  const [jobs, setJobs] = useState([]);
  const [matchResults, setMatchResults] = useState([]);
  const [matchMap, setMatchMap] = useState({});
  const [total, setTotal] = useState(0);

  const [listLoading, setListLoading] = useState(false);
  const [listError, setListError] = useState(null);
  const [matchLoading, setMatchLoading] = useState(false);
  const [matchError, setMatchError] = useState(null);
  const [notice, setNotice] = useState("");

  const fetchJobs = useCallback(async (kw = keyword, cat = category) => {
    setListLoading(true);
    setListError(null);
    try {
      const params = { page: 1, page_size: 8 };
      if (kw.trim()) params.keyword = kw.trim();
      if (cat && cat !== "全部") params.category = cat;
      const res = await getJobList(params);
      const items = res.data?.items ?? [];
      setJobs(items);
      setTotal(res.data?.total ?? items.length);
    } catch (err) {
      setJobs([]);
      setTotal(0);
      const msg = err instanceof ApiError ? err.message : err?.message || "岗位列表加载失败";
      setListError(
        msg.includes("HTTP") || msg.includes("网络") || err?.status === 0
          ? "岗位数据暂不可用，请检查后端服务"
          : msg
      );
    } finally {
      setListLoading(false);
    }
  }, [keyword, category]);

  useEffect(() => {
    fetchJobs("", "全部");
    // 仅挂载时拉首屏
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const searchJobs = useCallback(() => {
    setMode("browse");
    setMatchError(null);
    fetchJobs(keyword, category);
  }, [fetchJobs, keyword, category]);

  const runMatch = useCallback(async () => {
    setNotice("");
    setMatchError(null);
    const skills = (profile?.skills ?? []).map((s) => s.name?.trim()).filter(Boolean);
    if (!profile || skills.length === 0) {
      setNotice("请先在就业画像中完善并保存技能");
      return;
    }
    setMatchLoading(true);
    try {
      const res = await startMatch({
        skills,
        job_category: category === "全部" ? null : category,
        top_k: 8,
        user_id: currentUserId ?? null,
      });
      const matches = res.data?.matches ?? [];
      setMatchResults(matches);
      const map = {};
      matches.forEach((m) => { map[m.job_id] = m; });
      setMatchMap(map);
      setMode("match");
    } catch (err) {
      setMatchError(err instanceof ApiError ? err.message : err?.message || "匹配失败");
    } finally {
      setMatchLoading(false);
    }
  }, [profile, category, currentUserId]);

  const backToBrowse = useCallback(() => {
    setMode("browse");
    setMatchError(null);
  }, []);

  const displayItems = useMemo(() => {
    const raw = mode === "match" ? matchResults : jobs;
    return raw.map(toCardView);
  }, [mode, matchResults, jobs]);

  const value = useMemo(() => ({
    mode,
    keyword,
    setKeyword,
    category,
    setCategory,
    jobs,
    matchResults,
    matchMap,
    displayItems,
    total,
    listLoading,
    listError,
    matchLoading,
    matchError,
    notice,
    setNotice,
    fetchJobs,
    searchJobs,
    runMatch,
    backToBrowse,
  }), [
    mode, keyword, category, jobs, matchResults, matchMap, displayItems, total,
    listLoading, listError, matchLoading, matchError, notice,
    fetchJobs, searchJobs, runMatch, backToBrowse,
  ]);

  return <JobMatchContext.Provider value={value}>{children}</JobMatchContext.Provider>;
}
