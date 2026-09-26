import request,{apiData} from "./request"; import type * as T from "@/types/api";
export const api={
 getUser:(id:number)=>apiData<T.StudentProfile>(request.get(`/users/${id}`)), createUser:(b:object)=>apiData<T.StudentProfile>(request.post("/users",b)), updateUser:(id:number,b:object)=>apiData<T.StudentProfile>(request.put(`/users/${id}`,b)),
 skills:(id:number,v:T.Skill[])=>apiData<T.Skill[]>(request.put(`/users/${id}/skills`,{skills:v})), projects:(id:number,v:T.Project[])=>apiData<T.Project[]>(request.put(`/users/${id}/projects`,{projects:v})), competitions:(id:number,v:T.Competition[])=>apiData<T.Competition[]>(request.put(`/users/${id}/competitions`,{competitions:v})), internships:(id:number,v:T.Internship[])=>apiData<T.Internship[]>(request.put(`/users/${id}/internships`,{internships:v})),
 analysis:(b:object)=>apiData<T.AnalysisResponse>(request.post("/analysis",b)), analysisDetail:(id:number)=>apiData<T.AnalysisResponse>(request.get(`/analysis/${id}`)), analyses:(id:number)=>apiData<T.AnalysisHistory[]>(request.get(`/analysis/user/${id}`)),
 jobs:(p:object)=>apiData<T.JobListResponse>(request.get("/jobs",{params:p})), job:(id:string)=>apiData<T.JobDetail>(request.get(`/jobs/${encodeURIComponent(id)}`)), match:(b:object)=>apiData<T.JobMatchResponse>(request.post("/match",b)),
 resume:(b:object)=>apiData<T.ResumeResponse>(request.post("/resume",b)), resumeDetail:(id:number)=>apiData<T.ResumeResponse>(request.get(`/resume/${id}`)), resumes:(id:number)=>apiData<T.ResumeHistory[]>(request.get(`/resume/user/${id}`)), resumeVersions:(id:number)=>apiData<T.ResumeVersion[]>(request.get(`/resume/versions/user/${id}`)), resumeVersion:(id:number)=>apiData<T.ResumeVersion>(request.get(`/resume/versions/${id}`)), createResumeVersion:(b:object)=>apiData<T.ResumeVersion>(request.post("/resume/versions",b)), updateResumeVersion:(id:number,b:object)=>apiData<T.ResumeVersion>(request.put(`/resume/versions/${id}`,b)),
 growth:(b:object)=>apiData<T.GrowthResponse>(request.post("/growth",b)), growthDetail:(id:number)=>apiData<T.GrowthResponse>(request.get(`/growth/${id}`)), growths:(id:number)=>apiData<T.GrowthHistory[]>(request.get(`/growth/user/${id}`)),
 knowledge:(b:object)=>apiData<{query:string;results:T.KnowledgeResult[]}>(request.post("/knowledge/search",b)),
 chatTurn:(b:object)=>apiData<T.ChatTurnResponse>(request.post("/chat/turn",b)),
 chatProfileTurn:(b:object,signal?:AbortSignal)=>apiData<T.ChatTurnResponse>(request.post("/chat/profile-turn",b,{signal})),
 chatConversation:(b:object)=>apiData<T.ChatConversationResponse>(request.post("/chat/conversation",b)),
 chatResume:(b:object)=>apiData<T.ResumeResponse>(request.post("/chat/generate-resume",b)),
 syncChatProfile:(b:object)=>apiData<T.ChatProfileSyncResponse>(request.post("/chat/sync-profile",b)),
 health:()=>apiData<{status:string;ai_mode:"mock"|"live";modules:string[]}>(request.get("/health"))
};
