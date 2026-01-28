"""
スケジューラーのテスト
"""
from datetime import datetime, timedelta, timezone
from app.db import SessionLocal
from app.models import IGAccount, ScheduledPost
from app.enums import PostStatus, PostType, MediaType
from app.scheduler import process_due_posts


def test_process_due_posts_posts_pending_items(monkeypatch):
    """期限が来た投稿を処理するテスト"""
    db = SessionLocal()
    try:
        # テストアカウント作成
        account = IGAccount(
            name="test_account",
            ig_user_id="123",
            access_token="dummy_token",
        )
        db.add(account)
        db.commit()
        db.refresh(account)
        
        # 期限が来た投稿を作成
        now = datetime.now(timezone.utc)
        post = ScheduledPost(
            ig_account_id=account.id,
            post_type=PostType.FEED,
            media_type=MediaType.IMAGE,
            image_url="https://example.com/image.jpg",
            caption="test",
            scheduled_at=now - timedelta(minutes=1),
            status=PostStatus.PENDING,
        )
        db.add(post)
        db.commit()
        db.refresh(post)
        
        # Meta API呼び出しをモック
        def dummy_create_media_for_post(**kwargs):
            return "dummy_creation_id"
        
        def dummy_publish_media(**kwargs):
            return "dummy_media_id"
        
        monkeypatch.setattr(
            "app.scheduler.create_media_for_post",
            dummy_create_media_for_post,
        )
        monkeypatch.setattr(
            "app.scheduler.publish_media",
            dummy_publish_media,
        )
        
        # スケジューラー実行
        process_due_posts()
        
        # 投稿がPOSTEDになっているか確認
        db.refresh(post)
        assert post.status == PostStatus.POSTED
        
    finally:
        db.close()


