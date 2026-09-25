export interface ApiEnvelope<T> { code: number; message: string; data: T }
export type Proficiency = "了解" | "熟悉" | "掌握" | "精通";
export interface Skill { id?: number; user_id?: number; name: string; proficiency: Proficiency; description: string }
export interface Project { id?: number; user_id?: number; name: string; role: string; description: string; tech_stack: string[]; start_date: string | null; end_date: string | null }
export interface Competition { id?: number; user_id?: number; name: string; level: string; award: string; description: string; competition_date: string | null }
export interface Internship { id?: number; user_id?: number; company: string; position: string; description: string; tech_stack: string[]; start_date: string | null; end_date: string | null }
export interface StudentProfile { id:number; name:string; school:string; major:string; grade:string; bio:string; email:string; phone:string; target_city:string; target_salary:string; skills:Skill[]; projects:Project[]; competitions:Competition[]; internships:Internship[]; created_at:string; updated_at:string }
export interface AnalysisResult { profile_summary:string; technical_direction:string; core_advantages:string[]; current_level:string; recommended_directions:Array<{job_title:string;match_rate:number}>; areas_to_improve:string[]; comprehensive_score:number; skill_assessment:Record<string,number> }
export interface AnalysisResponse { id?:number; user_id?:number; target_job:string; result:AnalysisResult; is_mock:boolean; created_at?:string }
export interface AnalysisHistory { id:number; target_job:string; technical_direction:string; comprehensive_score:number; created_at?:string }
export interface JobBrief { job_id:string; title:string; category?:string; tags:string[]; snippet:string }
export interface JobDetail extends JobBrief { content:string; metadata:Record<string,unknown> }
export interface MatchedJob extends JobBrief { match_score:number; matched_skills:string[]; missing_skills:string[]; match_reason?:string; learning_suggestions?:string[]; interview_focus?:string[] }
export interface JobListResponse { total:number; items:JobBrief[]; keyword?:string }
export interface JobMatchResponse { user_skills:string[]; total_matches:number; matches:MatchedJob[]; record_id?:number }
export interface ResumeResult { optimized_projects:Array<{project_name:string;original:string;optimized:string;highlight_tags:string[]}>; optimized_skills:Array<{original:string;optimized:string}>; overall_suggestions:string[]; personal_summary:string; resume_score:number }
export interface ResumeResponse { id?:number; target_job:string; result:ResumeResult; is_mock:boolean; created_at?:string }
export interface ResumeHistory { id:number; target_job:string; resume_score:number; created_at?:string }
export interface GrowthResult { current_situation:string; ability_gaps:Array<{skill:string;importance:string;difficulty:string;description:string}>; learning_roadmap:Array<{stage:string;focus:string;tasks:string[];milestone:string}>; recommended_projects:Array<{name:string;description:string;tech_stack:string[];difficulty:string}>; recommended_resources:string[]; interview_prep_tips:string[]; expected_timeline:string }
export interface GrowthResponse { id?:number; target_job:string; result:GrowthResult; is_mock:boolean; created_at?:string }
export interface GrowthHistory { id:number; target_job:string; expected_timeline:string; created_at?:string }
export interface KnowledgeResult { id?:number; document_id?:number; doc_id?:string; title?:string; source?:string; category?:string; content:string; score?:number; metadata?:Record<string,unknown> }
export interface ChatMessage { role:"user"|"assistant"; content:string }
export interface ChatTurnResponse { reply:string; question_number:number; finished:boolean; extracted:Record<string,unknown>; missing:string[] }
export interface ChatConversationResponse { reply:string; suggested_action?:"profile"|"resume"|"analysis"|"growth"|"jobs"|null; extracted?:Record<string,unknown> }
