"""
アプリケーションイベントログユーティリティ
PythonロガーとDBのAppEventLogの両方に記録
"""
import json
import logging
from sqlalchemy.orm import Session
from app.models import AppEventLog

logger = logging.getLogger(__name__)


def log_event(
    db: Session,
    *,
    level: str = "INFO",
    source: str,
    event_type: str,
    message: str | None = None,
    meta: dict | None = None,
):
    """
    アプリケーションイベントをログに記録
    
    Args:
        db: データベースセッション
        level: ログレベル (DEBUG, INFO, WARN, ERROR)
        source: イベントの発生元 (scheduler, webhook_comment, etc.)
        event_type: イベントタイプ (post_posted, comment_received, etc.)
        message: メッセージ
        meta: 追加メタデータ（辞書形式）
    """
    level_upper = level.upper()
    meta_str = json.dumps(meta, ensure_ascii=False) if meta else None
    
    # DBに保存
    log = AppEventLog(
        level=level_upper,
        source=source,
        event_type=event_type,
        message=message,
        meta=meta_str,
    )
    db.add(log)
    db.commit()
    
    # Pythonロガーにも出力
    log_msg = f"[{source}] {event_type} - {message or ''}"
    if meta_str:
        log_msg += f" meta={meta_str}"
    
    if level_upper == "ERROR":
        logger.error(log_msg)
    elif level_upper == "WARN":
        logger.warning(log_msg)
    elif level_upper == "DEBUG":
        logger.debug(log_msg)
    else:
        logger.info(log_msg)


