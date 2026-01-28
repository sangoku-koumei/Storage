"""
予約投稿のスケジューラー
APSchedulerを使用して定期的に投稿を処理
"""
from datetime import datetime, timezone
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import ScheduledPost, IGAccount
from app.meta_client import create_media_for_post, publish_media, MetaAPIError
from app.utils_logging import log_event
from app.enums import PostStatus

scheduler = BackgroundScheduler()


def process_due_posts():
    """期限が来た予約投稿を処理"""
    db: Session = SessionLocal()
    try:
        now = datetime.now(timezone.utc)
        posts = (
            db.query(ScheduledPost)
            .filter(
                ScheduledPost.status == PostStatus.PENDING,
                ScheduledPost.scheduled_at <= now,
            )
            .all()
        )
        
        if not posts:
            return
        
        log_event(
            db,
            level="INFO",
            source="scheduler",
            event_type="post_batch_start",
            message=f"Processing {len(posts)} due posts",
            meta={"count": len(posts)},
        )
        
        for post in posts:
            account: IGAccount = (
                db.query(IGAccount)
                .filter(IGAccount.id == post.ig_account_id)
                .first()
            )
            
            if not account:
                post.status = PostStatus.FAILED
                post.error_message = "IGAccount not found"
                db.add(post)
                db.commit()
                log_event(
                    db,
                    level="ERROR",
                    source="scheduler",
                    event_type="post_failed",
                    message="Account not found for post",
                    meta={"post_id": post.id},
                )
                continue
            
            if account.is_active != 1:
                post.status = PostStatus.FAILED
                post.error_message = "IGAccount is inactive"
                db.add(post)
                db.commit()
                log_event(
                    db,
                    level="WARN",
                    source="scheduler",
                    event_type="post_failed",
                    message="Account is inactive",
                    meta={"post_id": post.id, "account_id": account.id},
                )
                continue
            
            try:
                post.status = PostStatus.PROCESSING
                db.add(post)
                db.commit()
                
                log_event(
                    db,
                    level="INFO",
                    source="scheduler",
                    event_type="post_processing",
                    message="Starting post processing",
                    meta={
                        "post_id": post.id,
                        "post_type": post.post_type,
                        "media_type": post.media_type,
                    },
                )
                
                # 1. メディアオブジェクト作成
                creation_id = create_media_for_post(
                    ig_user_id=account.ig_user_id,
                    post_type=post.post_type,
                    media_type=post.media_type,
                    image_url=post.image_url,
                    video_url=post.video_url,
                    caption=post.caption or "",
                    access_token=account.access_token,
                )
                
                post.remote_media_id = creation_id
                db.add(post)
                db.commit()
                
                log_event(
                    db,
                    level="INFO",
                    source="scheduler",
                    event_type="media_created",
                    message="Media object created",
                    meta={"post_id": post.id, "creation_id": creation_id},
                )
                
                # 2. メディア公開
                media_id = publish_media(
                    ig_user_id=account.ig_user_id,
                    creation_id=creation_id,
                    access_token=account.access_token,
                )
                
                post.status = PostStatus.POSTED
                post.updated_at = datetime.utcnow()
                db.add(post)
                db.commit()
                
                log_event(
                    db,
                    level="INFO",
                    source="scheduler",
                    event_type="post_posted",
                    message="Post published successfully",
                    meta={"post_id": post.id, "media_id": media_id},
                )
                
            except MetaAPIError as e:
                post.status = PostStatus.FAILED
                post.error_message = str(e)
                db.add(post)
                db.commit()
                log_event(
                    db,
                    level="ERROR",
                    source="scheduler",
                    event_type="post_failed",
                    message=f"Meta API error: {e}",
                    meta={"post_id": post.id, "error": str(e)},
                )
                
            except Exception as e:
                post.status = PostStatus.FAILED
                post.error_message = f"Unexpected error: {e}"
                db.add(post)
                db.commit()
                log_event(
                    db,
                    level="ERROR",
                    source="scheduler",
                    event_type="post_failed",
                    message=f"Unexpected error: {e}",
                    meta={"post_id": post.id, "error": str(e)},
                )
    
    finally:
        db.close()


def start_scheduler():
    """スケジューラーを開始"""
    scheduler.add_job(
        process_due_posts,
        "interval",
        seconds=60,  # 1分ごとにチェック
        id="process_due_posts",
        replace_existing=True,
    )
    scheduler.start()
    print("Scheduler started")


def stop_scheduler():
    """スケジューラーを停止"""
    scheduler.shutdown()
    print("Scheduler stopped")


