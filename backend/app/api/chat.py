"""对话式就业助手：用最多十轮问题采集信息、生成简历并同步档案。"""

from typing import Any

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.ai.deepseek_client import DeepSeekClient
from app.database.session import get_db
from app.schemas.chat import (
    ChatConversationRequest,
    ChatProfileRequest,
    ChatResumeRequest,
    ChatTurnRequest,
    ChatTurnResponse,
)
from app.schemas.resume import ResumeOptimizationRequest, ResumeOptimizationResponse
from app.schemas.user import UserUpdate, UserSkillsReplace, UserProjectsReplace, UserCompetitionsReplace, UserInternshipsReplace
from app.services.resume_service import ResumeService
from app.services.user_service import UserService
from app.utils.response import success

router = APIRouter(prefix="/api/chat", tags=["AI对话式求职助手"])


def _user_context(db: Session, user_id: int) -> dict[str, Any]:
    return UserService(db).get_user_context(user_id).model_dump(mode="json")


def _conversation_text(request: ChatTurnRequest) -> str:
    return "\n".join(f"{m.role}: {m.content}" for m in request.messages)


@router.post("/conversation")
def chat_conversation(request: ChatConversationRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    """通用自由对话，不执行简历采集问卷。"""
    context = _user_context(db, request.user_id)
    system = f"""你是大学生就业服务平台中的 AI 求职助手。请直接、自然地回答用户问题，结合求职、学习、简历和职业发展给出实用建议。
这是用户当前就业档案，仅用于理解上下文：{context}
不要声称已修改档案、简历、分析或成长规划；如果用户表达了新的经历、技能或目标，请先总结并明确告诉用户：可以前往对应功能查看或提交确认。不要编造用户经历，区分“已在档案中”和“本次对话提到”。回答结尾可给出一个最合适的下一步，但不要一次塞入太多选项。"""
    messages = [{"role": "system", "content": system}]
    messages.extend({"role": item.role, "content": item.content} for item in request.messages[-40:])
    reply = DeepSeekClient.instance().chat(messages, temperature=0.65, max_tokens=1800)
    last_user = next((item.content for item in reversed(request.messages) if item.role == "user"), "")
    action = None
    action_keywords = {
        "profile": ("档案", "经历", "技能", "个人信息", "补充资料"),
        "resume": ("简历", "自我介绍", "项目描述", "投递"),
        "analysis": ("竞争力", "能力画像", "优势", "短板", "分析"),
        "growth": ("学习计划", "成长", "提升", "路线", "学习什么"),
        "jobs": ("岗位", "职位", "工作", "匹配", "招聘"),
    }
    for key, keywords in action_keywords.items():
        if any(keyword in last_user for keyword in keywords):
            action = key
            break
    return success({"reply": reply.strip(), "suggested_action": action}, message="回复生成成功")


@router.post("/turn")
def chat_turn(request: ChatTurnRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    """根据聊天上下文提出下一问，并返回结构化信息草稿。"""
    context = _user_context(db, request.user_id)
    question_number = min(sum(1 for m in request.messages if m.role == "assistant") + 1, 10)
    system = """你是一个专业、友好的大学生求职教练。通过最多10个问题，逐步了解学生并帮助生成真实、有竞争力的简历。
严禁编造经历、数字或技能。每轮只问一个最关键的问题，问题要具体，优先追问项目中的目标、个人职责、技术方案和可验证成果。
请严格返回JSON：{"reply":"给用户的一句话和一个问题","finished":false,"extracted":{"target_job":"","bio":"","skills":[],"projects":[],"competitions":[],"internships":[]},"missing":[]}。
extracted只填写本轮对话中有明确依据的信息；技能格式为{name,proficiency,description}，项目格式为{name,role,description,tech_stack}。
当信息足够生成简历或达到第10问时finished=true。"""
    user = f"目标岗位：{request.target_job or '尚未确定'}\n已有档案：{context}\n对话：\n{_conversation_text(request)}"
    result = DeepSeekClient.instance().chat_json(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.45,
        max_tokens=1600,
    )
    response = ChatTurnResponse(
        reply=str(result.get("reply", "请介绍一段最能代表你的项目经历。")),
        question_number=question_number,
        finished=bool(result.get("finished", question_number >= 10)),
        extracted=result.get("extracted", {}),
        missing=result.get("missing", []),
    )
    return success(response.model_dump(mode="json"), message="对话回复生成成功")


@router.post("/profile-turn")
def profile_turn(request: ChatTurnRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    """用最多十轮轻量访谈补全就业档案，结果只作为待审核草稿返回。"""
    context = _user_context(db, request.user_id)
    question_number = min(sum(1 for m in request.messages if m.role == "assistant") + 1, 10)
    system = """你是大学生就业服务平台的档案助手。你的任务是通过最多10轮自然对话，帮用户补全和优化就业档案。
每轮只问一个简单、具体的问题，优先了解姓名、学校专业年级、求职方向、技能、项目、竞赛、实习和个人优势；已有明确资料不要重复追问。
用户不需要填写表格，可以用很短的话回答。严禁编造经历、数字、技能或联系方式，只提取用户明确说过的事实。
请严格返回JSON：{"reply":"自然的一句话加一个问题","finished":false,"extracted":{"name":"","school":"","major":"","grade":"","bio":"","target_city":"","target_salary":"","skills":[],"projects":[],"competitions":[],"internships":[]},"missing":[]}。
技能格式{name,proficiency,description}；项目格式{name,role,description,tech_stack}；竞赛格式{name,level,award,description}；实习格式{company,position,description,tech_stack}。
当关键资料已经足够，或达到第10轮时finished=true。回复要让用户知道可以直接说“没有”或“跳过”。"""
    user = f"已有档案：{context}\n对话：\n{_conversation_text(request)}"
    result = DeepSeekClient.instance().chat_json(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.4,
        max_tokens=1600,
    )
    response = ChatTurnResponse(
        reply=str(result.get("reply", "先从最想找的工作方向开始说起吧？")),
        question_number=question_number,
        finished=bool(result.get("finished", question_number >= 10)),
        extracted=result.get("extracted", {}),
        missing=result.get("missing", []),
    )
    return success(response.model_dump(mode="json"), message="档案访谈回复生成成功")


@router.post("/generate-resume")
def generate_resume(request: ChatResumeRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    """使用现有档案和对话补充信息，直接生成完整简历优化结果。"""
    context = _user_context(db, request.user_id)
    transcript = "\n".join(f"{m.role}: {m.content}" for m in request.messages)
    prompt = f"对话补充信息：\n{transcript[-7000:]}\n\n结构化补充信息：{request.extracted}"
    result = ResumeService(db).optimize_resume(
        ResumeOptimizationRequest(
            user_id=request.user_id,
            target_job=request.target_job,
            original_resume=prompt,
            name=context["name"],
        )
    )
    return success(result.model_dump(mode="json"), message="简历生成完成")


@router.post("/sync-profile")
def sync_profile(request: ChatProfileRequest, db: Session = Depends(get_db)) -> dict[str, Any]:
    """只同步用户确认过的聊天信息，避免自动覆盖已有档案。"""
    profile = request.profile
    service = UserService(db)
    basic_fields = {k: v for k, v in profile.items() if k in {"name", "school", "major", "grade", "bio", "email", "phone", "target_city", "target_salary"} and v}
    if basic_fields:
        service.update_user(request.user_id, UserUpdate(**basic_fields))
    current = service.get_user_context(request.user_id).model_dump(mode="json")
    if isinstance(profile.get("skills"), list) and profile["skills"]:
        skills = list(current.get("skills", []))
        for x in profile["skills"]:
            if not isinstance(x, dict) or not x.get("name"):
                continue
            item = {"name": x["name"], "proficiency": x.get("proficiency") if x.get("proficiency") in {"了解", "熟悉", "掌握", "精通"} else "掌握", "description": x.get("description") or ""}
            if not any(old.get("name", "").casefold() == item["name"].casefold() for old in skills):
                skills.append(item)
        service.replace_skills(request.user_id, UserSkillsReplace(skills=skills))
    if isinstance(profile.get("projects"), list) and profile["projects"]:
        projects = [{"name": x.get("name"), "role": x.get("role") or "项目成员", "description": x.get("description"), "tech_stack": x.get("tech_stack") if isinstance(x.get("tech_stack"), list) else []} for x in current.get("projects", [])]
        for x in profile["projects"]:
            if isinstance(x, dict) and x.get("name") and x.get("description") and not any(old["name"].casefold() == x["name"].casefold() for old in projects):
                projects.append({"name": x["name"], "role": x.get("role") or "项目成员", "description": x["description"], "tech_stack": x.get("tech_stack") if isinstance(x.get("tech_stack"), list) else []})
        service.replace_projects(request.user_id, UserProjectsReplace(projects=projects))
    if isinstance(profile.get("competitions"), list) and profile["competitions"]:
        competitions = [{"name": x.get("name"), "level": x.get("level") or "校级", "award": x.get("award") or "参与奖", "description": x.get("description") or ""} for x in current.get("competitions", [])]
        for x in profile["competitions"]:
            if isinstance(x, dict) and x.get("name") and not any(old["name"].casefold() == x["name"].casefold() for old in competitions):
                competitions.append({"name": x["name"], "level": x.get("level") or "校级", "award": x.get("award") or "参与奖", "description": x.get("description") or ""})
        service.replace_competitions(request.user_id, UserCompetitionsReplace(competitions=competitions))
    if isinstance(profile.get("internships"), list) and profile["internships"]:
        internships = [{"company": x.get("company"), "position": x.get("position"), "description": x.get("description") or "", "tech_stack": x.get("tech_stack") if isinstance(x.get("tech_stack"), list) else []} for x in current.get("internships", [])]
        for x in profile["internships"]:
            if isinstance(x, dict) and x.get("company") and x.get("position") and not any(old["company"].casefold() == x["company"].casefold() and old["position"].casefold() == x["position"].casefold() for old in internships):
                internships.append({"company": x["company"], "position": x["position"], "description": x.get("description") or "", "tech_stack": x.get("tech_stack") if isinstance(x.get("tech_stack"), list) else []})
        service.replace_internships(request.user_id, UserInternshipsReplace(internships=internships))
    return success(_user_context(db, request.user_id), message="已同步到就业档案")
