"""
FastAPIメインアプリケーション
"""
import json
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from app.db import Base, engine, get_db
from app.config import settings
from app.logging_config import setup_logging
from app.models import (
    IGAccount, ScheduledPost, CommentReplyRule, CommentLog,
    DMReplyRule, DMLog, UserConversation, MessageTemplate, AppEventLog
)
from app.meta_client import (
    reply_to_comment, send_instagram_dm, MetaAPIError
)
from app.dm_utils import get_or_create_conversation, can_auto_reply
from app.utils_logging import log_event
from app.enums import (
    PostStatus, PostType, MediaType, InboxStatus,
    MessageTemplateKind
)
from app.scheduler import start_scheduler

# ログ設定
setup_logging()

# FastAPIアプリ初期化
app = FastAPI(title="Instagram自動投稿・自動返信ツール")

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番環境では適切に設定
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# デバッグモード用のリクエストログミドルウェア
if settings.DEBUG:
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f"Request: {request.method} {request.url}")
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                body = await request.body()
                logger.debug(f"Request body: {body.decode()[:500]}")
            except:
                pass
        response = await call_next(request)
        logger.debug(f"Response: {response.status_code}")
        return response


# 起動時にDBテーブル作成とスケジューラー開始
@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    start_scheduler()


# ==================== Pydantic Schemas ====================

class IGAccountCreate(BaseModel):
    name: str
    ig_user_id: str
    access_token: str
    refresh_token: Optional[str] = None


class IGAccountRead(BaseModel):
    id: int
    name: str
    ig_user_id: str
    is_active: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ScheduledPostCreate(BaseModel):
    ig_account_id: int
    post_type: str = PostType.FEED
    media_type: str = MediaType.IMAGE
    image_url: Optional[str] = None
    video_url: Optional[str] = None
    caption: Optional[str] = None
    scheduled_at: datetime


class ScheduledPostRead(BaseModel):
    id: int
    ig_account_id: int
    post_type: str
    media_type: str
    image_url: Optional[str]
    video_url: Optional[str]
    caption: Optional[str]
    scheduled_at: datetime
    status: str
    error_message: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class MessageTemplateCreate(BaseModel):
    ig_account_id: int
    kind: str = MessageTemplateKind.COMMENT
    name: str
    body: str


class MessageTemplateRead(BaseModel):
    id: int
    ig_account_id: int
    kind: str
    name: str
    body: str
    is_active: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class CommentReplyRuleCreate(BaseModel):
    ig_account_id: int
    keyword: str
    reply_text: str
    template_id: Optional[int] = None
    priority: int = 100


class CommentReplyRuleRead(BaseModel):
    id: int
    ig_account_id: int
    keyword: str
    reply_text: str
    is_active: int
    template_id: Optional[int]
    priority: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class DMReplyRuleCreate(BaseModel):
    ig_account_id: int
    keyword: str
    reply_text: str
    template_id: Optional[int] = None
    priority: int = 100


class DMReplyRuleRead(BaseModel):
    id: int
    ig_account_id: int
    keyword: str
    reply_text: str
    is_active: int
    template_id: Optional[int]
    priority: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class CommentLogRead(BaseModel):
    id: int
    ig_account_id: int
    instagram_comment_id: str
    instagram_user_id: Optional[str]
    text: Optional[str]
    replied: int
    used_rule_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class DMLogRead(BaseModel):
    id: int
    ig_account_id: int
    instagram_user_id: Optional[str]
    message_id: str
    direction: str
    text: Optional[str]
    replied: int
    used_rule_id: Optional[int]
    created_at: datetime
    
    class Config:
        from_attributes = True


class CommentInboxItem(BaseModel):
    log_id: int
    account_name: str
    instagram_user_id: Optional[str]
    text: Optional[str]
    status: str
    created_at: datetime
    replied_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class DMInboxItem(BaseModel):
    log_id: int
    account_name: str
    instagram_user_id: Optional[str]
    text: Optional[str]
    status: str
    can_auto_reply: bool
    created_at: datetime
    replied_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class AppEventLogRead(BaseModel):
    id: int
    level: str
    source: str
    event_type: str
    message: Optional[str]
    meta: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True


class DashboardSummary(BaseModel):
    total_accounts: int
    active_accounts: int
    pending_posts: int
    today_posts: int
    unhandled_comments: int
    unhandled_dms: int


