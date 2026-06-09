from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.chat import Chat
from app.models.message import Message
from app.schemas.chat import (
    ChatResponse,
    ChatDetailResponse,
    MessageResponse,
    SendMessageRequest,
    SendMessageResponse,
    FeedbackRequest,
)
from app.services.rag_pipeline import answer_question
from app.services.analytics_service import track_event

router = APIRouter(prefix="/api/chats", tags=["chats"])


@router.post("/", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
def create_chat(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatResponse:
    chat = Chat(user_id=current_user.id)
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return ChatResponse.model_validate(chat)


@router.get("/", response_model=list[ChatResponse])
def list_chats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[ChatResponse]:
    chats = (
        db.query(Chat)
        .filter(Chat.user_id == current_user.id)
        .order_by(Chat.updated_at.desc())
        .all()
    )
    return [ChatResponse.model_validate(c) for c in chats]


@router.get("/{chat_id}", response_model=ChatDetailResponse)
def get_chat(
    chat_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ChatDetailResponse:
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chat not found")
    return ChatDetailResponse.model_validate(chat)


@router.post("/{chat_id}/messages", response_model=SendMessageResponse)
def send_message(
    chat_id: str,
    body: SendMessageRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> SendMessageResponse:
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chat not found")

    user_msg = Message(chat_id=chat_id, role="user", content=body.content)
    db.add(user_msg)
    db.commit()
    db.refresh(user_msg)

    history = (
        db.query(Message)
        .filter(Message.chat_id == chat_id)
        .order_by(Message.created_at.desc())
        .limit(4)
        .all()
    )
    history.reverse()
    chat_history = [{"role": m.role, "content": m.content} for m in history[:-1]]

    result = answer_question(body.content, current_user.department, chat_history)

    assistant_msg = Message(
        chat_id=chat_id,
        role="assistant",
        content=result["answer"],
    )
    db.add(assistant_msg)

    if chat.title == "New Chat":
        chat.title = body.content[:50] + ("..." if len(body.content) > 50 else "")

    db.commit()
    db.refresh(assistant_msg)

    track_event(db, "question_asked", user_id=current_user.id, metadata={"question": body.content})

    return SendMessageResponse(
        message=MessageResponse.model_validate(user_msg),
        answer=MessageResponse.model_validate(assistant_msg),
    )


@router.delete("/{chat_id}")
def delete_chat(
    chat_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    chat = db.query(Chat).filter(Chat.id == chat_id, Chat.user_id == current_user.id).first()
    if not chat:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Chat not found")
    db.delete(chat)
    db.commit()
    return {"status": "deleted"}


@router.post("/messages/{message_id}/feedback")
def submit_feedback(
    message_id: str,
    body: FeedbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    msg = (
        db.query(Message)
        .join(Chat)
        .filter(Message.id == message_id, Chat.user_id == current_user.id)
        .first()
    )
    if not msg:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Message not found")
    msg.feedback = body.feedback
    db.commit()
    return {"status": "ok"}
