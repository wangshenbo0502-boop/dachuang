"""AI 求职助手：开放咨询、档案访谈、简历生成与档案同步。"""

import json
from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.ai.deepseek_client import DeepSeekClient
from app.auth.dependencies import get_current_user, require_owner
from app.models.user import User
from app.database.session import get_db
from app.schemas.chat import (
    ChatConversationRequest,
    ChatProfileRequest,
    ChatResumeRequest,
    ChatTurnRequest,
    ChatTurnResponse,
)
from app.schemas.user import UserProfileResponse
from app.schemas.resume import ResumeOptimizationRequest, ResumeOptimizationResponse
from app.services.resume_service import ResumeService
from app.services.user_service import UserService
from app.utils.response import success

router = APIRouter(dependencies=[Depends(get_current_user)], prefix="/api/chat", tags=["AI对话式求职助手"])


def _user_context(db: Session, user_id: int) -> dict[str, Any]:
    return UserService(db).get_user_context(user_id).model_dump(mode="json")


def _conversation_text(request: ChatTurnRequest) -> str:
    return "\n".join(f"{m.role}: {m.content}" for m in request.messages)


def _conversation_messages(db: Session, request: ChatConversationRequest) -> list[dict[str, str]]:
    context = _user_context(db, request.user_id)
    system = f"""模式：开放式求职咨询。
你是大学生就业服务平台中的 AI 求职助手。请直接、自然地回答用户问题，结合求职、学习、简历和职业发展给出实用建议。
这是用户当前就业档案，仅用于理解上下文：{context}
用户本次咨询关注的目标岗位：{request.target_job or '尚未指定'}。
不要声称已修改档案、简历、分析或成长规划；不要编造用户经历，区分“已在档案中”和“本次对话提到”。回答结尾可以给出一个最合适的下一步，但不要一次塞入太多选项。"""
    messages = [{"role": "system", "content": system}]
    messages.extend({"role": item.role, "content": item.content} for item in request.messages[-40:])
    return messages


def _suggested_action(request: ChatConversationRequest) -> str | None:
    text = "\n".join(item.content for item in request.messages[-12:] if item.role == "user")
    action_keywords = {
        "profile": ("档案", "经历", "技能", "个人信息", "补充资料"),
        "resume": ("简历", "自我介绍", "项目描述", "投递"),
        "analysis": ("竞争力", "能力画像", "优势", "短板", "分析"),
        "growth": ("学习计划", "成长", "提升", "路线", "学习什么"),
        "jobs": ("岗位", "职位", "工作", "匹配", "招聘"),
    }
    scores = {key: sum(text.count(keyword) for keyword in keywords) for key, keywords in action_keywords.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] else None


def _sse_event(event: str, payload: dict[str, Any]) -> str:
    return f"event: {event}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


