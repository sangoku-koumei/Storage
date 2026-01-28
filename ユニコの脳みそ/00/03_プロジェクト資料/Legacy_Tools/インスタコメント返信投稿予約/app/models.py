"""
データベースモデル定義
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, DateTime, Text, ForeignKey, JSON, Boolean
)
from sqlalchemy.orm import relationship
from app.db import Base


class IGAccount(Base):
    """Instagramアカウント"""
    __tablename__ = "ig_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    ig_user_id = Column(String, unique=True, nullable=False, index=True)
    access_token = Column(Text, nullable=False)  # TODO: 暗号化推奨
    refresh_token = Column(Text, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Integer, default=1)  # 1=有効, 0=無効
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ScheduledPost(Base):
    """予約投稿"""
    __tablename__ = "scheduled_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    ig_account_id = Column(Integer, ForeignKey("ig_accounts.id"), nullable=False)
    post_type = Column(String, default="feed")  # feed, reel, story
    media_type = Column(String, default="image")  # image, video
    image_url = Column(Text, nullable=True)
    video_url = Column(Text, nullable=True)
    caption = Column(Text, nullable=True)
    scheduled_at = Column(DateTime, nullable=False, index=True)
    status = Column(String, default="pending")  # pending, processing, posted, failed, canceled, paused
    remote_media_id = Column(String, nullable=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    account = relationship("IGAccount", backref="scheduled_posts")


class MessageTemplate(Base):
    """メッセージテンプレート"""
    __tablename__ = "message_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    ig_account_id = Column(Integer, ForeignKey("ig_accounts.id"), nullable=False)
    kind = Column(String, nullable=False, default="comment")  # comment, dm, caption
    name = Column(String, nullable=False)
    body = Column(Text, nullable=False)
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    account = relationship("IGAccount", backref="message_templates")
    comment_rules = relationship("CommentReplyRule", back_populates="template")
    dm_rules = relationship("DMReplyRule", back_populates="template")


class CommentReplyRule(Base):
    """コメント自動返信ルール"""
    __tablename__ = "comment_reply_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    ig_account_id = Column(Integer, ForeignKey("ig_accounts.id"), nullable=False)
    keyword = Column(String, nullable=False)
    reply_text = Column(Text, nullable=False)
    is_active = Column(Integer, default=1)
    template_id = Column(Integer, ForeignKey("message_templates.id"), nullable=True)
    priority = Column(Integer, default=100)  # 小さいほど優先度高
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    account = relationship("IGAccount", backref="comment_rules")
    template = relationship("MessageTemplate", back_populates="comment_rules")


class CommentLog(Base):
    """コメントログ"""
    __tablename__ = "comment_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    ig_account_id = Column(Integer, ForeignKey("ig_accounts.id"), nullable=False)
    instagram_comment_id = Column(String, unique=True, nullable=False, index=True)
    instagram_user_id = Column(String, index=True)
    media_id = Column(String, nullable=True)
    text = Column(Text, nullable=True)
    replied = Column(Integer, default=0)  # 0=未返信, 1=返信済み
    used_rule_id = Column(Integer, ForeignKey("comment_reply_rules.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    replied_at = Column(DateTime, nullable=True)
    
    account = relationship("IGAccount", backref="comment_logs")
    rule = relationship("CommentReplyRule", backref="comment_logs")


class DMReplyRule(Base):
    """DM自動返信ルール"""
    __tablename__ = "dm_reply_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    ig_account_id = Column(Integer, ForeignKey("ig_accounts.id"), nullable=False)
    keyword = Column(String, nullable=False)
    reply_text = Column(Text, nullable=False)
    is_active = Column(Integer, default=1)
    template_id = Column(Integer, ForeignKey("message_templates.id"), nullable=True)
    priority = Column(Integer, default=100)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    account = relationship("IGAccount", backref="dm_rules")
    template = relationship("MessageTemplate", back_populates="dm_rules")


class DMLog(Base):
    """DMログ"""
    __tablename__ = "dm_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    ig_account_id = Column(Integer, ForeignKey("ig_accounts.id"), nullable=False)
    instagram_user_id = Column(String, index=True)
    thread_id = Column(String, nullable=True)
    message_id = Column(String, index=True)
    direction = Column(String, default="in")  # in, out
    text = Column(Text, nullable=True)
    replied = Column(Integer, default=0)
    used_rule_id = Column(Integer, ForeignKey("dm_reply_rules.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    replied_at = Column(DateTime, nullable=True)
    
    account = relationship("IGAccount", backref="dm_logs")
    rule = relationship("DMReplyRule", backref="dm_logs")


class UserConversation(Base):
    """ユーザー会話状態（24時間ルール管理用）"""
    __tablename__ = "user_conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    ig_account_id = Column(Integer, ForeignKey("ig_accounts.id"), nullable=False)
    instagram_user_id = Column(String, index=True, nullable=False)
    thread_id = Column(String, nullable=True)
    last_user_message_at = Column(DateTime, nullable=True)
    last_bot_message_at = Column(DateTime, nullable=True)
    is_open = Column(Integer, default=1)  # 1=24時間以内, 0=24時間経過
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    account = relationship("IGAccount", backref="conversations")


class AppEventLog(Base):
    """アプリケーションイベントログ"""
    __tablename__ = "app_event_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String, default="INFO")  # DEBUG, INFO, WARN, ERROR
    source = Column(String, nullable=False)  # scheduler, webhook_comment, webhook_dm, etc.
    event_type = Column(String, nullable=False)  # post_posted, comment_received, etc.
    message = Column(Text, nullable=True)
    meta = Column(Text, nullable=True)  # JSON文字列
    created_at = Column(DateTime, default=datetime.utcnow, index=True)


