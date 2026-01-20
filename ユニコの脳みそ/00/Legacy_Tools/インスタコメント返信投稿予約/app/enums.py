"""
定数定義
ステータスやタイプを文字列リテラルではなく定数で管理
"""


class PostStatus:
    """投稿ステータス"""
    PENDING = "pending"
    PROCESSING = "processing"
    POSTED = "posted"
    FAILED = "failed"
    CANCELED = "canceled"
    PAUSED = "paused"


class PostType:
    """投稿種別"""
    FEED = "feed"
    REEL = "reel"
    STORY = "story"


class MediaType:
    """メディアタイプ"""
    IMAGE = "image"
    VIDEO = "video"


class InboxStatus:
    """インボックスステータス"""
    UNHANDLED = "unhandled"
    AUTO_REPLIED = "auto_replied"
    NEED_REVIEW = "need_review"
    DONE = "done"


class MessageTemplateKind:
    """メッセージテンプレート種別"""
    COMMENT = "comment"
    DM = "dm"
    CAPTION = "caption"


class LogLevel:
    """ログレベル"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"