@router.post("/conversation")
def chat_conversation(request: ChatConversationRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    """通用自由对话，不执行简历采集问卷。"""
    require_owner(request.user_id, current_user)
    reply = DeepSeekClient.instance().chat(_conversation_messages(db, request), temperature=0.65, max_tokens=1800)
    return success({"reply": reply.strip(), "suggested_action": _suggested_action(request)}, message="回复生成成功")


@router.post("/conversation-stream")
def chat_conversation_stream(request: ChatConversationRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> StreamingResponse:
    """Stream an open-ended consultation response as SSE."""
    require_owner(request.user_id, current_user)
    messages = _conversation_messages(db, request)
    action = _suggested_action(request)

    def generate():
        yield _sse_event("start", {"type": "start", "message": "AI 正在思考"})
        try:
            for chunk in DeepSeekClient.instance().chat_stream(messages, temperature=0.65, max_tokens=1800):
                yield _sse_event("chunk", {"type": "chunk", "content": chunk})
            yield _sse_event("complete", {"type": "complete", "result": {"suggested_action": action}})
        except Exception as exc:
            yield _sse_event("error", {"type": "error", "message": f"AI 服务异常：{exc}"})

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.post("/turn")
def chat_turn(request: ChatTurnRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    """根据聊天上下文提出下一问，并返回结构化信息草稿。"""
    require_owner(request.user_id, current_user)
    context = _user_context(db, request.user_id)
    question_number = sum(1 for m in request.messages if m.role == "user")
    system = """你是一个专业、友好的大学生求职教练。通过自然对话逐步了解学生并帮助生成真实、有竞争力的简历。
严禁编造经历、数字或技能。每轮只问一个最关键的问题，问题要具体，优先追问项目中的目标、个人职责、技术方案和可验证成果。
请严格返回JSON：{"reply":"给用户的一句话和一个问题","finished":false,"extracted":{"target_job":"","bio":"","skills":[],"projects":[],"competitions":[],"internships":[]},"missing":[]}。
extracted只填写本轮对话中有明确依据的信息；技能格式为{name,proficiency,description}，项目格式为{name,role,description,tech_stack}。
当用户明确表示要结束访谈、生成或保存时finished=true；否则允许继续补充。"""
    user = f"目标岗位：{request.target_job or '尚未确定'}\n已有档案：{context}\n对话：\n{_conversation_text(request)}"
    result = DeepSeekClient.instance().chat_json(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.45,
        max_tokens=1600,
    )
    response = ChatTurnResponse(
        reply=str(result.get("reply", "请介绍一段最能代表你的项目经历。")),
        question_number=question_number,
        finished=bool(result.get("finished", False)),
        extracted=result.get("extracted", {}),
        missing=result.get("missing", []),
    )
    return success(response.model_dump(mode="json"), message="对话回复生成成功")


@router.post("/profile-turn")
def profile_turn(request: ChatTurnRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    """通过不限轮数的轻量访谈补全就业档案，结果只作为待审核草稿返回。"""
    require_owner(request.user_id, current_user)
    context = _user_context(db, request.user_id)
    question_number = sum(1 for m in request.messages if m.role == "user")
    system = """你是大学生就业服务平台的档案助手。你的任务是通过自然对话，帮用户补全和优化就业档案，用户可以回答任意轮数。
每轮只问一个简单、具体的问题，优先了解姓名、学校专业年级、求职方向、技能、项目、竞赛、实习和个人优势；已有明确资料不要重复追问。
用户不需要填写表格，可以用很短的话回答。严禁编造经历、数字、技能或联系方式，只提取用户明确说过的事实。
请严格返回JSON：{"reply":"自然的一句话加一个问题","finished":false,"extracted":{"name":"","school":"","major":"","grade":"","bio":"","target_city":"","target_salary":"","skills":[],"projects":[],"competitions":[],"internships":[]},"missing":[]}。
技能格式{name,proficiency,description}；项目格式{name,role,description,tech_stack}；竞赛格式{name,level,award,description}；实习格式{company,position,description,tech_stack}。
用户提出更正时，extracted 必须返回相同名称或相同公司岗位的记录，并只填写有明确依据的修正字段。不要自动补“掌握”“项目成员”“校级”“参与奖”等默认事实。
当用户明确表示准备确认或保存时finished=true；否则允许继续补充。回复要让用户知道可以直接说“没有”或“跳过”。"""
    user = f"已有档案：{context}\n对话：\n{_conversation_text(request)}"
    result = DeepSeekClient.instance().chat_json(
        [{"role": "system", "content": system}, {"role": "user", "content": user}],
        temperature=0.4,
        max_tokens=1600,
    )
    response = ChatTurnResponse(
        reply=str(result.get("reply", "先从最想找的工作方向开始说起吧？")),
        question_number=question_number,
        finished=bool(result.get("finished", False)),
        extracted=result.get("extracted", {}),
        missing=result.get("missing", []),
    )
    return success(response.model_dump(mode="json"), message="档案访谈回复生成成功")


@router.post("/generate-resume")
def generate_resume(request: ChatResumeRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    """使用现有档案和对话补充信息，直接生成完整简历优化结果。"""
    require_owner(request.user_id, current_user)
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
def sync_profile(request: ChatProfileRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> dict[str, Any]:
    """Atomically merge only facts the user confirmed in the draft."""
    require_owner(request.user_id, current_user)
    updated, skipped = UserService(db).sync_profile_draft(request.user_id, request.profile)
    profile = UserProfileResponse.model_validate(updated).model_dump(mode="json")
    return success(
        {
            "profile": profile,
            "skipped": skipped,
        },
        message="已同步到就业档案",
    )