class CalendarPost(BaseModel):
    id: int
    account_name: str
    post_type: str
    scheduled_at: datetime
    status: str
    
    class Config:
        from_attributes = True


class ReschedulePayload(BaseModel):
    scheduled_at: datetime


class RuleOrderUpdate(BaseModel):
    rule_ids: List[int]


class RuleTestRequest(BaseModel):
    text: str


class RuleTestResult(BaseModel):
    matched: bool
    rule_id: Optional[int]
    rule_keyword: Optional[str]
    reply_text: Optional[str]


# ==================== API Endpoints ====================

# --- アカウント管理 ---
@app.get("/accounts", response_model=List[IGAccountRead])
def list_accounts(db: Session = Depends(get_db)):
    """アカウント一覧取得"""
    return db.query(IGAccount).all()


@app.post("/accounts", response_model=IGAccountRead)
def create_account(account: IGAccountCreate, db: Session = Depends(get_db)):
    """アカウント作成"""
    db_account = IGAccount(**account.dict())
    db.add(db_account)
    db.commit()
    db.refresh(db_account)
    return db_account


@app.get("/accounts/{account_id}", response_model=IGAccountRead)
def get_account(account_id: int, db: Session = Depends(get_db)):
    """アカウント取得"""
    account = db.query(IGAccount).filter(IGAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account


@app.delete("/accounts/{account_id}")
def delete_account(account_id: int, db: Session = Depends(get_db)):
    """アカウント削除"""
    account = db.query(IGAccount).filter(IGAccount.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    db.delete(account)
    db.commit()
    return {"status": "ok"}


# --- 予約投稿管理 ---
@app.post("/posts", response_model=ScheduledPostRead)
def create_post(post: ScheduledPostCreate, db: Session = Depends(get_db)):
    """予約投稿作成"""
    # バリデーション
    if post.post_type == PostType.REEL:
        if not post.video_url:
            raise HTTPException(
                status_code=400,
                detail="video_url is required for reel posts"
            )
    elif post.post_type == PostType.STORY:
        if post.media_type == MediaType.IMAGE and not post.image_url:
            raise HTTPException(
                status_code=400,
                detail="image_url is required for story image"
            )
        elif post.media_type == MediaType.VIDEO and not post.video_url:
            raise HTTPException(
                status_code=400,
                detail="video_url is required for story video"
            )
    elif post.post_type == PostType.FEED:
        if post.media_type == MediaType.IMAGE and not post.image_url:
            raise HTTPException(
                status_code=400,
                detail="image_url is required for feed image"
            )
        elif post.media_type == MediaType.VIDEO and not post.video_url:
            raise HTTPException(
                status_code=400,
                detail="video_url is required for feed video"
            )
    
    db_post = ScheduledPost(**post.dict(), status=PostStatus.PENDING)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


@app.get("/posts", response_model=List[ScheduledPostRead])
def list_posts(
    account_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """予約投稿一覧取得"""
    query = db.query(ScheduledPost)
    if account_id:
        query = query.filter(ScheduledPost.ig_account_id == account_id)
    if status:
        query = query.filter(ScheduledPost.status == status)
    return query.order_by(ScheduledPost.scheduled_at.desc()).all()


@app.get("/posts/{post_id}", response_model=ScheduledPostRead)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """予約投稿取得"""
    post = db.query(ScheduledPost).filter(ScheduledPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post


@app.delete("/posts/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    """予約投稿削除"""
    post = db.query(ScheduledPost).filter(ScheduledPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.status == PostStatus.POSTED:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete already posted item"
        )
    post.status = PostStatus.CANCELED
    db.add(post)
    db.commit()
    return {"status": "ok"}


# --- カレンダー表示 ---
@app.get("/calendar/posts", response_model=List[CalendarPost])
def get_calendar_posts(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    account_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """カレンダー表示用の投稿一覧"""
    query = db.query(ScheduledPost, IGAccount.name).join(
        IGAccount, ScheduledPost.ig_account_id == IGAccount.id
    )
    
    if account_id:
        query = query.filter(ScheduledPost.ig_account_id == account_id)
    if start_date:
        query = query.filter(ScheduledPost.scheduled_at >= start_date)
    if end_date:
        query = query.filter(ScheduledPost.scheduled_at <= end_date)
    
    results = query.order_by(ScheduledPost.scheduled_at.asc()).all()
    
    return [
        CalendarPost(
            id=post.id,
            account_name=name,
            post_type=post.post_type,
            scheduled_at=post.scheduled_at,
            status=post.status,
        )
        for post, name in results
    ]


@app.patch("/calendar/posts/{post_id}/reschedule")
def reschedule_post(
    post_id: int,
    payload: ReschedulePayload,
    db: Session = Depends(get_db),
):
    """投稿のスケジュール変更"""
    post = db.query(ScheduledPost).filter(ScheduledPost.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.status == PostStatus.POSTED:
        raise HTTPException(
            status_code=400,
            detail="Cannot reschedule already posted item"
        )
    
    post.scheduled_at = payload.scheduled_at
    db.add(post)
    db.commit()
    return {"status": "ok"}


# --- コメント自動返信ルール ---
@app.get("/comment-rules", response_model=List[CommentReplyRuleRead])
def list_comment_rules(
    account_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """コメント返信ルール一覧"""
    query = db.query(CommentReplyRule)
    if account_id:
        query = query.filter(CommentReplyRule.ig_account_id == account_id)
    return query.order_by(CommentReplyRule.priority.asc()).all()


@app.post("/comment-rules", response_model=CommentReplyRuleRead)
def create_comment_rule(
    rule: CommentReplyRuleCreate,
    db: Session = Depends(get_db),
):
    """コメント返信ルール作成"""
    db_rule = CommentReplyRule(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


@app.post("/comment-rules/reorder")
def reorder_comment_rules(
    payload: RuleOrderUpdate,
    db: Session = Depends(get_db),
):
    """コメント返信ルールの優先度を更新"""
    for priority, rule_id in enumerate(payload.rule_ids, start=1):
        rule = db.query(CommentReplyRule).filter(
            CommentReplyRule.id == rule_id
        ).first()
        if rule:
            rule.priority = priority
            db.add(rule)
    db.commit()
    return {"status": "ok"}


@app.post("/comment-rules/test", response_model=RuleTestResult)
def test_comment_rule(
    account_id: int,
    request: RuleTestRequest,
    db: Session = Depends(get_db),
):
    """コメント返信ルールのテスト"""
    rules = (
        db.query(CommentReplyRule)
        .filter(
            CommentReplyRule.ig_account_id == account_id,
            CommentReplyRule.is_active == 1,
        )
        .order_by(CommentReplyRule.priority.asc())
        .all()
    )
    
    matched_rule = None
    lower_text = request.text.lower()
    for rule in rules:
        if rule.keyword.lower() in lower_text:
            matched_rule = rule
            break
    
    if matched_rule:
        reply_text = matched_rule.reply_text
        if matched_rule.template and matched_rule.template.is_active == 1:
            reply_text = matched_rule.template.body
        
        return RuleTestResult(
            matched=True,
            rule_id=matched_rule.id,
            rule_keyword=matched_rule.keyword,
            reply_text=reply_text,
        )
    else:
        return RuleTestResult(
            matched=False,
            rule_id=None,
            rule_keyword=None,
            reply_text=None,
        )


# --- DM自動返信ルール ---
@app.get("/dm-rules", response_model=List[DMReplyRuleRead])
def list_dm_rules(
    account_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    """DM返信ルール一覧"""
    query = db.query(DMReplyRule)
    if account_id:
        query = query.filter(DMReplyRule.ig_account_id == account_id)
    return query.order_by(DMReplyRule.priority.asc()).all()


@app.post("/dm-rules", response_model=DMReplyRuleRead)
def create_dm_rule(
    rule: DMReplyRuleCreate,
    db: Session = Depends(get_db),
):
    """DM返信ルール作成"""
    db_rule = DMReplyRule(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


@app.post("/dm-rules/reorder")
def reorder_dm_rules(
    payload: RuleOrderUpdate,
    db: Session = Depends(get_db),
):
    """DM返信ルールの優先度を更新"""
    for priority, rule_id in enumerate(payload.rule_ids, start=1):
        rule = db.query(DMReplyRule).filter(DMReplyRule.id == rule_id).first()
        if rule:
            rule.priority = priority
            db.add(rule)
    db.commit()
    return {"status": "ok"}


@app.post("/dm-rules/test", response_model=RuleTestResult)
def test_dm_rule(
    account_id: int,
    request: RuleTestRequest,
    db: Session = Depends(get_db),
):
    """DM返信ルールのテスト"""
    rules = (
        db.query(DMReplyRule)
        .filter(
            DMReplyRule.ig_account_id == account_id,
            DMReplyRule.is_active == 1,
        )
        .order_by(DMReplyRule.priority.asc())
        .all()
    )
    
    matched_rule = None
    lower_text = request.text.lower()
    for rule in rules:
        if rule.keyword.lower() in lower_text:
            matched_rule = rule
            break
    
    if matched_rule:
        reply_text = matched_rule.reply_text
        if matched_rule.template and matched_rule.template.is_active == 1:
            reply_text = matched_rule.template.body
        
        return RuleTestResult(
            matched=True,
            rule_id=matched_rule.id,
            rule_keyword=matched_rule.keyword,
            reply_text=reply_text,
        )
    else:
        return RuleTestResult(
            matched=False,
            rule_id=None,
            rule_keyword=None,
            reply_text=None,
        )


# --- メッセージテンプレート ---
@app.get("/templates", response_model=List[MessageTemplateRead])
def list_templates(
    account_id: Optional[int] = None,
    kind: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """テンプレート一覧"""
    query = db.query(MessageTemplate)
    if account_id:
        query = query.filter(MessageTemplate.ig_account_id == account_id)
    if kind:
        query = query.filter(MessageTemplate.kind == kind)
    return query.order_by(MessageTemplate.created_at.desc()).all()


@app.post("/templates", response_model=MessageTemplateRead)
def create_template(
    template: MessageTemplateCreate,
    db: Session = Depends(get_db),
):
    """テンプレート作成"""
    db_template = MessageTemplate(**template.dict())
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


@app.get("/templates/{template_id}", response_model=MessageTemplateRead)
def get_template(template_id: int, db: Session = Depends(get_db)):
    """テンプレート取得"""
    template = db.query(MessageTemplate).filter(
        MessageTemplate.id == template_id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@app.delete("/templates/{template_id}")
def delete_template(template_id: int, db: Session = Depends(get_db)):
    """テンプレート削除"""
    template = db.query(MessageTemplate).filter(
        MessageTemplate.id == template_id
    ).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    db.delete(template)
    db.commit()
    return {"status": "ok"}


# --- コメントログ ---
@app.get("/comment-logs", response_model=List[CommentLogRead])
def list_comment_logs(
    account_id: Optional[int] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """コメントログ一覧"""
    query = db.query(CommentLog)
    if account_id:
        query = query.filter(CommentLog.ig_account_id == account_id)
    return query.order_by(CommentLog.created_at.desc()).limit(limit).all()


# --- インボックス（コメント） ---
@app.get("/inbox/comments", response_model=List[CommentInboxItem])
def get_comment_inbox(
    account_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """コメントインボックス取得"""
    query = (
        db.query(CommentLog, IGAccount.name)
        .join(IGAccount, CommentLog.ig_account_id == IGAccount.id)
    )
    
    if account_id:
        query = query.filter(CommentLog.ig_account_id == account_id)
    if status:
        if status == InboxStatus.UNHANDLED:
            query = query.filter(CommentLog.replied == 0)
        elif status == InboxStatus.AUTO_REPLIED:
            query = query.filter(CommentLog.replied == 1)
    
    results = query.order_by(CommentLog.created_at.desc()).limit(100).all()
    
    return [
        CommentInboxItem(
            log_id=log.id,
            account_name=name,
            instagram_user_id=log.instagram_user_id,
            text=log.text,
            status=InboxStatus.AUTO_REPLIED if log.replied == 1 else InboxStatus.UNHANDLED,
            created_at=log.created_at,
            replied_at=log.replied_at,
        )
        for log, name in results
    ]


# --- インボックス（DM） ---
@app.get("/inbox/dms", response_model=List[DMInboxItem])
def get_dm_inbox(
    account_id: Optional[int] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """DMインボックス取得"""
    query = (
        db.query(DMLog, IGAccount.name)
        .join(IGAccount, DMLog.ig_account_id == IGAccount.id)
        .filter(DMLog.direction == "in")
    )
    
    if account_id:
        query = query.filter(DMLog.ig_account_id == account_id)
    if status:
        if status == InboxStatus.UNHANDLED:
            query = query.filter(DMLog.replied == 0)
        elif status == InboxStatus.AUTO_REPLIED:
            query = query.filter(DMLog.replied == 1)
    
    results = query.order_by(DMLog.created_at.desc()).limit(100).all()
    
    inbox_items = []
    for log, name in results:
        can_reply = can_auto_reply(db, log.ig_account_id, log.instagram_user_id or "")
        inbox_items.append(
            DMInboxItem(
                log_id=log.id,
                account_name=name,
                instagram_user_id=log.instagram_user_id,
                text=log.text,
                status=InboxStatus.AUTO_REPLIED if log.replied == 1 else InboxStatus.UNHANDLED,
                can_auto_reply=can_reply,
                created_at=log.created_at,
                replied_at=log.replied_at,
            )
        )
    
    return inbox_items


# --- ダッシュボード ---
@app.get("/dashboard/summary", response_model=DashboardSummary)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """ダッシュボードサマリー取得"""
    now = datetime.now(timezone.utc)
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    
    total_accounts = db.query(IGAccount).count()
    active_accounts = db.query(IGAccount).filter(IGAccount.is_active == 1).count()
    pending_posts = db.query(ScheduledPost).filter(
        ScheduledPost.status == PostStatus.PENDING
    ).count()
    today_posts = db.query(ScheduledPost).filter(
        ScheduledPost.scheduled_at >= today_start,
        ScheduledPost.status == PostStatus.PENDING,
    ).count()
    unhandled_comments = db.query(CommentLog).filter(
        CommentLog.replied == 0
    ).count()
    unhandled_dms = db.query(DMLog).filter(
        DMLog.direction == "in",
        DMLog.replied == 0,
    ).count()
    
    return DashboardSummary(
        total_accounts=total_accounts,
        active_accounts=active_accounts,
        pending_posts=pending_posts,
        today_posts=today_posts,
        unhandled_comments=unhandled_comments,
        unhandled_dms=unhandled_dms,
    )


# --- アプリケーションイベントログ ---
@app.get("/logs/app-events", response_model=List[AppEventLogRead])
def list_app_event_logs(
    level: Optional[str] = None,
    source: Optional[str] = None,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """アプリケーションイベントログ一覧"""
    query = db.query(AppEventLog)
    if level:
        query = query.filter(AppEventLog.level == level.upper())
    if source:
        query = query.filter(AppEventLog.source == source)
    return query.order_by(AppEventLog.created_at.desc()).limit(limit).all()


# --- Webhook: Instagram コメント ---
@app.get("/webhook/instagram")
def verify_webhook(request: Request):
    """Webhook検証（MetaからのGETリクエスト）"""
    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")
    
    if mode == "subscribe" and token == settings.META_WEBHOOK_VERIFY_TOKEN:
        return int(challenge)
    raise HTTPException(status_code=403, detail="Forbidden")


@app.post("/webhook/instagram")
async def handle_instagram_comments(request: Request):
    """InstagramコメントWebhook処理"""
    payload = await request.json()
    db: Session = SessionLocal()
    
    try:
        entries = payload.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                field = change.get("field")
                
                if field != "comments":
                    continue
                
                # Webhookペイロードの構造は実際のMeta APIに合わせて調整が必要
                # 以下は一般的な構造の例
                comment_id = value.get("id")
                text = value.get("text")
                from_user = value.get("from", {})
                instagram_user_id = from_user.get("id")
                media_id = value.get("media", {}).get("id")
                
                # ig_user_idを取得（アカウント特定用）
                # 実際のWebhookペイロード構造に応じて調整
                ig_user_id = entry.get("id")  # または適切なフィールド
                
                if not comment_id or not ig_user_id:
                    log_event(
                        db,
                        level="WARN",
                        source="webhook_comment",
                        event_type="comment_parse_failed",
                        message="Missing comment_id or ig_user_id in webhook",
                        meta={"payload_snippet": str(payload)[:200]},
                    )
                    continue
                
                account = db.query(IGAccount).filter(
                    IGAccount.ig_user_id == ig_user_id
                ).first()
                
                if not account:
                    log_event(
                        db,
                        level="WARN",
                        source="webhook_comment",
                        event_type="comment_account_not_found",
                        message=f"IGAccount not found for ig_user_id: {ig_user_id}",
                        meta={"comment_id": comment_id},
                    )
                    continue
                
                # 重複チェック
                existing = db.query(CommentLog).filter(
                    CommentLog.instagram_comment_id == comment_id
                ).first()
                
                if existing:
                    log_event(
                        db,
                        level="DEBUG",
                        source="webhook_comment",
                        event_type="comment_duplicate",
                        message="Duplicate comment webhook ignored",
                        meta={"comment_id": comment_id},
                    )
                    continue
                
                # コメントログ保存
                log = CommentLog(
                    ig_account_id=account.id,
                    instagram_comment_id=comment_id,
                    instagram_user_id=instagram_user_id,
                    media_id=media_id,
                    text=text,
                )
                db.add(log)
                db.commit()
                db.refresh(log)
                
                log_event(
                    db,
                    level="INFO",
                    source="webhook_comment",
                    event_type="comment_received",
                    message="Comment received and logged",
                    meta={
                        "comment_log_id": log.id,
                        "comment_id": comment_id,
                        "text_preview": (text or "")[:50],
                    },
                )
                
                # 自動返信ルール適用
                rules = (
                    db.query(CommentReplyRule)
                    .filter(
                        CommentReplyRule.ig_account_id == account.id,
                        CommentReplyRule.is_active == 1,
                    )
                    .order_by(CommentReplyRule.priority.asc())
                    .all()
                )
                
                matched_rule = None
                lower_text = (text or "").lower()
                for rule in rules:
                    if rule.keyword.lower() in lower_text:
                        matched_rule = rule
                        break
                
                if not matched_rule:
                    log_event(
                        db,
                        level="DEBUG",
                        source="webhook_comment",
                        event_type="comment_no_rule_match",
                        message="No comment reply rule matched",
                        meta={"comment_log_id": log.id},
                    )
                    continue
                
                # 返信テキスト決定
                reply_text = matched_rule.reply_text
                if matched_rule.template and matched_rule.template.is_active == 1:
                    reply_text = matched_rule.template.body
                
                # コメント返信
                try:
                    reply_id = reply_to_comment(
                        comment_id=comment_id,
                        message=reply_text,
                        access_token=account.access_token,
                    )
                    
                    now_utc = datetime.now(timezone.utc)
                    log.replied = 1
                    log.used_rule_id = matched_rule.id
                    log.replied_at = now_utc
                    db.add(log)
                    db.commit()
                    
                    log_event(
                        db,
                        level="INFO",
                        source="webhook_comment",
                        event_type="comment_auto_replied",
                        message="Comment auto-replied successfully",
                        meta={
                            "comment_log_id": log.id,
                            "rule_id": matched_rule.id,
                            "reply_id": reply_id,
                        },
                    )
                except Exception as e:
                    log_event(
                        db,
                        level="ERROR",
                        source="webhook_comment",
                        event_type="comment_auto_reply_failed",
                        message=f"Failed to auto-reply to comment: {e}",
                        meta={
                            "comment_log_id": log.id,
                            "error": str(e),
                        },
                    )
                    db.add(log)
                    db.commit()
        
        return {"status": "ok"}
    
    finally:
        db.close()


# --- Webhook: Instagram DM ---
@app.post("/webhook/instagram-messages")
async def handle_instagram_messages(request: Request):
    """Instagram DM Webhook処理"""
    payload = await request.json()
    db: Session = SessionLocal()
    
    try:
        entries = payload.get("entry", [])
        for entry in entries:
            changes = entry.get("changes", [])
            for change in changes:
                value = change.get("value", {})
                field = change.get("field")
                
                if field not in ("messages", "instagram_messages"):
                    continue
                
                # Webhookペイロードの構造は実際のMeta APIに合わせて調整が必要
                to_list = value.get("to", [])
                ig_user_id = to_list[0].get("id") if to_list else None
                from_user = value.get("from", {})
                sender_id = from_user.get("id")
                message_obj = value.get("message", {})
                text = message_obj.get("text")
                message_id = message_obj.get("mid")
                
                if not ig_user_id or not sender_id:
                    log_event(
                        db,
                        level="WARN",
                        source="webhook_dm",
                        event_type="dm_parse_failed",
                        message="Missing ig_user_id or sender_id in DM webhook",
                        meta={"payload_snippet": str(payload)[:200]},
                    )
                    continue
                
                account = db.query(IGAccount).filter(
                    IGAccount.ig_user_id == ig_user_id
                ).first()
                
                if not account:
                    log_event(
                        db,
                        level="WARN",
                        source="webhook_dm",
                        event_type="dm_account_not_found",
                        message=f"IGAccount not found for ig_user_id: {ig_user_id}",
                        meta={"sender_id": sender_id},
                    )
                    continue
                
                # 会話状態更新
                now_utc = datetime.now(timezone.utc)
                conv = get_or_create_conversation(db, account.id, sender_id)
                conv.last_user_message_at = now_utc
                conv.is_open = 1
                db.add(conv)
                db.commit()
                
                log_event(
                    db,
                    level="DEBUG",
                    source="webhook_dm",
                    event_type="conversation_updated",
                    message="User conversation updated",
                    meta={"conv_id": conv.id, "sender_id": sender_id},
                )
                
                # DMログ保存
                log = DMLog(
                    ig_account_id=account.id,
                    instagram_user_id=sender_id,
                    thread_id=None,  # 必要に応じて取得
                    message_id=message_id,
                    direction="in",
                    text=text,
                )
                db.add(log)
                db.commit()
                db.refresh(log)
                
                log_event(
                    db,
                    level="INFO",
                    source="webhook_dm",
                    event_type="dm_received",
                    message="DM received and logged",
                    meta={
                        "dm_log_id": log.id,
                        "sender_id": sender_id,
                        "text_preview": (text or "")[:50],
                    },
                )
                
                # 自動返信ルール適用
                rules = (
                    db.query(DMReplyRule)
                    .filter(
                        DMReplyRule.ig_account_id == account.id,
                        DMReplyRule.is_active == 1,
                    )
                    .order_by(DMReplyRule.priority.asc())
                    .all()
                )
                
                matched_rule = None
                lower_text = (text or "").lower()
                for rule in rules:
                    if rule.keyword.lower() in lower_text:
                        matched_rule = rule
                        break
                
                if not matched_rule:
                    log_event(
                        db,
                        level="DEBUG",
                        source="webhook_dm",
                        event_type="dm_no_rule_match",
                        message="No DM reply rule matched",
                        meta={"dm_log_id": log.id},
                    )
                    continue
                
                # 24時間ルールチェック
                if not can_auto_reply(db, account.id, sender_id):
                    log_event(
                        db,
                        level="WARN",
                        source="webhook_dm",
                        event_type="dm_auto_reply_blocked_24h",
                        message="DM auto-reply blocked by 24-hour rule",
                        meta={"dm_log_id": log.id, "sender_id": sender_id},
                    )
                    continue
                
                # 返信テキスト決定
                message_body = matched_rule.reply_text
                if matched_rule.template and matched_rule.template.is_active == 1:
                    message_body = matched_rule.template.body
                
                # DM送信
                try:
                    msg_id = send_instagram_dm(
                        ig_user_id=account.ig_user_id,
                        recipient_id=sender_id,
                        message=message_body,
                        access_token=account.access_token,
                    )
                    
                    now_utc = datetime.now(timezone.utc)
                    log.replied = 1
                    log.used_rule_id = matched_rule.id
                    log.replied_at = now_utc
                    db.add(log)
                    
                    conv.last_bot_message_at = now_utc
                    db.add(conv)
                    db.commit()
                    
                    log_event(
                        db,
                        level="INFO",
                        source="webhook_dm",
                        event_type="dm_auto_replied",
                        message="DM auto-replied successfully",
                        meta={
                            "dm_log_id": log.id,
                            "sender_id": sender_id,
                            "rule_id": matched_rule.id,
                            "out_msg_id": msg_id,
                        },
                    )
                except Exception as e:
                    log_event(
                        db,
                        level="ERROR",
                        source="webhook_dm",
                        event_type="dm_auto_reply_failed",
                        message=f"Failed to auto-reply to DM: {e}",
                        meta={
                            "dm_log_id": log.id,
                            "sender_id": sender_id,
                            "error": str(e),
                        },
                    )
                    db.add(log)
                    db.commit()
        
        return {"status": "ok"}
    
    finally:
        db.close()


