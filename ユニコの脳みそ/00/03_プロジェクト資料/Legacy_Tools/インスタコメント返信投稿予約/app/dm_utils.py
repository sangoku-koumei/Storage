"""
DM関連ユーティリティ
24時間ルールの判定など
"""
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from app.models import UserConversation

# 24時間ルールの時間窓
AUTO_REPLY_WINDOW_HOURS = 24


def get_or_create_conversation(
    db: Session,
    ig_account_id: int,
    instagram_user_id: str,
) -> UserConversation:
    """
    ユーザー会話を取得または作成
    
    Args:
        db: データベースセッション
        ig_account_id: InstagramアカウントID
        instagram_user_id: InstagramユーザーID
        
    Returns:
        UserConversationオブジェクト
    """
    conv = (
        db.query(UserConversation)
        .filter(
            UserConversation.ig_account_id == ig_account_id,
            UserConversation.instagram_user_id == instagram_user_id,
        )
        .first()
    )
    
    if not conv:
        conv = UserConversation(
            ig_account_id=ig_account_id,
            instagram_user_id=instagram_user_id,
            is_open=1,
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)
    
    return conv


def can_auto_reply(
    db: Session,
    ig_account_id: int,
    instagram_user_id: str,
) -> bool:
    """
    24時間ルールに基づいて自動返信可能か判定
    
    Args:
        db: データベースセッション
        ig_account_id: InstagramアカウントID
        instagram_user_id: InstagramユーザーID
        
    Returns:
        自動返信可能な場合True
    """
    conv = (
        db.query(UserConversation)
        .filter(
            UserConversation.ig_account_id == ig_account_id,
            UserConversation.instagram_user_id == instagram_user_id,
        )
        .first()
    )
    
    if not conv or not conv.last_user_message_at:
        return False
    
    now_utc = datetime.now(timezone.utc)
    diff = now_utc - conv.last_user_message_at
    
    return diff <= timedelta(hours=AUTO_REPLY_WINDOW_HOURS)


