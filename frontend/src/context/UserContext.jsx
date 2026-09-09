/**
 * 文件名称：UserContext.jsx
 * 文件作用：当前学生档案与就业画像状态；user_id 持久化到 localStorage。
 */

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { createUser, getUser, replaceCompetitions, replaceInternships, replaceProjects, replaceSkills, updateUser } from "../api/user";
import { getAnalysis, getAnalysisHistory, startAnalysis } from "../api/analysis";
import {
  toCompetitionPayload,
  toInternshipPayload,
  toProjectPayload,
  toSkillPayload,
} from "../adapters/profile";
import { ApiError } from "../api/index";

const USER_ID_KEY = "aijob:current_user_id";

const UserContext = createContext(null);

export function useUser() {
  const ctx = useContext(UserContext);
  if (!ctx) {
    throw new Error("useUser must be used within UserProvider");
  }
  return ctx;
}

function readStoredId() {
  try {
    const raw = localStorage.getItem(USER_ID_KEY);
    if (!raw) return null;
    const n = Number(raw);
    return Number.isFinite(n) && n > 0 ? n : null;
  } catch {
    return null;
  }
}

export function UserProvider({ children }) {
  const [currentUserId, setCurrentUserIdState] = useState(readStoredId);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const [analysis, setAnalysis] = useState(null);
  const [analysisHistory, setAnalysisHistory] = useState([]);
  const [analysisLoading, setAnalysisLoading] = useState(false);
  const [analysisError, setAnalysisError] = useState(null);

  const setCurrentUserId = useCallback((id) => {
    setCurrentUserIdState(id);
    if (id == null) localStorage.removeItem(USER_ID_KEY);
    else localStorage.setItem(USER_ID_KEY, String(id));
  }, []);

  const fetchProfile = useCallback(async (id = currentUserId) => {
    if (id == null) {
      setProfile(null);
      return null;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await getUser(id);
      setProfile(res.data);
      setCurrentUserId(id);
      return res.data;
    } catch (err) {
      setProfile(null);
      if (err instanceof ApiError && (err.status === 404 || err.code === 3001 || err.code === 2001)) {
        setCurrentUserId(null);
        setError("本地档案已失效，请重新创建");
      } else {
        setError(err?.message || "加载档案失败");
      }
      return null;
    } finally {
      setLoading(false);
    }
  }, [currentUserId, setCurrentUserId]);

  const loadHistory = useCallback(async (id = currentUserId) => {
    if (id == null) {
      setAnalysisHistory([]);
      return;
    }
    try {
      const res = await getAnalysisHistory(id);
      setAnalysisHistory(Array.isArray(res.data) ? res.data : []);
    } catch {
      setAnalysisHistory([]);
    }
  }, [currentUserId]);

  useEffect(() => {
    if (currentUserId != null) {
      fetchProfile(currentUserId).then((p) => {
        if (p) loadHistory(p.id);
      });
    }
    // 仅启动时拉一次
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const saveBasic = useCallback(async (data) => {
    setLoading(true);
    setError(null);
    try {
      if (currentUserId == null) {
        const res = await createUser(data);
        setProfile(res.data);
        setCurrentUserId(res.data.id);
        return res.data;
      }
      const res = await updateUser(currentUserId, data);
      setProfile(res.data);
      return res.data;
    } catch (err) {
      setError(err?.message || "保存资料失败");
      throw err;
    } finally {
      setLoading(false);
    }
  }, [currentUserId, setCurrentUserId]);

  const saveSkills = useCallback(async (skills) => {
    if (currentUserId == null) throw new Error("请先创建档案");
    const res = await replaceSkills(currentUserId, toSkillPayload(skills));
    setProfile((prev) => (prev ? { ...prev, skills: res.data } : prev));
    return res.data;
  }, [currentUserId]);

  const saveProjects = useCallback(async (projects) => {
    if (currentUserId == null) throw new Error("请先创建档案");
    const res = await replaceProjects(currentUserId, toProjectPayload(projects));
    setProfile((prev) => (prev ? { ...prev, projects: res.data } : prev));
    return res.data;
  }, [currentUserId]);

  const saveCompetitions = useCallback(async (items) => {
    if (currentUserId == null) throw new Error("请先创建档案");
    const res = await replaceCompetitions(currentUserId, toCompetitionPayload(items));
    setProfile((prev) => (prev ? { ...prev, competitions: res.data } : prev));
    return res.data;
  }, [currentUserId]);

  const saveInternships = useCallback(async (items) => {
    if (currentUserId == null) throw new Error("请先创建档案");
    const res = await replaceInternships(currentUserId, toInternshipPayload(items));
    setProfile((prev) => (prev ? { ...prev, internships: res.data } : prev));
    return res.data;
  }, [currentUserId]);

  const runAnalysis = useCallback(async (targetJob = "") => {
    if (currentUserId == null) {
      setAnalysisError("请先创建并保存档案");
      throw new Error("请先创建并保存档案");
    }
    setAnalysisLoading(true);
    setAnalysisError(null);
    try {
      const payload = { user_id: currentUserId };
      if (targetJob) payload.target_job = targetJob;
      const res = await startAnalysis(payload);
      setAnalysis(res.data);
      await loadHistory(currentUserId);
      return res.data;
    } catch (err) {
      setAnalysisError(err?.message || "画像生成失败");
      throw err;
    } finally {
      setAnalysisLoading(false);
    }
  }, [currentUserId, loadHistory]);

  const loadAnalysisItem = useCallback(async (id) => {
    setAnalysisLoading(true);
    setAnalysisError(null);
    try {
      const res = await getAnalysis(id);
      setAnalysis(res.data);
      return res.data;
    } catch (err) {
      setAnalysisError(err?.message || "加载画像失败");
      throw err;
    } finally {
      setAnalysisLoading(false);
    }
  }, []);

  const value = useMemo(() => ({
    currentUserId,
    profile,
    loading,
    error,
    hasUser: profile != null,
    analysis,
    analysisHistory,
    analysisLoading,
    analysisError,
    fetchProfile,
    saveBasic,
    saveSkills,
    saveProjects,
    saveCompetitions,
    saveInternships,
    runAnalysis,
    loadHistory,
    loadAnalysisItem,
  }), [
    currentUserId, profile, loading, error, analysis, analysisHistory,
    analysisLoading, analysisError, fetchProfile, saveBasic, saveSkills,
    saveProjects, saveCompetitions, saveInternships, runAnalysis, loadHistory, loadAnalysisItem,
  ]);

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
}
