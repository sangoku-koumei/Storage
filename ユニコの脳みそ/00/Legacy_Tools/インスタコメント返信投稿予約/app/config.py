"""
アプリケーション設定管理
環境変数から設定を読み込む
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """アプリケーション設定"""
    
    # Meta API設定
    META_APP_ID: str
    META_APP_SECRET: str
    META_REDIRECT_URI: str = "https://your-app.com/oauth/callback"
    GRAPH_API_BASE_URL: str = "https://graph.facebook.com/v21.0"
    META_WEBHOOK_VERIFY_TOKEN: str = "your-verify-token"
    
    # データベース設定
    DATABASE_URL: str = "sqlite:///./insta_tool.db"
    
    # ログ設定
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    LOG_TO_FILE: bool = True
    LOG_FILE_PATH: str = "./logs/app.log"
    
    # Google Sheets連携（オプション）
    GOOGLE_SHEETS_SERVICE_ACCOUNT_JSON: str | None = None
    GOOGLE_SHEETS_SPREADSHEET_ID: str | None = None
    GOOGLE_SHEETS_LOG_SHEET_NAME: str = "ログ"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()


